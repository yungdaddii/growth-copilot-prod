from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import json
import asyncio
import structlog
from typing import Dict, Set, Optional
from uuid import UUID, uuid4

from app.database import get_db
from app.schemas.message import WebSocketMessage, MessagePayload, AnalysisUpdatePayload
from app.schemas.conversation import MessageCreate
from app.models.conversation import Conversation, Message, MessageRole, MessageType
from app.models.analysis import Analysis

# Import User conditionally to avoid circular imports
try:
    from app.models.user import User
    USER_MODEL_AVAILABLE = True
except ImportError:
    User = None
    USER_MODEL_AVAILABLE = False
from app.core.analyzer import DomainAnalyzer
from app.core.safe_enhanced_nlp import SafeEnhancedNLPProcessor
from app.core.conversation_handler import ConversationHandler
from app.core.ai_conversation import AIConversationEngine
from app.utils.cache import get_redis
from app.services.context_chat import ContextAwareChat
from app.utils.analytics import Analytics, FeatureFlags

logger = structlog.get_logger()
router = APIRouter()

# Active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        try:
            await websocket.accept()
            self.active_connections[client_id] = websocket
            logger.info("WebSocket connected", client_id=client_id)
            # Track WebSocket connection
            Analytics.track_websocket("connected", client_id)
        except Exception as e:
            logger.error(f"Failed to accept WebSocket connection: {e}", client_id=client_id)
            Analytics.track_websocket("connection_failed", client_id, {"error": str(e)})
            raise
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info("WebSocket disconnected", client_id=client_id)
            # Track WebSocket disconnection
            Analytics.track_websocket("disconnected", client_id)
    
    async def send_message(self, client_id: str, message: WebSocketMessage):
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_json(message.model_dump(mode="json"))
            except Exception as e:
                logger.error("Failed to send message", client_id=client_id, error=str(e))
    
    async def broadcast(self, message: WebSocketMessage, exclude: Set[str] = None):
        exclude = exclude or set()
        for client_id, websocket in self.active_connections.items():
            if client_id not in exclude:
                try:
                    await websocket.send_json(message.model_dump(mode="json"))
                except Exception as e:
                    logger.error("Broadcast failed", client_id=client_id, error=str(e))


manager = ConnectionManager()


