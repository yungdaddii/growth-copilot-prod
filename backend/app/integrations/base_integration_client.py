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
            
            # Initialize HTTP client with default headers
            self.http_client = httpx.AsyncClient(
                headers=self._get_default_headers(),
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
                return None
            
            key = f"{self.INTEGRATION_NAME}:credentials:{self.session_id}"
            creds_json = await redis.get(key)
            
            if creds_json:
                return json.loads(creds_json)
            
            # Also check for OAuth completion marker
            oauth_marker = await redis.get(f"{self.INTEGRATION_NAME}:oauth_complete:{self.session_id}")
            if oauth_marker:
                # Return minimal credentials to indicate connection
                return {"connected": True}
                
            return None
            
        except Exception as e:
            logger.error(f"Failed to get credentials: {e}")
            return None
    
    async def _ensure_valid_token(self) -> Optional[str]:
        """Get valid access token, refreshing if needed."""
        try:
            if not self.credentials:
                return None
            
            # Check if we have a valid token
            if self.credentials.get("token") and self.credentials.get("expiry"):
                expiry = datetime.fromisoformat(self.credentials["expiry"])
                if expiry > datetime.utcnow():
                    return self.credentials["token"]
            
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
                    
                    # Update stored credentials
                    self.credentials["token"] = new_token
                    self.credentials["expiry"] = (
                        datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
                    ).isoformat()
                    
                    # Save updated credentials
                    await self._save_credentials(self.credentials)
                    
                    logger.info(f"Refreshed token for {self.INTEGRATION_NAME}")
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
                logger.error("HTTP client not initialized")
                return None
            
            url = f"{self.API_BASE_URL}/{endpoint}"
            
            response = await self.http_client.request(
                method=method,
                url=url,
                json=json_data,
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"API request error: {e}")
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