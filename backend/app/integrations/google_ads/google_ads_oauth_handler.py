"""
Google Ads OAuth Handler

Manages OAuth 2.0 flow for Google Ads API authentication.
Handles authorization URL generation and token exchange.
"""

import json
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import structlog
from google.auth.transport import requests as google_requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from app.config import settings
from app.utils.cache import get_redis
from app.utils.encryption import encrypt_data, decrypt_data
from app.models.integration import Integration, IntegrationType
from app.database import get_db

logger = structlog.get_logger()


class GoogleAdsOAuthHandler:
    """Handles OAuth 2.0 flow for Google Ads API."""
    
    # Google Ads API scope
    SCOPES = ['https://www.googleapis.com/auth/adwords']
    
    # OAuth endpoints
    AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
    TOKEN_URI = "https://oauth2.googleapis.com/token"
    
    def __init__(self):
        """Initialize OAuth handler with client credentials."""
        self.client_id = settings.GOOGLE_ADS_CLIENT_ID
        self.client_secret = settings.GOOGLE_ADS_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_ADS_REDIRECT_URI or \
                           f"{settings.BACKEND_URL}/api/integrations/google-ads/oauth/callback"
        
        if not self.client_id or not self.client_secret:
            logger.warning("Google Ads OAuth credentials not configured")
    
    async def generate_auth_url(self, session_id: str) -> Dict[str, str]:
        """
        Generate OAuth authorization URL for user to grant access.
        
        Args:
            session_id: User's session ID for state tracking
            
        Returns:
            Dict with auth_url and state token
        """
        try:
            # Create OAuth flow
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": self.AUTH_URI,
                        "token_uri": self.TOKEN_URI,
                    }
                },
                scopes=self.SCOPES,
                redirect_uri=self.redirect_uri
            )
            
            # Generate authorization URL with state token
            auth_url, state = flow.authorization_url(
                access_type='offline',  # Request refresh token
                include_granted_scopes='true',
                prompt='consent'  # Always show consent screen
            )
            
            # Store state in Redis for verification (expires in 10 minutes)
            redis = await get_redis()
            if redis:
                await redis.setex(
                    f"oauth:google_ads:state:{state}",
                    600,  # 10 minutes
                    json.dumps({
                        "session_id": session_id,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                )
            
            logger.info(
                "Generated Google Ads OAuth URL",
                session_id=session_id,
                state=state[:10] + "..."
            )
            
            return {
                "auth_url": auth_url,
                "state": state
            }
            
        except Exception as e:
            logger.error(f"Failed to generate auth URL: {e}")
            raise
    
    async def handle_callback(
        self,
        code: str,
        state: str
    ) -> Dict[str, Any]:
        """
        Handle OAuth callback and exchange code for tokens.
        
        Args:
            code: Authorization code from Google
            state: State token for verification
            
        Returns:
            Dict with success status and user session_id
        """
        try:
            # Verify state token
            redis = await get_redis()
            state_data = None
            
            if redis:
                state_json = await redis.get(f"oauth:google_ads:state:{state}")
                if state_json:
                    state_data = json.loads(state_json)
                    # Delete state after use
                    await redis.delete(f"oauth:google_ads:state:{state}")
            
            if not state_data:
                raise ValueError("Invalid or expired state token")
            
            session_id = state_data["session_id"]
            
            # Exchange code for tokens
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": self.AUTH_URI,
                        "token_uri": self.TOKEN_URI,
                    }
                },
                scopes=self.SCOPES,
                redirect_uri=self.redirect_uri,
                state=state
            )
            
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            # Store credentials in Redis for now (simpler than database)
            credentials_data = {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
                "expiry": credentials.expiry.isoformat() if credentials.expiry else None
            }
            
            # Store in Redis with 30 day expiry
            redis = await get_redis()
            if redis:
                await redis.setex(
                    f"google_ads:credentials:{session_id}",
                    30 * 24 * 3600,  # 30 days
                    json.dumps(credentials_data)
                )
                logger.info(f"Stored Google Ads credentials in Redis for session {session_id}")
            
            logger.info(
                "Google Ads OAuth successful",
                session_id=session_id
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "message": "Google Ads account connected successfully"
            }
            
        except Exception as e:
            logger.error(f"OAuth callback failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_valid_credentials(self, session_id: str) -> Optional[Credentials]:
        """
        Get valid credentials for a user, refreshing if needed.
        
        Args:
            session_id: User's session ID
            
        Returns:
            Valid Google Credentials object or None
        """
        try:
            # Get credentials from Redis
            redis = await get_redis()
            if not redis:
                return None
                
            creds_json = await redis.get(f"google_ads:credentials:{session_id}")
            if not creds_json:
                return None
                
            creds_data = json.loads(creds_json)
            
            # Create Credentials object
            credentials = Credentials(
                token=creds_data.get("token"),
                refresh_token=creds_data.get("refresh_token"),
                token_uri=creds_data.get("token_uri"),
                client_id=creds_data.get("client_id"),
                client_secret=creds_data.get("client_secret"),
                scopes=creds_data.get("scopes")
            )
            
            # Set expiry if exists
            if creds_data.get("expiry"):
                credentials.expiry = datetime.fromisoformat(creds_data["expiry"])
            
            # Refresh if expired
            if credentials.expired:
                request = google_requests.Request()
                credentials.refresh(request)
                
                # Update stored credentials in Redis
                new_creds_data = {
                    "token": credentials.token,
                    "refresh_token": credentials.refresh_token,
                    "token_uri": credentials.token_uri,
                    "client_id": credentials.client_id,
                    "client_secret": credentials.client_secret,
                    "scopes": credentials.scopes,
                    "expiry": credentials.expiry.isoformat() if credentials.expiry else None
                }
                
                redis = await get_redis()
                if redis:
                    await redis.setex(
                        f"google_ads:credentials:{session_id}",
                        30 * 24 * 3600,  # 30 days
                        json.dumps(new_creds_data)
                    )
            
            return credentials
                
        except Exception as e:
            logger.error(f"Failed to get valid credentials: {e}")
            return None
    
    async def disconnect(self, session_id: str) -> bool:
        """
        Disconnect Google Ads integration for a user.
        
        Args:
            session_id: User's session ID
            
        Returns:
            True if disconnected successfully
        """
        try:
            # Remove credentials from Redis
            redis = await get_redis()
            if redis:
                result = await redis.delete(f"google_ads:credentials:{session_id}")
                if result:
                    logger.info(
                        "Google Ads disconnected",
                        session_id=session_id
                    )
                    return True
            
            return False
                
        except Exception as e:
            logger.error(f"Failed to disconnect: {e}")
            return False