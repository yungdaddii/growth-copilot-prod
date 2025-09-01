"""
Google Ads REST API Client

Production-ready REST API implementation for Google Ads.
Inherits from BaseIntegrationClient for consistency across integrations.
"""

from typing import Dict, List, Any, Optional
import structlog
from datetime import datetime, timedelta

from app.integrations.base_integration_client import BaseIntegrationClient
from app.config import settings

logger = structlog.get_logger()


class GoogleAdsRESTAPIClient(BaseIntegrationClient):
    """REST API client for Google Ads using the base integration architecture."""
    
    INTEGRATION_NAME = "google_ads"
    # Google Ads uses a different REST endpoint structure
    API_BASE_URL = "https://googleads.googleapis.com"
    API_VERSION = "v18"  # Try v18, the latest stable version
    SCOPES = [
        'https://www.googleapis.com/auth/adwords',
        'openid', 
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]
    
    def __init__(self, session_id: str):
        """Initialize Google Ads REST client."""
        super().__init__(session_id)
        self.customer_id = None
        self.developer_token = settings.GOOGLE_ADS_DEVELOPER_TOKEN
        
    def _get_default_headers(self) -> Dict[str, str]:
        """Get headers required for Google Ads API."""
        headers = {
            "Content-Type": "application/json",
            "developer-token": self.developer_token
        }
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
            
        return headers
    
    async def make_api_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Override to handle Google Ads specific URL structure."""
        try:
            logger.info(f"[Google Ads REST] make_api_request called with endpoint: {endpoint}")
            
            if not self.http_client:
                logger.error(f"[{self.INTEGRATION_NAME}] HTTP client not initialized")
                return None
            
            # Google Ads API URLs need special handling
            # For listAccessibleCustomers: /v17/customers:listAccessibleCustomers
            # For specific customer: /v17/customers/{customer_id}
            
            # Remove leading slash if present
            if endpoint.startswith("/"):
                endpoint = endpoint[1:]
            
            # Build the complete URL
            url = f"{self.API_BASE_URL}/{self.API_VERSION}/{endpoint}"
            
            logger.info(f"[Google Ads REST] Final URL: {url}")
            
            # Add login-customer-id header if we have a customer ID (needed for some calls)
            headers = self.http_client.headers.copy()
            if hasattr(self, 'customer_id') and self.customer_id and 'listAccessibleCustomers' not in endpoint:
                headers['login-customer-id'] = str(self.customer_id)
                logger.info(f"[{self.INTEGRATION_NAME}] Added login-customer-id header: {self.customer_id}")
            
            response = await self.http_client.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                headers=headers
            )
            
            logger.info(f"[{self.INTEGRATION_NAME}] Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"[{self.INTEGRATION_NAME}] ✅ API request successful")
                return data
            else:
                logger.error(f"[{self.INTEGRATION_NAME}] ❌ API request failed: {response.status_code}")
                logger.error(f"[{self.INTEGRATION_NAME}] Response body: {response.text[:500]}")
                return None
                
        except Exception as e:
            logger.error(f"[{self.INTEGRATION_NAME}] API request error: {e}")
            import traceback
            logger.error(f"[{self.INTEGRATION_NAME}] Traceback: {traceback.format_exc()}")
            return None
    
    async def _custom_initialize(self) -> bool:
        """Google Ads specific initialization - get customer ID."""
        try:
            # Get the first accessible customer ID
            self.customer_id = await self._get_customer_id()
            if not self.customer_id:
                logger.warning("No accessible Google Ads accounts found")
                # Don't fail initialization - user might not have accounts yet
                
            return True
            
        except Exception as e:
            logger.error(f"Google Ads initialization error: {e}")
            return False
    
    async def _get_customer_id(self) -> Optional[str]:
        """Get the first accessible customer ID."""
        try:
            logger.info(f"[REST API] Getting customer ID for session: {self.session_id}")
            logger.info(f"[REST API] Using developer token: {self.developer_token[:10]}...")
            logger.info(f"[REST API] Has access token: {bool(self.access_token)}")
            
            # Google Ads REST API uses POST for listAccessibleCustomers, not GET!
            # This is different from most REST APIs
            response = await self.make_api_request(
                method="POST",  # Changed from GET to POST
                endpoint="customers:listAccessibleCustomers",
                json_data={}  # Empty body for this request
            )
            
            logger.info(f"[REST API] ListAccessibleCustomers response: {response}")
            
            if response and response.get("resourceNames"):
                # Extract customer ID from first resource name
                # Format: customers/1234567890
                customer_id = response["resourceNames"][0].split("/")[1]
                logger.info(f"[REST API] ✅ Found Google Ads customer ID: {customer_id}")
                return customer_id
                
            logger.warning("[REST API] No accessible Google Ads customers found - user may not have any ad accounts")
            return None
            
        except Exception as e:
            logger.error(f"[REST API] Failed to get customer ID: {e}")
            import traceback
            logger.error(f"[REST API] Traceback: {traceback.format_exc()}")
            return None
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get basic Google Ads account information."""
        if not self.customer_id:
            return {
                "connected": True,
                "has_accounts": False,
                "message": "Connected to Google Ads but no ad accounts found"
            }
        
        try:
            # Google Ads doesn't have a simple GET endpoint for customer info
            # We need to use a search query instead
            query = f"""
                SELECT
                    customer.descriptive_name,
                    customer.currency_code,
                    customer.id
                FROM customer
                LIMIT 1
            """
            
            response = await self.search_stream(query)
            
            if response and len(response) > 0:
                customer_data = response[0].get("customer", {})
                return {
                    "connected": True,
                    "has_accounts": True,
                    "customer_id": self.customer_id,
                    "account_name": customer_data.get("descriptiveName", "Unknown"),
                    "currency": customer_data.get("currencyCode", "USD")
                }
            
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            
        return {
            "connected": True,
            "has_accounts": True,
            "customer_id": self.customer_id
        }
    
    async def search_stream(self, query: str) -> List[Dict[str, Any]]:
        """Execute a Google Ads Query Language query."""
        if not self.customer_id:
            logger.warning("[REST API] No customer ID available for search")
            return []
        
        try:
            logger.info(f"[REST API] Executing search query for customer {self.customer_id}")
            response = await self.make_api_request(
                method="POST",  # Google Ads uses POST for search
                endpoint=f"customers/{self.customer_id}/googleAds:searchStream",
                json_data={"query": query}
            )
            
            if response:
                results = []
                for result in response.get("results", []):
                    results.append(result)
                return results
                
            return []
            
        except Exception as e:
            logger.error(f"Search stream failed: {e}")
            return []
    
    async def get_campaigns(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get campaign data with performance metrics."""
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
        
        results = await self.search_stream(query)
        
        campaigns = []
        for row in results:
            campaign = row.get("campaign", {})
            metrics = row.get("metrics", {})
            
            campaigns.append({
                "id": campaign.get("id"),
                "name": campaign.get("name"),
                "status": campaign.get("status"),
                "cost": metrics.get("costMicros", 0) / 1_000_000,
                "clicks": metrics.get("clicks", 0),
                "impressions": metrics.get("impressions", 0),
                "conversions": metrics.get("conversions", 0),
                "ctr": self._calculate_ctr(metrics),
                "conversion_rate": self._calculate_conversion_rate(metrics)
            })
        
        return campaigns
    
    async def get_account_performance(self) -> Dict[str, Any]:
        """Get overall account performance metrics."""
        try:
            # Initialize if needed
            if not self.access_token:
                if not await self.initialize():
                    return {}
            
            if not self.customer_id:
                logger.info("No customer ID - returning empty performance")
                return {}
            
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
                return {}
            
            # Aggregate all metrics
            total_cost = 0
            total_clicks = 0
            total_impressions = 0
            total_conversions = 0
            total_value = 0
            
            for row in results:
                metrics = row.get("metrics", {})
                total_cost += metrics.get("costMicros", 0) / 1_000_000
                total_clicks += metrics.get("clicks", 0)
                total_impressions += metrics.get("impressions", 0)
                total_conversions += metrics.get("conversions", 0)
                total_value += metrics.get("conversionsValue", 0)
            
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
                    "cost_change": 0,  # Would need previous period
                    "conversions_change": 0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get account performance: {e}")
            return {}
    
    async def get_wasted_spend_keywords(self, threshold_cost: float = 100) -> List[Dict[str, Any]]:
        """Find keywords with high spend but no conversions."""
        query = f"""
            SELECT
                ad_group.name,
                ad_group_criterion.keyword.text,
                ad_group_criterion.keyword.match_type,
                metrics.cost_micros,
                metrics.clicks,
                metrics.impressions
            FROM keyword_view
            WHERE 
                segments.date DURING LAST_30_DAYS
                AND metrics.cost_micros > {int(threshold_cost * 1_000_000)}
                AND metrics.conversions = 0
            ORDER BY metrics.cost_micros DESC
            LIMIT 20
        """
        
        results = await self.search_stream(query)
        
        wasted_keywords = []
        for row in results:
            keyword_data = row.get("adGroupCriterion", {}).get("keyword", {})
            metrics = row.get("metrics", {})
            
            wasted_keywords.append({
                "ad_group": row.get("adGroup", {}).get("name"),
                "keyword": keyword_data.get("text"),
                "match_type": keyword_data.get("matchType"),
                "cost": metrics.get("costMicros", 0) / 1_000_000,
                "clicks": metrics.get("clicks", 0),
                "impressions": metrics.get("impressions", 0),
                "ctr": self._calculate_ctr(metrics)
            })
        
        return wasted_keywords
    
    async def get_top_performing_keywords(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get best performing keywords by conversions."""
        query = f"""
            SELECT
                campaign.name,
                ad_group.name,
                ad_group_criterion.keyword.text,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.clicks
            FROM keyword_view
            WHERE 
                segments.date DURING LAST_30_DAYS
                AND metrics.conversions > 0
            ORDER BY metrics.conversions DESC
            LIMIT {limit}
        """
        
        results = await self.search_stream(query)
        
        top_keywords = []
        for row in results:
            metrics = row.get("metrics", {})
            cost = metrics.get("costMicros", 0) / 1_000_000
            conversions = metrics.get("conversions", 0)
            value = metrics.get("conversionsValue", 0)
            
            top_keywords.append({
                "campaign": row.get("campaign", {}).get("name"),
                "ad_group": row.get("adGroup", {}).get("name"),
                "keyword": row.get("adGroupCriterion", {}).get("keyword", {}).get("text"),
                "cost": cost,
                "conversions": conversions,
                "value": value,
                "clicks": metrics.get("clicks", 0),
                "cpa": cost / conversions if conversions > 0 else 0,
                "roas": value / cost if cost > 0 else 0
            })
        
        return top_keywords
    
    def _calculate_ctr(self, metrics: Dict) -> float:
        """Calculate click-through rate."""
        clicks = metrics.get("clicks", 0)
        impressions = metrics.get("impressions", 0)
        return (clicks / impressions * 100) if impressions > 0 else 0
    
    def _calculate_conversion_rate(self, metrics: Dict) -> float:
        """Calculate conversion rate."""
        conversions = metrics.get("conversions", 0)
        clicks = metrics.get("clicks", 0)
        return (conversions / clicks * 100) if clicks > 0 else 0