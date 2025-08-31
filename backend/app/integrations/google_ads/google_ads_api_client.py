"""
Google Ads API Client

Wrapper for Google Ads API operations.
Fetches campaign data, keywords, and performance metrics.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import structlog
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from app.config import settings
from app.utils.cache import get_redis
from .google_ads_oauth_handler import GoogleAdsOAuthHandler
import json

logger = structlog.get_logger()


class GoogleAdsAPIClient:
    """Client for interacting with Google Ads API."""
    
    def __init__(self, session_id: str):
        """
        Initialize Google Ads API client.
        
        Args:
            session_id: User's session ID for credentials
        """
        self.session_id = session_id
        self.oauth_handler = GoogleAdsOAuthHandler()
        self.client = None
        self.customer_id = None
    
    async def initialize(self) -> bool:
        """
        Initialize the Google Ads client with user credentials.
        
        Returns:
            True if initialized successfully
        """
        try:
            # Get credentials data from Redis (not the Credentials object)
            from app.utils.cache import get_redis
            redis = await get_redis()
            if not redis:
                logger.error("Redis not available for credentials")
                return False
            
            redis_key = f"google_ads:credentials:{self.session_id}"
            creds_json = await redis.get(redis_key)
            if not creds_json:
                logger.warning("No valid credentials for Google Ads", session_id=self.session_id)
                return False
            
            import json
            creds_data = json.loads(creds_json)
            
            # Create Google Ads client configuration with OAuth2 credentials
            # IMPORTANT: Do not pass client_id/secret separately when using OAuth2 credentials
            config = {
                "developer_token": settings.GOOGLE_ADS_DEVELOPER_TOKEN,
                "refresh_token": creds_data.get("refresh_token"),
                "client_id": settings.GOOGLE_ADS_CLIENT_ID,  # Use from settings, not from stored creds
                "client_secret": settings.GOOGLE_ADS_CLIENT_SECRET,  # Use from settings
                "use_proto_plus": False,  # Disable proto-plus to avoid GRPC issues
                "login_customer_id": None,  # Don't set unless using manager account
            }
            
            # Log config for debugging (without secrets)
            logger.info(f"Initializing Google Ads client")
            logger.info(f"Developer token: {settings.GOOGLE_ADS_DEVELOPER_TOKEN[:10]}...")
            logger.info(f"Client ID: {creds_data.get('client_id', '')[:20]}...")
            logger.info(f"Has refresh token: {bool(creds_data.get('refresh_token'))}")
            
            # Initialize client with OAuth2 credentials format
            try:
                self.client = GoogleAdsClient.load_from_dict(config)
                logger.info("Google Ads client created successfully")
            except Exception as e:
                logger.error(f"Failed to create Google Ads client: {e}")
                raise
            
            # Get customer ID (first accessible account)
            await self._get_customer_id()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Ads client: {e}")
            return False
    
    async def _get_customer_id(self) -> Optional[str]:
        """Get the first accessible customer ID."""
        try:
            customer_service = self.client.get_service("CustomerService", version="v17")
            
            # List accessible customers - simpler call without request object
            accessible_customers = customer_service.list_accessible_customers()
            
            if accessible_customers.resource_names:
                # Extract customer ID from resource name (format: customers/1234567890)
                self.customer_id = accessible_customers.resource_names[0].split("/")[1]
                logger.info(f"Found customer ID: {self.customer_id}")
                return self.customer_id
            
            logger.warning("No accessible customers found")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get customer ID: {e}")
            # Don't use fallback ID as it will cause more errors
            return None
    
    async def get_campaigns(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch active campaigns with performance metrics.
        
        Args:
            limit: Maximum number of campaigns to return
            
        Returns:
            List of campaign data with metrics
        """
        try:
            if not self.client or not self.customer_id:
                if not await self.initialize():
                    return []
            
            # Check cache first
            redis = await get_redis()
            cache_key = f"google_ads:campaigns:{self.session_id}"
            
            if redis:
                cached = await redis.get(cache_key)
                if cached:
                    return json.loads(cached)
            
            # Query for campaigns with metrics
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Simplified query to avoid API version issues
            query = f"""
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    metrics.cost_micros,
                    metrics.clicks,
                    metrics.impressions,
                    metrics.conversions
                FROM campaign
                WHERE segments.date DURING LAST_30_DAYS
                LIMIT {limit}
            """
            
            response = ga_service.search_stream(
                customer_id=self.customer_id,
                query=query
            )
            
            campaigns = []
            for batch in response:
                for row in batch.results:
                    campaign = row.campaign
                    metrics = row.metrics
                    budget = row.campaign_budget
                    
                    campaigns.append({
                        "id": campaign.id,
                        "name": campaign.name,
                        "status": campaign.status.name,
                        "budget": budget.amount_micros / 1_000_000 if budget else 0,
                        "cost": metrics.cost_micros / 1_000_000,
                        "clicks": metrics.clicks,
                        "impressions": metrics.impressions,
                        "conversions": metrics.conversions,
                        "cost_per_conversion": metrics.cost_per_conversion,
                        "ctr": (metrics.clicks / metrics.impressions * 100) if metrics.impressions > 0 else 0,
                        "conversion_rate": (metrics.conversions / metrics.clicks * 100) if metrics.clicks > 0 else 0
                    })
            
            # Cache results for 1 hour
            if redis and campaigns:
                await redis.setex(
                    cache_key,
                    3600,
                    json.dumps(campaigns)
                )
            
            logger.info(
                "Fetched Google Ads campaigns",
                session_id=self.session_id,
                count=len(campaigns)
            )
            
            return campaigns
            
        except GoogleAdsException as e:
            logger.error(f"Google Ads API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to fetch campaigns: {e}")
            return []
    
    async def get_wasted_spend_keywords(self, threshold_cost: float = 100) -> List[Dict[str, Any]]:
        """
        Find keywords with high spend but no conversions.
        
        Args:
            threshold_cost: Minimum spend to consider (in account currency)
            
        Returns:
            List of wasteful keywords with metrics
        """
        try:
            if not self.client or not self.customer_id:
                if not await self.initialize():
                    return []
            
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = """
                SELECT
                    ad_group.name,
                    ad_group_criterion.keyword.text,
                    ad_group_criterion.keyword.match_type,
                    metrics.cost_micros,
                    metrics.clicks,
                    metrics.impressions,
                    metrics.conversions,
                    metrics.average_cpc
                FROM keyword_view
                WHERE 
                    segments.date DURING LAST_30_DAYS
                    AND metrics.cost_micros > {threshold}
                    AND metrics.conversions = 0
                ORDER BY metrics.cost_micros DESC
                LIMIT 20
            """.format(threshold=int(threshold_cost * 1_000_000))
            
            response = ga_service.search_stream(
                customer_id=self.customer_id,
                query=query
            )
            
            wasted_keywords = []
            for batch in response:
                for row in batch.results:
                    keyword = row.ad_group_criterion.keyword
                    metrics = row.metrics
                    
                    wasted_keywords.append({
                        "ad_group": row.ad_group.name,
                        "keyword": keyword.text,
                        "match_type": keyword.match_type.name,
                        "cost": metrics.cost_micros / 1_000_000,
                        "clicks": metrics.clicks,
                        "impressions": metrics.impressions,
                        "avg_cpc": metrics.average_cpc,
                        "ctr": (metrics.clicks / metrics.impressions * 100) if metrics.impressions > 0 else 0
                    })
            
            logger.info(
                "Found wasted spend keywords",
                session_id=self.session_id,
                count=len(wasted_keywords)
            )
            
            return wasted_keywords
            
        except Exception as e:
            logger.error(f"Failed to fetch wasted keywords: {e}")
            return []
    
    async def test_connection(self) -> bool:
        """
        Simple test to verify Google Ads connection works.
        
        Returns:
            True if connection successful
        """
        try:
            if not self.client:
                if not await self.initialize():
                    return False
            
            # Try the simplest possible API call
            customer_service = self.client.get_service("CustomerService")
            
            # This call doesn't need a customer ID
            try:
                request = self.client.get_type("ListAccessibleCustomersRequest")
                result = customer_service.list_accessible_customers(request=request)
                logger.info(f"Connection test successful. Found {len(result.resource_names)} accessible customers")
                return True
            except Exception as e:
                logger.error(f"Connection test failed: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to test connection: {e}")
            return False
    
    async def get_account_performance(self) -> Dict[str, Any]:
        """
        Get overall account performance metrics.
        
        Returns:
            Account-level performance summary
        """
        try:
            if not self.client or not self.customer_id:
                if not await self.initialize():
                    return {}
            
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Get last 30 days vs previous 30 days
            query = """
                SELECT
                    metrics.cost_micros,
                    metrics.clicks,
                    metrics.impressions,
                    metrics.conversions,
                    metrics.conversions_value,
                    segments.date
                FROM customer
                WHERE segments.date DURING LAST_60_DAYS
            """
            
            response = ga_service.search(
                customer_id=self.customer_id,
                query=query
            )
            
            # Split into current and previous period
            today = datetime.now().date()
            thirty_days_ago = today - timedelta(days=30)
            sixty_days_ago = today - timedelta(days=60)
            
            current_metrics = {
                "cost": 0,
                "clicks": 0,
                "impressions": 0,
                "conversions": 0,
                "value": 0
            }
            
            previous_metrics = {
                "cost": 0,
                "clicks": 0,
                "impressions": 0,
                "conversions": 0,
                "value": 0
            }
            
            for row in response:
                date = datetime.strptime(row.segments.date, "%Y-%m-%d").date()
                metrics = row.metrics
                
                if date >= thirty_days_ago:
                    current_metrics["cost"] += metrics.cost_micros / 1_000_000
                    current_metrics["clicks"] += metrics.clicks
                    current_metrics["impressions"] += metrics.impressions
                    current_metrics["conversions"] += metrics.conversions
                    current_metrics["value"] += metrics.conversions_value
                else:
                    previous_metrics["cost"] += metrics.cost_micros / 1_000_000
                    previous_metrics["clicks"] += metrics.clicks
                    previous_metrics["impressions"] += metrics.impressions
                    previous_metrics["conversions"] += metrics.conversions
                    previous_metrics["value"] += metrics.conversions_value
            
            # Calculate derived metrics and changes
            performance = {
                "current_period": {
                    **current_metrics,
                    "ctr": (current_metrics["clicks"] / current_metrics["impressions"] * 100) 
                           if current_metrics["impressions"] > 0 else 0,
                    "conversion_rate": (current_metrics["conversions"] / current_metrics["clicks"] * 100)
                                      if current_metrics["clicks"] > 0 else 0,
                    "cpa": current_metrics["cost"] / current_metrics["conversions"]
                          if current_metrics["conversions"] > 0 else 0,
                    "roas": current_metrics["value"] / current_metrics["cost"]
                           if current_metrics["cost"] > 0 else 0
                },
                "changes": {
                    "cost_change": ((current_metrics["cost"] - previous_metrics["cost"]) / 
                                   previous_metrics["cost"] * 100)
                                  if previous_metrics["cost"] > 0 else 0,
                    "conversions_change": ((current_metrics["conversions"] - previous_metrics["conversions"]) /
                                          previous_metrics["conversions"] * 100)
                                         if previous_metrics["conversions"] > 0 else 0
                }
            }
            
            return performance
            
        except Exception as e:
            logger.error(f"Failed to fetch account performance: {e}")
            return {}
    
    async def get_top_performing_keywords(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get best performing keywords by conversions and ROAS.
        
        Args:
            limit: Number of keywords to return
            
        Returns:
            List of top performing keywords
        """
        try:
            if not self.client or not self.customer_id:
                if not await self.initialize():
                    return []
            
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = """
                SELECT
                    campaign.name,
                    ad_group.name,
                    ad_group_criterion.keyword.text,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.conversions_value,
                    metrics.clicks,
                    metrics.impressions
                FROM keyword_view
                WHERE 
                    segments.date DURING LAST_30_DAYS
                    AND metrics.conversions > 0
                ORDER BY metrics.conversions DESC
                LIMIT {limit}
            """.format(limit=limit)
            
            response = ga_service.search_stream(
                customer_id=self.customer_id,
                query=query
            )
            
            top_keywords = []
            for batch in response:
                for row in batch.results:
                    metrics = row.metrics
                    
                    top_keywords.append({
                        "campaign": row.campaign.name,
                        "ad_group": row.ad_group.name,
                        "keyword": row.ad_group_criterion.keyword.text,
                        "cost": metrics.cost_micros / 1_000_000,
                        "conversions": metrics.conversions,
                        "value": metrics.conversions_value,
                        "clicks": metrics.clicks,
                        "cpa": (metrics.cost_micros / 1_000_000) / metrics.conversions
                              if metrics.conversions > 0 else 0,
                        "roas": metrics.conversions_value / (metrics.cost_micros / 1_000_000)
                               if metrics.cost_micros > 0 else 0
                    })
            
            return top_keywords
            
        except Exception as e:
            logger.error(f"Failed to fetch top keywords: {e}")
            return []