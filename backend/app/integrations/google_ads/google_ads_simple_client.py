"""
Simple Google Ads Client - Temporary Mock Implementation

This bypasses the complex Google Ads SDK to provide demo functionality
while we resolve the GRPC issues.
"""

from typing import Dict, List, Any, Optional
import structlog
import random
from datetime import datetime, timedelta

logger = structlog.get_logger()


class SimpleGoogleAdsClient:
    """Simplified Google Ads client with mock data for testing."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        logger.info(f"Initialized SimpleGoogleAdsClient for session {session_id}")
    
    async def has_credentials(self) -> bool:
        """Check if we have stored credentials."""
        from app.utils.cache import get_redis
        redis = await get_redis()
        if not redis:
            return False
        
        # Check for any OAuth completion marker
        oauth_marker = await redis.get(f"google_ads:oauth_complete:{self.session_id}")
        return oauth_marker is not None
    
    async def mark_oauth_complete(self):
        """Mark that OAuth was completed for this session."""
        from app.utils.cache import get_redis
        redis = await get_redis()
        if redis:
            await redis.setex(
                f"google_ads:oauth_complete:{self.session_id}",
                30 * 24 * 3600,  # 30 days
                "true"
            )
    
    async def get_account_performance(self) -> Dict[str, Any]:
        """Return mock account performance data."""
        if not await self.has_credentials():
            return {}
        
        # Generate realistic mock data
        base_cost = random.randint(5000, 20000)
        conversions = random.randint(50, 200)
        
        return {
            "current_period": {
                "cost": base_cost,
                "clicks": random.randint(1000, 5000),
                "impressions": random.randint(10000, 50000),
                "conversions": conversions,
                "value": conversions * random.randint(50, 150),
                "ctr": round(random.uniform(2.0, 5.0), 2),
                "conversion_rate": round(random.uniform(1.0, 4.0), 2),
                "cpa": round(base_cost / conversions, 2) if conversions > 0 else 0,
                "roas": round(random.uniform(2.0, 5.0), 2)
            },
            "changes": {
                "cost_change": round(random.uniform(-20, 20), 2),
                "conversions_change": round(random.uniform(-30, 30), 2)
            }
        }
    
    async def get_wasted_spend_keywords(self) -> List[Dict[str, Any]]:
        """Return mock wasted spend keywords."""
        if not await self.has_credentials():
            return []
        
        keywords = [
            {"keyword": "buy cheap insurance", "cost": 450.23, "clicks": 234, "impressions": 5678},
            {"keyword": "free consultation lawyer", "cost": 380.45, "clicks": 189, "impressions": 4321},
            {"keyword": "discount software download", "cost": 295.67, "clicks": 147, "impressions": 3456},
            {"keyword": "wholesale prices online", "cost": 189.90, "clicks": 95, "impressions": 2345},
            {"keyword": "best deals near me", "cost": 156.78, "clicks": 78, "impressions": 1890}
        ]
        
        for kw in keywords:
            kw["match_type"] = random.choice(["BROAD", "PHRASE", "EXACT"])
            kw["ad_group"] = f"Ad Group {random.randint(1, 5)}"
            kw["ctr"] = round((kw["clicks"] / kw["impressions"]) * 100, 2)
        
        return keywords
    
    async def get_campaigns(self) -> List[Dict[str, Any]]:
        """Return mock campaign data."""
        if not await self.has_credentials():
            return []
        
        campaigns = []
        for i in range(3):
            cost = random.randint(1000, 5000)
            clicks = random.randint(100, 500)
            conversions = random.randint(5, 50)
            
            campaigns.append({
                "id": f"campaign_{i+1}",
                "name": f"Campaign {i+1} - {'Search' if i == 0 else 'Display' if i == 1 else 'Shopping'}",
                "status": "ENABLED",
                "budget": cost * 1.2,
                "cost": cost,
                "clicks": clicks,
                "impressions": clicks * random.randint(10, 20),
                "conversions": conversions,
                "ctr": round(random.uniform(2.0, 5.0), 2),
                "conversion_rate": round((conversions / clicks) * 100, 2) if clicks > 0 else 0
            })
        
        return campaigns
    
    async def get_top_performing_keywords(self) -> List[Dict[str, Any]]:
        """Return mock top performing keywords."""
        if not await self.has_credentials():
            return []
        
        keywords = []
        terms = [
            "enterprise software solutions",
            "cloud migration services",
            "data analytics platform",
            "cybersecurity consulting",
            "digital transformation agency"
        ]
        
        for term in terms:
            cost = random.randint(100, 500)
            conversions = random.randint(2, 15)
            
            keywords.append({
                "campaign": f"Campaign {random.randint(1, 3)}",
                "ad_group": f"Ad Group {random.randint(1, 5)}",
                "keyword": term,
                "cost": cost,
                "conversions": conversions,
                "value": conversions * random.randint(100, 300),
                "clicks": random.randint(20, 100),
                "cpa": round(cost / conversions, 2) if conversions > 0 else 0,
                "roas": round(random.uniform(3.0, 8.0), 2)
            })
        
        return keywords