"""
Google Ads REST API Client

Direct REST API implementation to bypass GRPC issues.
Uses the Google Ads REST API v17.
"""

from typing import Dict, List, Any, Optional
import httpx
import structlog
from datetime import datetime, timedelta

from app.config import settings
from app.utils.cache import get_redis

logger = structlog.get_logger()


class GoogleAdsRESTClient:
    """Direct REST API client for Google Ads."""
    
    BASE_URL = "https://googleads.googleapis.com/v17"
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.access_token = None
        self.customer_id = None
        
    async def initialize(self) -> bool:
        """Initialize REST client with access token."""
        try:
            # Get stored credentials
            redis = await get_redis()
            if not redis:
                logger.error("Redis not available")
                return False
            
            creds_json = await redis.get(f"google_ads:credentials:{self.session_id}")
            if not creds_json:
                logger.warning(f"No credentials found for session {self.session_id}")
                return False
            
            import json
            creds_data = json.loads(creds_json)
            
            # Get or refresh access token
            self.access_token = await self._get_access_token(creds_data)
            if not self.access_token:
                logger.error("Failed to get access token")
                return False
            
            # Get customer ID
            self.customer_id = await self._get_customer_id()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize REST client: {e}")
            return False
    
    async def _get_access_token(self, creds_data: Dict) -> Optional[str]:
        """Get or refresh access token using refresh token."""
        try:
            # Check if we have a valid access token
            if creds_data.get("token") and creds_data.get("expiry"):
                expiry = datetime.fromisoformat(creds_data["expiry"])
                if expiry > datetime.utcnow():
                    return creds_data["token"]
            
            # Refresh the access token
            refresh_token = creds_data.get("refresh_token")
            if not refresh_token:
                logger.error("No refresh token available")
                return None
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": settings.GOOGLE_ADS_CLIENT_ID,
                        "client_secret": settings.GOOGLE_ADS_CLIENT_SECRET,
                        "refresh_token": refresh_token,
                        "grant_type": "refresh_token"
                    }
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    new_token = token_data.get("access_token")
                    
                    # Update stored credentials with new token
                    creds_data["token"] = new_token
                    creds_data["expiry"] = (
                        datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
                    ).isoformat()
                    
                    # Store updated credentials
                    redis = await get_redis()
                    if redis:
                        await redis.setex(
                            f"google_ads:credentials:{self.session_id}",
                            30 * 24 * 3600,
                            json.dumps(creds_data)
                        )
                    
                    logger.info("Successfully refreshed access token")
                    return new_token
                else:
                    logger.error(f"Failed to refresh token: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            return None
    
    async def _get_customer_id(self) -> Optional[str]:
        """Get first accessible customer ID via REST API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/customers:listAccessibleCustomers",
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "developer-token": settings.GOOGLE_ADS_DEVELOPER_TOKEN,
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("resourceNames"):
                        # Extract customer ID from first resource name
                        customer_id = data["resourceNames"][0].split("/")[1]
                        logger.info(f"Found customer ID: {customer_id}")
                        return customer_id
                else:
                    logger.error(f"Failed to get customer ID: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Failed to get customer ID: {e}")
            
        return None
    
    async def search_stream(self, query: str) -> List[Dict[str, Any]]:
        """Execute a Google Ads Query Language query via REST API."""
        if not self.customer_id:
            logger.error("No customer ID available")
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/customers/{self.customer_id}/googleAds:searchStream",
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "developer-token": settings.GOOGLE_ADS_DEVELOPER_TOKEN,
                        "Content-Type": "application/json",
                    },
                    json={"query": query}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    
                    # Parse the response batches
                    for result in data.get("results", []):
                        results.append(result)
                    
                    return results
                else:
                    logger.error(f"Search failed: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Failed to execute search: {e}")
            return []
    
    async def get_account_performance(self) -> Dict[str, Any]:
        """Get account performance metrics via REST API."""
        try:
            if not await self.initialize():
                return {}
            
            # Simple query for last 30 days performance
            query = """
                SELECT
                    metrics.cost_micros,
                    metrics.clicks,
                    metrics.impressions,
                    metrics.conversions,
                    metrics.conversions_value
                FROM customer
                WHERE segments.date DURING LAST_30_DAYS
            """
            
            results = await self.search_stream(query)
            
            if not results:
                logger.warning("No performance data returned")
                return {}
            
            # Aggregate metrics
            total_cost = sum(r.get("metrics", {}).get("costMicros", 0) for r in results) / 1_000_000
            total_clicks = sum(r.get("metrics", {}).get("clicks", 0) for r in results)
            total_impressions = sum(r.get("metrics", {}).get("impressions", 0) for r in results)
            total_conversions = sum(r.get("metrics", {}).get("conversions", 0) for r in results)
            total_value = sum(r.get("metrics", {}).get("conversionsValue", 0) for r in results)
            
            return {
                "current_period": {
                    "cost": total_cost,
                    "clicks": total_clicks,
                    "impressions": total_impressions,
                    "conversions": total_conversions,
                    "value": total_value,
                    "ctr": (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
                    "conversion_rate": (total_conversions / total_clicks * 100) if total_clicks > 0 else 0,
                    "cpa": total_cost / total_conversions if total_conversions > 0 else 0,
                    "roas": total_value / total_cost if total_cost > 0 else 0
                },
                "changes": {
                    "cost_change": 0,  # Would need previous period data
                    "conversions_change": 0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get account performance: {e}")
            return {}