"""
Google Ads Integration Module

Provides OAuth connection and data fetching for Google Ads accounts.
All files are clearly named to indicate their specific purpose.
"""

from app.integrations import is_integration_enabled


def is_google_ads_enabled() -> bool:
    """Check if Google Ads integration is enabled."""
    return is_integration_enabled("google_ads")


# Only import if enabled to avoid loading unnecessary dependencies
if is_google_ads_enabled():
    from .google_ads_oauth_handler import GoogleAdsOAuthHandler
    from .google_ads_api_client import GoogleAdsAPIClient
    from .google_ads_nlp_responder import GoogleAdsNLPResponder
    
    __all__ = [
        "GoogleAdsOAuthHandler",
        "GoogleAdsAPIClient", 
        "GoogleAdsNLPResponder"
    ]