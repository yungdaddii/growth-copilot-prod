from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.analysis import Analysis
from app.core.conversation_handler import ConversationHandler
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.get("/test-conversation/{domain}")
async def test_conversation(domain: str, db: AsyncSession = Depends(get_db)):
    """Test endpoint for conversational features"""
    
    # Get the most recent analysis for this domain
    result = await db.execute(
        select(Analysis)
        .where(Analysis.domain == domain)
        .order_by(Analysis.started_at.desc())
        .limit(1)
    )
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        return {"error": f"No analysis found for {domain}. Please analyze it first."}
    
    # Test various conversational queries
    conv_handler = ConversationHandler()
    
    responses = {}
    
    # Test form query
    responses["forms"] = await conv_handler.handle_follow_up(
        "tell me about forms",
        analysis
    )
    
    # Test pricing query  
    responses["pricing"] = await conv_handler.handle_follow_up(
        "what about pricing?",
        analysis
    )
    
    # Test quick wins
    responses["quick_wins"] = await conv_handler.handle_follow_up(
        "show me quick wins",
        analysis
    )
    
    # Test AI search
    responses["ai_search"] = await conv_handler.handle_follow_up(
        "ai search optimization?",
        analysis
    )
    
    return {
        "domain": domain,
        "analysis_id": str(analysis.id),
        "responses": {
            "forms": responses["forms"]["content"][:200] + "...",
            "pricing": responses["pricing"]["content"][:200] + "...",
            "quick_wins": responses["quick_wins"]["content"][:200] + "...",
            "ai_search": responses["ai_search"]["content"][:200] + "..."
        }
    }