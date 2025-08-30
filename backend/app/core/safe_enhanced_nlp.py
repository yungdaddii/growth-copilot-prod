"""
Safe Enhanced NLP Wrapper
This version has extensive error handling and fallback mechanisms
"""

import structlog
from typing import Dict, Any, Optional
from app.core.nlp import NLPProcessor
from app.models.analysis import Analysis

logger = structlog.get_logger()


class SafeEnhancedNLPProcessor:
    """
    Safe wrapper around enhanced NLP that falls back gracefully
    """
    
    def __init__(self):
        self.standard_nlp = NLPProcessor()
        self.enhanced_nlp = None
        self.context = None
        self.is_enhanced_available = False
        
        # Try to initialize enhanced components
        try:
            from app.core.conversation_context import ConversationContext
            from app.core.enhanced_nlp import EnhancedNLPProcessor
            
            # This will work even without Redis
            self.context = ConversationContext("default", redis_client=None)
            self.enhanced_nlp = EnhancedNLPProcessor(context=self.context)
            self.is_enhanced_available = True
            logger.info("Enhanced NLP initialized successfully")
        except Exception as e:
            logger.warning(f"Enhanced NLP not available, using standard: {e}")
            self.is_enhanced_available = False
    
    async def detect_intent(self, text: str) -> Dict[str, Any]:
        """Detect intent with fallback"""
        try:
            if self.is_enhanced_available and self.enhanced_nlp:
                return await self.enhanced_nlp.detect_intent(text)
        except Exception as e:
            logger.error(f"Enhanced intent detection failed: {e}")
        
        # Fallback to standard
        return await self.standard_nlp.detect_intent(text)
    
    async def generate_analysis_response(
        self,
        domain: str,
        analysis: Analysis,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate response with automatic fallback"""
        
        # First, check if we have valid analysis data
        if not analysis or not analysis.results:
            logger.error(f"Invalid analysis data for {domain}")
            return {
                "content": f"I encountered an issue analyzing {domain}. The analysis may be incomplete. Please try again or check if the domain is accessible.",
                "metadata": {"error": True}
            }
        
        # Try enhanced NLP first if available
        if self.is_enhanced_available and self.enhanced_nlp:
            try:
                logger.info(f"Attempting enhanced NLP response for {domain}")
                
                # Store analysis in context if available
                if self.context and hasattr(analysis, 'results'):
                    self.context.set_current_analysis(domain, analysis.results)
                
                response = await self.enhanced_nlp.generate_analysis_response(
                    domain, analysis, context
                )
                
                # Validate response
                if response and response.get("content") and len(response["content"]) > 50:
                    logger.info("Enhanced NLP response generated successfully")
                    return response
                else:
                    logger.warning("Enhanced response too short or invalid")
                    
            except Exception as e:
                logger.error(f"Enhanced NLP failed: {e}", exc_info=True)
        
        # Fallback to standard NLP
        logger.info(f"Using standard NLP for {domain}")
        try:
            response = await self.standard_nlp.generate_analysis_response(
                domain, analysis, context
            )
            
            # Ensure we have a valid response
            if not response or not response.get("content"):
                raise ValueError("Empty response from standard NLP")
                
            return response
            
        except Exception as e:
            logger.error(f"Standard NLP also failed: {e}", exc_info=True)
            
            # Last resort: Generate a basic response from the data
            return self._generate_emergency_response(domain, analysis)
    
    def _generate_emergency_response(self, domain: str, analysis: Analysis) -> Dict[str, Any]:
        """Generate a basic response when all NLP fails"""
        try:
            results = analysis.results if hasattr(analysis, 'results') else {}
            
            # Extract basic metrics
            perf_score = results.get("performance", {}).get("score", "N/A")
            conv_score = getattr(analysis, 'conversion_score', "N/A")
            seo_score = getattr(analysis, 'seo_score', "N/A")
            
            # Build basic response
            content_parts = [
                f"Analysis complete for {domain}.",
                f"\nKey Metrics:",
                f"• Performance Score: {perf_score}/100",
                f"• Conversion Score: {conv_score}/100", 
                f"• SEO Score: {seo_score}/100"
            ]
            
            # Add top issues if available
            if "recommendations" in results and results["recommendations"]:
                content_parts.append("\n\nTop Issues Found:")
                for i, rec in enumerate(results["recommendations"][:3], 1):
                    issue = rec.get("issue", "Issue")
                    content_parts.append(f"{i}. {issue}")
            
            return {
                "content": "\n".join(content_parts),
                "metadata": {"fallback": True, "type": "emergency_response"}
            }
            
        except Exception as e:
            logger.error(f"Emergency response generation failed: {e}")
            return {
                "content": f"Analysis for {domain} completed but I'm having trouble formatting the results. Please try again.",
                "metadata": {"error": True}
            }
    
    async def generate_follow_up_response(
        self,
        question: str,
        conversation: Any,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate follow-up with fallback"""
        
        # Try enhanced first
        if self.is_enhanced_available and self.enhanced_nlp:
            try:
                return await self.enhanced_nlp.generate_follow_up_response(
                    question, conversation, context
                )
            except Exception as e:
                logger.error(f"Enhanced follow-up failed: {e}")
        
        # Fallback to standard
        return await self.standard_nlp.generate_follow_up_response(
            question, conversation, context
        )
    
    async def generate_response(self, text: str) -> Dict[str, Any]:
        """Generate general response with fallback"""
        
        # Try enhanced first
        if self.is_enhanced_available and self.enhanced_nlp:
            try:
                return await self.enhanced_nlp.generate_response(text)
            except Exception as e:
                logger.error(f"Enhanced general response failed: {e}")
        
        # Fallback to standard
        return await self.standard_nlp.generate_response(text)