@router.websocket("/chat")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str = Query(None),
    token: str = Query(None)  # Optional Firebase ID token
):
    # Verify user if token provided
    user: Optional[User] = None
    if token and USER_MODEL_AVAILABLE:
        try:
            from firebase_admin import auth as firebase_auth
            from app.database import get_db_context
            
            # Verify Firebase token directly
            decoded_token = firebase_auth.verify_id_token(token)
            firebase_uid = decoded_token.get("uid")
            
            # Get user from database
            async with get_db_context() as db:
                user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
                if user:
                    logger.info(f"WebSocket authenticated for user: {user.email}")
        except Exception as e:
            logger.warning(f"Failed to authenticate WebSocket: {e}")
            # Continue without authentication
    
    # Use provided session_id or generate new one
    if not session_id:
        session_id = str(uuid4())
        logger.warning(f"No session_id provided, generated new one: {session_id}")
    else:
        logger.info(f"WebSocket connected with session_id from client: {session_id}")
    
    client_id = session_id  # Use session_id as client_id for consistency
    import sys
    print(f"DEBUG: WebSocket connection with session_id: {session_id}", file=sys.stderr, flush=True)
    logger.info(f"WebSocket connection established - session_id: {session_id}, client_id: {client_id}")
    await manager.connect(websocket, client_id)
    
    # Initialize conversation and context-aware chat
    conversation = None
    nlp = SafeEnhancedNLPProcessor()
    context_chat = None  # Will initialize with DB session
    
    try:
        logger.info(f"Sending connection confirmation to {client_id}")
        # Send connection confirmation
        await manager.send_message(
            client_id,
            WebSocketMessage(
                type="connection",
                payload={"status": "connected", "client_id": client_id}
            )
        )
        logger.info(f"Connection confirmation sent to {client_id}")
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            logger.info(f"📨 Received WebSocket message from {client_id}: {data[:100]}...")
            
            try:
                message_data = json.loads(data)
                logger.info(f"📦 Parsed message type: {message_data.get('type')}, has payload: {bool(message_data.get('payload'))}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse message as JSON: {e}")
                continue
            
            # Track message received
            Analytics.track_websocket("message_received", client_id, {
                "message_type": message_data.get("type", "unknown")
            })
            
            # Handle different message types
            logger.info(f"🔍 Processing message type: {message_data.get('type')}")
            
            if message_data.get("type") == "chat":
                payload = MessagePayload(**message_data.get("payload", {}))
                logger.info(f"💬 Chat message content: {payload.content[:100]}...")
                
                # Create or get conversation
                if not conversation:
                    from app.database import get_db_context
                    async with get_db_context() as db:
                        conversation = Conversation(
                            share_slug=generate_share_slug(),
                            user_id=user.id if user else None,
                            session_id=session_id
                        )
                        db.add(conversation)
                        await db.commit()
                        await db.refresh(conversation)
                
                # Save user message
                from app.database import get_db_context
                async with get_db_context() as db:
                    user_message = Message(
                        conversation_id=conversation.id,
                        role=MessageRole.USER,
                        content=payload.content,
                        message_type=MessageType.TEXT
                    )
                    db.add(user_message)
                    await db.commit()
                
                # Send typing indicator
                await manager.send_message(
                    client_id,
                    WebSocketMessage(
                        type="typing",
                        payload={"is_typing": True}
                    )
                )
                
                # Initialize AI conversation engine
                ai_engine = AIConversationEngine()
                
                # Try context-aware processing first
                handled_by_context = False
                logger.info(f"🔄 Starting message processing for: {payload.content[:50]}...")
                
                try:
                    logger.info("Attempting context-aware processing...")
                    from app.database import get_db_context
                    async with get_db_context() as db:
                        context_chat = ContextAwareChat(db)
                        context_response = await context_chat.process_message(payload.content, session_id)
                        
                        # If context handler has a specific response, send it
                        if context_response.get('type') in ['competitor_update', 'progress_report', 'opportunities', 'comparison', 'prediction', 'monitoring_added']:
                            await manager.send_message(
                                client_id,
                                WebSocketMessage(
                                    type="chat",
                                    payload={
                                        "content": context_response['content'],
                                        "message_id": str(uuid4()),
                                        "conversation_id": str(conversation.id) if conversation else None,
                                        "metadata": context_response
                                    }
                                )
                            )
                            handled_by_context = True
                except Exception as e:
                    logger.error(f"Context processing error: {e}")
                
                # If not handled by context, do regular processing
                if not handled_by_context:
                    # Check for Google Ads intent first
                    google_ads_response = None
                    logger.info(f"Checking for Google Ads intent - session_id: {session_id}, message: {payload.content[:50]}...")
                    
                    try:
                        from app.integrations import is_integration_enabled
                        # Always check Google Ads (we removed the feature flag check)
                        logger.info("Attempting to import Google Ads modules...")
                        
                        try:
                            from app.integrations.google_ads.google_ads_intent_detector import GoogleAdsIntentDetector
                            logger.info(f"[WebSocket] GoogleAdsIntentDetector imported. Session: {session_id}, Client: {client_id}")
                            
                            google_ads_intent = GoogleAdsIntentDetector.detect_intent(payload.content)
                            logger.info(f"[WebSocket] Google Ads intent result: {google_ads_intent}")
                            
                            if google_ads_intent:
                                logger.info(f"[WebSocket] ✅ Google Ads intent type: {google_ads_intent.get('type')}")
                                logger.info(f"[WebSocket] Using session_id: {session_id} for Google Ads processing")
                                from app.integrations.google_ads.google_ads_chat_handler import GoogleAdsChatHandler
                                handler = GoogleAdsChatHandler()
                                google_ads_response = await handler.process_message(
                                    payload.content,
                                    session_id,
                                    None
                                )
                                logger.info(f"[WebSocket] Google Ads response generated: {bool(google_ads_response)}")
                        except ImportError as ie:
                            logger.error(f"Failed to import Google Ads modules: {ie}")
                            
                    except Exception as e:
                        logger.error(f"Google Ads integration error: {e}", exc_info=True)
                    
                    if google_ads_response:
                        response = google_ads_response
                    else:
                        # Regular intent detection and processing
                        intent = await nlp.detect_intent(payload.content)
                        logger.info(f"Detected intent: {intent}")
                        
                        if intent["type"] == "unsupported_topic":
                            # Handle questions about things we don't analyze
                            if intent.get("topic") == "tracking_attribution":
                                response = {
                                    "content": (
                                        "📈 **Attribution & Tracking Analysis**\n\n"
                                        "I don't analyze internal tracking setups like Google Analytics, UTM parameters, or attribution models. "
                                        "These require access to private analytics data.\n\n"
                                        "**What I CAN help you with:**\n"
                                        "• ⚡ **Performance optimization** - Load times, Core Web Vitals\n"
                                        "• 🎯 **Conversion optimization** - Forms, CTAs, user flow\n"
                                        "• 🏆 **Competitor analysis** - Feature comparisons, gaps\n"
                                        "• 🔍 **SEO improvements** - Meta tags, content gaps\n"
                                        "• 📱 **Mobile experience** - Responsiveness issues\n\n"
                                        "Would you like me to analyze any of these areas instead?"
                                    ),
                                    "metadata": {
                                        "type": "unsupported_query",
                                        "topic": "tracking_attribution"
                                    }
                                }
                            else:
                                response = {
                                    "content": "I can't analyze that specific aspect, but I can help with website optimization, competitor analysis, and conversion improvements. What would you like to explore?",
                                    "metadata": {"type": "unsupported_query"}
                                }
                        
                        elif intent["type"] == "analyze_domain":
                            domain = intent["domain"]
                            logger.info(f"Starting domain analysis for: {domain}")
                            
                            # Track analysis start
                            Analytics.track_analysis(
                                domain=domain,
                                conversation_id=str(conversation.id),
                                status="started"
                            )
                            
                            # Start analysis with streaming updates
                            async def update_callback(status: str, message: str, progress: int = None):
                                # Generate natural language update
                                natural_message = await ai_engine.generate_streaming_update(status, progress)
                                
                                await manager.send_message(
                                    client_id,
                                    WebSocketMessage(
                                        type="analysis_update",
                                        payload=AnalysisUpdatePayload(
                                            status=status,
                                            message=natural_message,
                                            progress=progress
                                        ).model_dump()
                                    )
                                )
                            
                            # Run analysis with new database session
                            from app.database import get_db_context
                            import time
                            analysis_start_time = time.time()
                            
                            try:
                                async with get_db_context() as db:
                                    analyzer = DomainAnalyzer(db)
                                    analysis_result = await analyzer.analyze(
                                        domain=domain,
                                        conversation_id=conversation.id,
                                        update_callback=update_callback,
                                        user_id=user.id if user else None
                                    )
                                
                                # Track successful analysis
                                analysis_duration = time.time() - analysis_start_time
                                # Handle both dict and object types
                                if hasattr(analysis_result, 'issues'):
                                    issues_count = len(analysis_result.issues) if analysis_result.issues else 0
                                elif isinstance(analysis_result, dict):
                                    issues_count = len(analysis_result.get("issues", [])) if analysis_result else 0
                                else:
                                    issues_count = 0
                                
                                Analytics.track_analysis(
                                    domain=domain,
                                    conversation_id=str(conversation.id),
                                    status="completed",
                                    duration=analysis_duration,
                                    issues_found=issues_count
                                )
                            except Exception as e:
                                # Track failed analysis
                                analysis_duration = time.time() - analysis_start_time
                                Analytics.track_analysis(
                                    domain=domain,
                                    conversation_id=str(conversation.id),
                                    status="failed",
                                    duration=analysis_duration,
                                    error=str(e)
                                )
                                raise
                            
                            # Generate conversational response using AI
                            initial_response = await ai_engine.format_initial_response(domain, analysis_result)
                            response = {
                                "content": initial_response,
                                "metadata": {
                                    "type": "analysis_complete",
                                    "domain": domain,
                                    "has_suggestions": True
                                }
                            }
                            
                        elif intent["type"] == "follow_up":
                            # Use AI engine for follow-ups too
                            from app.database import get_db_context
                            async with get_db_context() as db:
                                result = await db.execute(
                                    select(Analysis)
                                    .where(Analysis.conversation_id == conversation.id)
                                    .order_by(Analysis.started_at.desc())
                                    .limit(1)
                                )
                                last_analysis = result.scalar_one_or_none()
                                
                                # Get conversation history
                                messages_result = await db.execute(
                                    select(Message)
                                    .where(Message.conversation_id == conversation.id)
                                    .order_by(Message.created_at.desc())
                                    .limit(10)
                                )
                                messages = messages_result.scalars().all()
                            
                            conversation_history = []
                            for msg in reversed(messages):
                                conversation_history.append({
                                    "role": "user" if msg.role == MessageRole.USER else "assistant",
                                    "content": msg.content
                                })
                            
                            # Use AI engine for natural response
                            response = await ai_engine.generate_response(
                                user_message=payload.content,
                                analysis=last_analysis,
                                conversation_history=conversation_history
                            )
                            
                        else:
                            # Check if we have a previous analysis for context
                            from app.database import get_db_context
                            async with get_db_context() as db:
                                result = await db.execute(
                                    select(Analysis)
                                    .where(Analysis.conversation_id == conversation.id)
                                    .order_by(Analysis.started_at.desc())
                                    .limit(1)
                                )
                                last_analysis = result.scalar_one_or_none()
                                
                                # Get conversation history for context
                                messages_result = await db.execute(
                                    select(Message)
                                    .where(Message.conversation_id == conversation.id)
                                    .order_by(Message.created_at.desc())
                                    .limit(10)
                                )
                                messages = messages_result.scalars().all()
                            
                            # Build conversation history
                            conversation_history = []
                            for msg in reversed(messages):  # Reverse to get chronological order
                                conversation_history.append({
                                    "role": "user" if msg.role == MessageRole.USER else "assistant",
                                    "content": msg.content
                                })
                            
                            # Use AI engine for natural conversation
                            response = await ai_engine.generate_response(
                                user_message=payload.content,
                                analysis=last_analysis,
                                conversation_history=conversation_history
                            )
                    
                    # Save assistant response
                    from app.database import get_db_context
                    async with get_db_context() as db:
                        assistant_message = Message(
                            conversation_id=conversation.id,
                            role=MessageRole.ASSISTANT,
                            content=response["content"],
                            message_type=MessageType.TEXT,
                            metadata=response.get("metadata", {})
                        )
                        db.add(assistant_message)
                        await db.commit()
                    
                    # Send response
                    await manager.send_message(
                        client_id,
                        WebSocketMessage(
                            type="chat",
                            payload={
                                "content": response["content"],
                                "metadata": response.get("metadata", {}),
                                "conversation_id": str(conversation.id),
                                "message_id": str(assistant_message.id)
                            }
                        )
                    )
                    
                    # Stop typing indicator
                    await manager.send_message(
                        client_id,
                        WebSocketMessage(
                            type="typing",
                            payload={"is_typing": False}
                        )
                    )
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        Analytics.track_websocket("disconnected_unexpectedly", client_id)
    except Exception as e:
        logger.error("WebSocket error", client_id=client_id, error=str(e))
        Analytics.track_error(
            error_type="websocket_error",
            error_message=str(e),
            context={"client_id": client_id}
        )
        await manager.send_message(
            client_id,
            WebSocketMessage(
                type="error",
                payload={"message": "An error occurred", "details": str(e)}
            )
        )
        manager.disconnect(client_id)


def generate_share_slug() -> str:
    import secrets
    import string
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(8))