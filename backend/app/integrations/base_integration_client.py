"""
Base Integration Client

Abstract base class for all third-party integrations.
Provides common functionality for OAuth, REST API calls, and data fetching.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import httpx
import structlog
from datetime import datetime, timedelta
import json

from app.utils.cache import get_redis
from app.config import settings

logger = structlog.get_logger()


class BaseIntegrationClient(ABC):
    """Base class for all integration clients (Google Ads, Salesforce, etc.)"""
    
    # Override these in subclasses
    INTEGRATION_NAME = "base"
    API_BASE_URL = ""
    SCOPES = []
    
    def __init__(self, session_id: str):
        """Initialize with session ID for credential management."""
        self.session_id = session_id
        self.access_token = None
        self.credentials = None
        self.http_client = None
        
    async def initialize(self) -> bool:
        """Initialize the client with stored credentials."""
        try:
            # Get stored credentials from Redis
            self.credentials = await self._get_stored_credentials()
            if not self.credentials:
                logger.warning(f"No credentials found for {self.INTEGRATION_NAME}")
                return False
            
            # Get or refresh access token
            self.access_token = await self._ensure_valid_token()
            if not self.access_token:
                logger.error(f"Failed to get access token for {self.INTEGRATION_NAME}")
                return False
            
            logger.info(f"[{self.INTEGRATION_NAME}] Access token obtained: {self.access_token[:20]}...")
            
            # Initialize HTTP client with default headers
            headers = self._get_default_headers()
            logger.info(f"[{self.INTEGRATION_NAME}] Default headers: {headers}")
            
            self.http_client = httpx.AsyncClient(
                headers=headers,
                timeout=30.0
            )
            
            # Run any integration-specific initialization
            return await self._custom_initialize()
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.INTEGRATION_NAME}: {e}")
            return False
    
    async def cleanup(self):
        """Clean up resources."""
        if self.http_client:
            await self.http_client.aclose()
    
    async def _get_stored_credentials(self) -> Optional[Dict]:
        """Get credentials from Redis."""
        try:
            redis = await get_redis()
            if not redis:
                logger.error(f"[{self.INTEGRATION_NAME}] Redis not available for credential retrieval")
                return None
            
            key = f"{self.INTEGRATION_NAME}:credentials:{self.session_id}"
            logger.info(f"[{self.INTEGRATION_NAME}] Looking for credentials with key: {key}")
            
            # Debug: List all related keys
            all_keys = await redis.keys(f"{self.INTEGRATION_NAME}:credentials:*")
            if all_keys:
                logger.info(f"[{self.INTEGRATION_NAME}] Found {len(all_keys)} credential keys in Redis")
                for k in all_keys[:3]:  # Show first 3
                    key_str = k.decode() if isinstance(k, bytes) else k
                    logger.info(f"  - {key_str}")
            
            creds_json = await redis.get(key)
            
            if creds_json:
                creds = json.loads(creds_json)
                logger.info(f"[{self.INTEGRATION_NAME}] ✅ Found credentials for session {self.session_id}")
                logger.info(f"  - Has refresh token: {bool(creds.get('refresh_token'))}")
                return creds
            
            # Also check for OAuth completion marker
            oauth_marker = await redis.get(f"{self.INTEGRATION_NAME}:oauth_complete:{self.session_id}")
            if oauth_marker:
                logger.info(f"[{self.INTEGRATION_NAME}] Found OAuth marker but no full credentials")
                # Return minimal credentials to indicate connection
                return {"connected": True}
            
            logger.warning(f"[{self.INTEGRATION_NAME}] No credentials found for session {self.session_id}")
            return None
            
        except Exception as e:
            logger.error(f"[{self.INTEGRATION_NAME}] Failed to get credentials: {e}")
            import traceback
            logger.error(f"[{self.INTEGRATION_NAME}] Traceback: {traceback.format_exc()}")
            return None
    
    async def _ensure_valid_token(self) -> Optional[str]:
        """Get valid access token, refreshing if needed."""
        try:
            if not self.credentials:
                logger.error(f"[{self.INTEGRATION_NAME}] No credentials available for token validation")
                return None
            
            # Check if we have a valid token
            if self.credentials.get("token") and self.credentials.get("expiry"):
                expiry = datetime.fromisoformat(self.credentials["expiry"])
                now = datetime.utcnow()
                
                # Add 5 minute buffer before expiry
                if expiry > (now + timedelta(minutes=5)):
                    logger.info(f"[{self.INTEGRATION_NAME}] Token valid until {expiry}")
                    return self.credentials["token"]
                else:
                    logger.info(f"[{self.INTEGRATION_NAME}] Token expired or expiring soon, refreshing...")
            
            # Refresh the token
            return await self._refresh_token()
            
        except Exception as e:
            logger.error(f"Failed to ensure valid token: {e}")
            return None
    
    async def _refresh_token(self) -> Optional[str]:
        """Refresh OAuth access token."""
        try:
            refresh_token = self.credentials.get("refresh_token")
            if not refresh_token:
                logger.error(f"No refresh token for {self.INTEGRATION_NAME}")
                return None
            
            # Get client credentials from settings
            client_id = getattr(settings, f"{self.INTEGRATION_NAME.upper()}_CLIENT_ID", None)
            client_secret = getattr(settings, f"{self.INTEGRATION_NAME.upper()}_CLIENT_SECRET", None)
            
            if not client_id or not client_secret:
                logger.error(f"Missing OAuth credentials for {self.INTEGRATION_NAME}")
                return None
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "refresh_token": refresh_token,
                        "grant_type": "refresh_token"
                    }
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    new_token = token_data.get("access_token")
                    
                    logger.info(f"[{self.INTEGRATION_NAME}] Token refreshed successfully")
                    
                    # Update stored credentials
                    self.credentials["token"] = new_token
                    self.credentials["expiry"] = (
                        datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
                    ).isoformat()
                    
                    # Save updated credentials
                    await self._save_credentials(self.credentials)
                    
                    logger.info(f"[{self.INTEGRATION_NAME}] ✅ New token saved, expires in {token_data.get('expires_in', 3600)} seconds")
                    return new_token
                else:
                    logger.error(f"Token refresh failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            return None
    
    async def _save_credentials(self, credentials: Dict):
        """Save credentials to Redis."""
        try:
            redis = await get_redis()
            if redis:
                key = f"{self.INTEGRATION_NAME}:credentials:{self.session_id}"
                await redis.setex(
                    key,
                    30 * 24 * 3600,  # 30 days
                    json.dumps(credentials)
                )
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
    
    async def make_api_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Make an API request with authentication."""
        try:
            if not self.http_client:
                logger.error(f"[{self.INTEGRATION_NAME}] HTTP client not initialized")
                return None
            
            url = f"{self.API_BASE_URL}/{endpoint}"
            
            logger.info(f"[{self.INTEGRATION_NAME}] Making {method} request to: {url}")
            logger.info(f"[{self.INTEGRATION_NAME}] Headers: {self._get_default_headers()}")
            if json_data:
                logger.info(f"[{self.INTEGRATION_NAME}] Body: {json_data}")
            
            response = await self.http_client.request(
                method=method,
                url=url,
                json=json_data,
                params=params
            )
            
            logger.info(f"[{self.INTEGRATION_NAME}] Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"[{self.INTEGRATION_NAME}] ✅ API request successful")
                return data
            else:
                logger.error(f"[{self.INTEGRATION_NAME}] ❌ API request failed: {response.status_code}")
                logger.error(f"[{self.INTEGRATION_NAME}] Response body: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"[{self.INTEGRATION_NAME}] API request error: {e}")
            import traceback
            logger.error(f"[{self.INTEGRATION_NAME}] Traceback: {traceback.format_exc()}")
            return None
    
    async def has_valid_connection(self) -> bool:
        """Check if integration is connected and working."""
        credentials = await self._get_stored_credentials()
        return credentials is not None
    
    # Abstract methods to be implemented by subclasses
    
    @abstractmethod
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        pass
    
    @abstractmethod
    async def _custom_initialize(self) -> bool:
        """Run integration-specific initialization."""
        pass
    
    @abstractmethod
    async def get_account_info(self) -> Dict[str, Any]:
        """Get basic account information."""
        pass