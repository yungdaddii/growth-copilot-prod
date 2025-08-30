"""
Enhanced WebSocket endpoint with context-aware NLP
This is a modified version that can be swapped in when ready
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import json
import asyncio
import structlog
from typing import Dict, Set
from uuid import UUID, uuid4
import os

from app.database import get_db
from app.schemas.message import WebSocketMessage, MessagePayload, AnalysisUpdatePayload
from app.schemas.conversation import MessageCreate
from app.models.conversation import Conversation, Message, MessageRole, MessageType
from app.models.analysis import Analysis
from app.core.analyzer import DomainAnalyzer
from app.core.nlp import NLPProcessor
from app.core.enhanced_nlp import EnhancedNLPProcessor
from app.core.conversation_context import ConversationContext
from app.core.conversation_handler import ConversationHandler
from app.core.ai_conversation import AIConversationEngine
from app.utils.cache import get_redis
from app.services.context_chat import ContextAwareChat
from app.utils.analytics import Analytics, FeatureFlags

logger = structlog.get_logger()
router = APIRouter()

# Feature flag for enhanced NLP
ENABLE_ENHANCED_NLP = os.getenv("ENABLE_ENHANCED_NLP", "false").lower() == "true"

# Existing ConnectionManager class stays the same
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        try:
            await websocket.accept()
            self.active_connections[client_id] = websocket
            logger.info("WebSocket connected", client_id=client_id)
            Analytics.track_websocket("connected", client_id)
        except Exception as e:
            logger.error(f"Failed to accept WebSocket connection: {e}", client_id=client_id)
            Analytics.track_websocket("connection_failed", client_id, {"error": str(e)})
            raise
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info("WebSocket disconnected", client_id=client_id)
            Analytics.track_websocket("disconnected", client_id)
    
    async def send_message(self, client_id: str, message: WebSocketMessage):
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_json(message.model_dump(mode="json"))
            except Exception as e:
                logger.error("Failed to send message", client_id=client_id, error=str(e))


manager = ConnectionManager()


@router.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(uuid4())
    session_id = client_id  # Use client_id as session_id for context persistence
    
    logger.info(f"New WebSocket connection attempt: {client_id}")
    await manager.connect(websocket, client_id)
    
    # Initialize conversation and NLP processor
    conversation = None
    conversation_context = None
    nlp = None
    
    # Choose NLP processor based on feature flag
    try:
        if ENABLE_ENHANCED_NLP:
            # Initialize context manager
            redis_client = await get_redis()
            conversation_context = ConversationContext(session_id, redis_client)
            nlp = EnhancedNLPProcessor(context=conversation_context)
            logger.info(f"Using enhanced NLP with context for {client_id}")
        else:
            # Fallback to original NLP
            nlp = NLPProcessor()
            logger.info(f"Using standard NLP for {client_id}")
    except Exception as e:
        logger.warning(f"Failed to initialize enhanced NLP, falling back: {e}")
        nlp = NLPProcessor()
    
    context_chat = None  # Will initialize with DB session
    
    try:
        # Send connection confirmation
        await manager.send_message(
            client_id,
            WebSocketMessage(
                type="connection",
                payload={
                    "status": "connected", 
                    "client_id": client_id,
                    "enhanced_nlp": ENABLE_ENHANCED_NLP
                }
            )
        )
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            logger.info(f"Received message from {client_id}: {data[:100]}...")  # Log first 100 chars
            message_data = json.loads(data)
            
            # Track message received
            Analytics.track_websocket("message_received", client_id, {
                "message_type": message_data.get("type", "unknown"),
                "enhanced_nlp": ENABLE_ENHANCED_NLP
            })
            
            # Handle different message types
            if message_data.get("type") == "chat":
                payload = MessagePayload(**message_data.get("payload", {}))
                
                # Track message in context if available
                if conversation_context:
                    conversation_context.add_message("user", payload.content)
                
                # Create or get conversation
                if not conversation:
                    from app.database import get_db_context
                    async with get_db_context() as db:
                        conversation = Conversation(share_slug=generate_share_slug())
                        db.add(conversation)
                        await db.commit()
                        await db.refresh(conversation)
                
                # Save user message to database
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
                
                # Detect intent
                intent = await nlp.detect_intent(payload.content)
                logger.info(f"Detected intent: {intent}")
                
                # Track intent in context
                if conversation_context:
                    conversation_context.add_message("user", payload.content, intent.get("type"))
                
                # Process based on intent
                if intent["type"] == "analyze_domain":
                    domain = intent["domain"]
                    
                    # Update context with domain
                    if conversation_context:
                        conversation_context.context["current_domain"] = domain
                        conversation_context.save()
                    
                    # Track analysis start
                    Analytics.track_analysis(
                        domain=domain,
                        conversation_id=str(conversation.id),
                        status="started"
                    )
                    
                    # Run analysis
                    from app.database import get_db_context
                    async with get_db_context() as db:
                        analyzer = DomainAnalyzer(db)
                        
                        # Progress callback
                        async def send_progress(message: str, progress: int):
                            await manager.send_message(
                                client_id,
                                WebSocketMessage(
                                    type="analysis_update",
                                    payload=AnalysisUpdatePayload(
                                        message=message,
                                        progress=progress
                                    )
                                )
                            )
                        
                        # Run analysis
                        analysis = await analyzer.analyze(
                            domain=domain,
                            progress_callback=send_progress
                        )
                        
                        # Link analysis to conversation
                        analysis.conversation_id = conversation.id
                        db.add(analysis)
                        await db.commit()
                        await db.refresh(analysis)
                    
                    # Generate response using NLP
                    response_data = await nlp.generate_analysis_response(
                        domain=domain,
                        analysis=analysis,
                        context=intent.get("context")
                    )
                    
                    # Track analysis completion
                    Analytics.track_analysis(
                        domain=domain,
                        conversation_id=str(conversation.id),
                        status="completed",
                        duration=(analysis.completed_at - analysis.created_at).total_seconds() if analysis.completed_at else 0,
                        issues_found=len(analysis.issues) if analysis.issues else 0
                    )
                    
                elif intent["type"] == "follow_up":
                    # Handle follow-up questions with context
                    response_data = await nlp.generate_follow_up_response(
                        question=payload.content,
                        conversation=conversation,
                        context=intent
                    )
                    
                else:
                    # General response
                    response_data = await nlp.generate_response(payload.content)
                
                # Save assistant response
                from app.database import get_db_context
                async with get_db_context() as db:
                    assistant_message = Message(
                        conversation_id=conversation.id,
                        role=MessageRole.ASSISTANT,
                        content=response_data.get("content", ""),
                        message_type=MessageType.TEXT,
                        metadata=response_data.get("metadata")
                    )
                    db.add(assistant_message)
                    await db.commit()
                
                # Track assistant response in context
                if conversation_context:
                    conversation_context.add_message("assistant", response_data.get("content", ""))
                
                # Send response to client
                await manager.send_message(
                    client_id,
                    WebSocketMessage(
                        type="chat",
                        payload={
                            "content": response_data.get("content"),
                            "message_id": str(uuid4()),
                            "conversation_id": str(conversation.id),
                            "metadata": response_data.get("metadata", {})
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
        logger.info(f"WebSocket disconnected: {client_id}")
        manager.disconnect(client_id)
        
        # Clean up context if needed
        if conversation_context:
            conversation_context.save()  # Save final state
    
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}", exc_info=True)
        manager.disconnect(client_id)
        
        # Try to send error message
        try:
            await manager.send_message(
                client_id,
                WebSocketMessage(
                    type="error",
                    payload={"message": "An error occurred processing your request"}
                )
            )
        except:
            pass


def generate_share_slug(length: int = 8) -> str:
    """Generate a random share slug"""
    import string
    import random
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))