"""
Integration modules for external services.
Each integration is self-contained with clear naming.
"""

from app.utils.feature_flags import FeatureFlags


def is_integration_enabled(integration_name: str) -> bool:
    """Check if a specific integration is enabled via feature flags."""
    flag_map = {
        "google_ads": "google_ads_integration",
        "salesforce": "salesforce_integration",
        "hubspot": "hubspot_integration",
        "meta_ads": "meta_ads_integration",
        "linkedin_ads": "linkedin_ads_integration"
    }
    
    flag_name = flag_map.get(integration_name)
    if not flag_name:
        return False
    
    return FeatureFlags.is_enabled(flag_name)