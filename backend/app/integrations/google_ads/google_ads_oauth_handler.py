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
            
            # Store encrypted credentials in database
            async for db in get_db():
                # Check if integration exists
                existing = await db.query(Integration).filter(
                    Integration.user_id == session_id,
                    Integration.type == IntegrationType.GOOGLE_ADS
                ).first()
                
                credentials_data = {
                    "token": credentials.token,
                    "refresh_token": credentials.refresh_token,
                    "token_uri": credentials.token_uri,
                    "client_id": credentials.client_id,
                    "client_secret": credentials.client_secret,
                    "scopes": credentials.scopes,
                    "expiry": credentials.expiry.isoformat() if credentials.expiry else None
                }
                
                encrypted_creds = encrypt_data(json.dumps(credentials_data))
                
                if existing:
                    # Update existing integration
                    existing.credentials = encrypted_creds
                    existing.is_active = True
                    existing.last_sync = datetime.utcnow()
                    existing.last_error = None
                else:
                    # Create new integration
                    integration = Integration(
                        user_id=session_id,
                        type=IntegrationType.GOOGLE_ADS,
                        name="Google Ads",
                        credentials=encrypted_creds,
                        is_active=True,
                        meta_data={}
                    )
                    db.add(integration)
                
                await db.commit()
            
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
            async for db in get_db():
                integration = await db.query(Integration).filter(
                    Integration.user_id == session_id,
                    Integration.type == IntegrationType.GOOGLE_ADS,
                    Integration.is_active == True
                ).first()
                
                if not integration or not integration.credentials:
                    return None
                
                # Decrypt credentials
                creds_json = decrypt_data(integration.credentials)
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
                    
                    # Update stored credentials
                    new_creds_data = {
                        "token": credentials.token,
                        "refresh_token": credentials.refresh_token,
                        "token_uri": credentials.token_uri,
                        "client_id": credentials.client_id,
                        "client_secret": credentials.client_secret,
                        "scopes": credentials.scopes,
                        "expiry": credentials.expiry.isoformat() if credentials.expiry else None
                    }
                    
                    integration.credentials = encrypt_data(json.dumps(new_creds_data))
                    await db.commit()
                
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
            async for db in get_db():
                integration = await db.query(Integration).filter(
                    Integration.user_id == session_id,
                    Integration.type == IntegrationType.GOOGLE_ADS
                ).first()
                
                if integration:
                    # Soft delete - mark as inactive but keep record
                    integration.is_active = False
                    integration.credentials = None  # Clear credentials
                    integration.last_error = "User disconnected"
                    await db.commit()
                    
                    logger.info(
                        "Google Ads disconnected",
                        session_id=session_id
                    )
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Failed to disconnect: {e}")
            return False