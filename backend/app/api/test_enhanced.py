"""
Test endpoint for Enhanced NLP
This allows testing without affecting production
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import structlog
import uuid
from typing import Optional
from app.core.safe_enhanced_nlp import SafeEnhancedNLPProcessor
from app.core.analyzer import DomainAnalyzer
from app.database import get_db
from app.models import Conversation

logger = structlog.get_logger()
router = APIRouter()


class TestRequest(BaseModel):
    domain: str
    use_enhanced: bool = True


class TestResponse(BaseModel):
    success: bool
    enhanced_used: bool
    response: str
    metadata: dict
    error: Optional[str] = None


@router.post("/test-enhanced-nlp")
async def test_enhanced_nlp(request: TestRequest) -> TestResponse:
    """
    Test endpoint for enhanced NLP
    This doesn't affect production WebSocket
    """
    try:
        logger.info(f"Testing enhanced NLP for {request.domain}")
        
        # Initialize safe NLP processor
        nlp = SafeEnhancedNLPProcessor()
        
        # Run analysis
        async for db in get_db():
            # Create a test conversation first
            test_conversation = Conversation(
                id=str(uuid.uuid4()),
                share_slug=f"test-{uuid.uuid4().hex[:8]}"
            )
            db.add(test_conversation)
            await db.commit()
            
            analyzer = DomainAnalyzer(db)
            
            # Analyze domain with test conversation ID
            analysis = await analyzer.analyze(
                conversation_id=test_conversation.id,
                domain=request.domain
            )
            
            # Generate response
            response_data = await nlp.generate_analysis_response(
                request.domain,
                analysis,
                f"analyze {request.domain}"
            )
            
            return TestResponse(
                success=True,
                enhanced_used=nlp.is_enhanced_available,
                response=response_data.get("content", ""),
                metadata=response_data.get("metadata", {}),
                error=None
            )
            
    except Exception as e:
        logger.error(f"Test endpoint error: {e}", exc_info=True)
        return TestResponse(
            success=False,
            enhanced_used=False,
            response="",
            metadata={},
            error=str(e)
        )


@router.get("/test-enhanced-status")
async def test_enhanced_status():
    """Check if enhanced NLP is available"""
    try:
        nlp = SafeEnhancedNLPProcessor()
        
        return {
            "enhanced_available": nlp.is_enhanced_available,
            "has_context": nlp.context is not None,
            "has_enhanced_nlp": nlp.enhanced_nlp is not None,
            "has_standard_nlp": nlp.standard_nlp is not None
        }
    except Exception as e:
        return {
            "error": str(e),
            "enhanced_available": False
        }