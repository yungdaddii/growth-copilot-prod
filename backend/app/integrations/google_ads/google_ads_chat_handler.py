"""
Google Ads Chat Handler

Handles Google Ads integration within the chat WebSocket flow.
Processes OAuth connections and data queries through natural language.
"""

from typing import Dict, Any, Optional
import structlog

from app.integrations import is_integration_enabled
from .google_ads_intent_detector import GoogleAdsIntentDetector
from .google_ads_oauth_handler import GoogleAdsOAuthHandler
from .google_ads_nlp_responder import GoogleAdsNLPResponder

logger = structlog.get_logger()


class GoogleAdsChatHandler:
    """Handle Google Ads interactions in chat."""
    
    def __init__(self):
        """Initialize handler components."""
        self.enabled = is_integration_enabled("google_ads")
        if self.enabled:
            self.oauth_handler = GoogleAdsOAuthHandler()
        else:
            self.oauth_handler = None
            logger.info("Google Ads integration disabled via feature flag")
    
    async def process_message(
        self,
        message: str,
        session_id: str,
        domain: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Process a message for Google Ads intent.
        
        Args:
            message: User's message
            session_id: User's session ID
            domain: Current domain being analyzed (if any)
            
        Returns:
            Response dict if Google Ads intent detected, None otherwise
        """
        if not self.enabled:
            return None
        
        # Detect Google Ads intent
        intent = GoogleAdsIntentDetector.detect_intent(message)
        if not intent:
            return None
        
        logger.info(
            "Google Ads intent detected",
            intent_type=intent["type"],
            session_id=session_id
        )
        
        # Handle different intent types
        if intent["type"] == "google_ads_connect":
            return await self._handle_connect(session_id)
        
        elif intent["type"] == "google_ads_disconnect":
            return await self._handle_disconnect(session_id)
        
        elif intent["type"] == "google_ads_query":
            return await self._handle_query(
                message,
                session_id,
                intent.get("query_type", "general"),
                domain
            )
        
        return None
    
    async def _handle_connect(self, session_id: str) -> Dict[str, Any]:
        """Handle Google Ads connection request."""
        try:
            # Generate OAuth URL
            auth_data = await self.oauth_handler.generate_auth_url(session_id)
            
            return {
                "content": (
                    "I'll help you connect your Google Ads account for deeper insights.\n\n"
                    f"**[🔗 Click here to connect Google Ads]({auth_data['auth_url']})**\n\n"
                    "**What I'll be able to analyze:**\n"
                    "• 📊 Campaign performance and ROI\n"
                    "• 💸 Wasted ad spend and optimization opportunities\n"
                    "• 🎯 Keyword performance and quality scores\n"
                    "• 📈 Conversion tracking and attribution\n"
                    "• 🔄 Month-over-month trends\n\n"
                    "*Connection is secure, read-only, and you can disconnect anytime.*"
                ),
                "metadata": {
                    "type": "oauth_prompt",
                    "platform": "google_ads",
                    "auth_url": auth_data["auth_url"],
                    "state": auth_data["state"]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate auth URL: {e}")
            return {
                "content": "I encountered an issue setting up the Google Ads connection. Please try again in a moment.",
                "metadata": {"type": "error", "platform": "google_ads"}
            }
    
    async def _handle_disconnect(self, session_id: str) -> Dict[str, Any]:
        """Handle Google Ads disconnection request."""
        try:
            success = await self.oauth_handler.disconnect(session_id)
            
            if success:
                return {
                    "content": (
                        "✅ I've disconnected your Google Ads account and removed all stored credentials.\n\n"
                        "Your historical insights are preserved, but I won't be able to fetch new Google Ads data "
                        "until you reconnect.\n\n"
                        "You can reconnect anytime by saying \"connect my Google Ads\"."
                    ),
                    "metadata": {
                        "type": "disconnection_success",
                        "platform": "google_ads"
                    }
                }
            else:
                return {
                    "content": "No Google Ads account was connected to disconnect.",
                    "metadata": {
                        "type": "no_connection",
                        "platform": "google_ads"
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to disconnect: {e}")
            return {
                "content": "I encountered an issue disconnecting your Google Ads account. Please try again.",
                "metadata": {"type": "error", "platform": "google_ads"}
            }
    
    async def _handle_query(
        self,
        message: str,
        session_id: str,
        query_type: str,
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle Google Ads data query."""
        try:
            # Initialize NLP responder
            responder = GoogleAdsNLPResponder(session_id)
            
            # Generate response based on query
            response = await responder.respond_to_query(message)
            
            # Check if connection is required
            if response.get("metadata", {}).get("type") == "connection_required":
                # Enhance response with connection prompt
                response["content"] += (
                    "\n\n**[🔗 Connect Google Ads now]** to unlock these insights."
                )
                # Generate auth URL
                auth_data = await self.oauth_handler.generate_auth_url(session_id)
                response["metadata"]["auth_url"] = auth_data["auth_url"]
            
            # If we have a domain context, add cross-analysis
            if domain and response.get("metadata", {}).get("has_data"):
                response["content"] += await self._add_domain_context(domain, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to handle query: {e}")
            return {
                "content": (
                    "I encountered an issue accessing your Google Ads data. "
                    "This might be a temporary issue. Please try again or reconnect your account."
                ),
                "metadata": {"type": "error", "platform": "google_ads"}
            }
    
    async def _add_domain_context(
        self,
        domain: str,
        ads_response: Dict[str, Any]
    ) -> str:
        """Add domain-specific context to Google Ads insights."""
        try:
            # Extract key metrics from ads response
            metadata = ads_response.get("metadata", {})
            
            if metadata.get("category") == "wasted_spend":
                return (
                    f"\n\n**Connection to {domain}:**\n"
                    f"The ${metadata.get('total_waste', 0):.2f} wasted could be redirected to "
                    f"improving your {domain} landing page experience, potentially increasing "
                    f"overall conversion rate by 15-20%."
                )
            
            elif metadata.get("category") == "performance":
                metrics = metadata.get("metrics", {})
                if metrics.get("conversion_rate", 0) < 2:
                    return (
                        f"\n\n**{domain} Impact:**\n"
                        f"Your ads conversion rate ({metrics.get('conversion_rate', 0):.1f}%) "
                        f"is lower than your site average. This suggests a mismatch between "
                        f"ad messaging and landing page content."
                    )
            
            return ""
            
        except Exception as e:
            logger.error(f"Failed to add domain context: {e}")
            return ""
    
    async def check_auto_prompt(
        self,
        domain: str,
        analysis: Any,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check if we should auto-prompt for Google Ads connection.
        
        Args:
            domain: Analyzed domain
            analysis: Website analysis results
            session_id: User's session ID
            
        Returns:
            Auto-prompt response or None
        """
        if not self.enabled:
            return None
        
        try:
            # Check if user already has Google Ads connected
            credentials = await self.oauth_handler.get_valid_credentials(session_id)
            if credentials:
                return None  # Already connected
            
            # Check if analysis suggests they're running ads
            if not analysis or not hasattr(analysis, 'results'):
                return None
            
            results = analysis.results if hasattr(analysis, 'results') else analysis
            
            # Look for signs of Google Ads
            signs_of_ads = False
            
            # Check for Google Ads conversion tracking
            if "technical" in results:
                tech = results["technical"]
                if any("google" in str(s).lower() and "ads" in str(s).lower() 
                      for s in tech.get("scripts", [])):
                    signs_of_ads = True
            
            # Check for UTM parameters or gclid in URLs
            if "seo" in results:
                seo = results["seo"]
                if "gclid" in str(seo).lower() or "utm_source=google" in str(seo).lower():
                    signs_of_ads = True
            
            if signs_of_ads:
                return {
                    "content": (
                        f"I noticed {domain} appears to be running Google Ads campaigns. "
                        f"Would you like to connect your Google Ads account for deeper insights?\n\n"
                        f"I could show you:\n"
                        f"• Which keywords are wasting money\n"
                        f"• Your actual cost per conversion\n"
                        f"• Campaign-specific optimization opportunities\n\n"
                        f"**[🔗 Connect Google Ads]** (takes 30 seconds)"
                    ),
                    "metadata": {
                        "type": "auto_prompt",
                        "platform": "google_ads",
                        "trigger": "ads_detected"
                    }
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to check auto-prompt: {e}")
            return None