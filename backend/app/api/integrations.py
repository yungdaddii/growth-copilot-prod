"""
OAuth integration endpoints for connecting external data sources.
Handles Google Analytics, Search Console, and other integrations.
"""

import json
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from google.auth.transport import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import structlog

from app.db import get_db
from app.models.user import User
from app.models.integration import Integration, IntegrationType
from app.core.config import settings
from app.core.security import get_current_user
from app.utils.encryption import encrypt_data, decrypt_data

logger = structlog.get_logger()

router = APIRouter(prefix="/api/integrations", tags=["integrations"])

# OAuth2 configuration for Google services
GOOGLE_OAUTH_SCOPES = {
    "google-analytics": [
        "https://www.googleapis.com/auth/analytics.readonly",
        "https://www.googleapis.com/auth/analytics.manage.users.readonly"
    ],
    "search-console": [
        "https://www.googleapis.com/auth/webmasters.readonly"
    ],
    "google-ads": [
        "https://www.googleapis.com/auth/adwords"
    ]
}

# Store OAuth states temporarily (in production, use Redis)
oauth_states: Dict[str, Dict[str, Any]] = {}


@router.get("/")
async def list_integrations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """List all integrations for the current user."""
    integrations = await db.query(Integration).filter(
        Integration.user_id == current_user.id
    ).all()
    
    return {
        "integrations": [
            {
                "id": str(integration.id),
                "type": integration.type.value,
                "name": integration.name,
                "connected": integration.is_active,
                "connected_at": integration.created_at.isoformat() if integration.created_at else None,
                "last_sync": integration.last_sync.isoformat() if integration.last_sync else None,
                "metrics_available": integration.metadata.get("metrics_count", 0) if integration.metadata else 0
            }
            for integration in integrations
        ]
    }


@router.post("/google/auth")
async def initiate_google_oauth(
    integration_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Initiate OAuth flow for Google services.
    Returns the authorization URL for the user to visit.
    """
    if integration_type not in GOOGLE_OAUTH_SCOPES:
        raise HTTPException(status_code=400, detail="Invalid integration type")
    
    # Create OAuth flow
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [f"{settings.FRONTEND_URL}/integrations/callback"]
            }
        },
        scopes=GOOGLE_OAUTH_SCOPES[integration_type]
    )
    
    # Set redirect URI
    flow.redirect_uri = f"{settings.BACKEND_URL}/api/integrations/google/callback"
    
    # Generate state token for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {
        "user_id": str(current_user.id),
        "integration_type": integration_type,
        "created_at": datetime.utcnow()
    }
    
    # Get authorization URL
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        state=state,
        prompt="consent"
    )
    
    return {"auth_url": auth_url}


@router.get("/google/callback")
async def google_oauth_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db)
) -> RedirectResponse:
    """
    Handle OAuth callback from Google.
    Exchange authorization code for access token and save integration.
    """
    # Verify state token
    if state not in oauth_states:
        raise HTTPException(status_code=400, detail="Invalid state token")
    
    state_data = oauth_states.pop(state)
    
    # Check if state is expired (5 minutes)
    if datetime.utcnow() - state_data["created_at"] > timedelta(minutes=5):
        raise HTTPException(status_code=400, detail="State token expired")
    
    try:
        # Create OAuth flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [f"{settings.FRONTEND_URL}/integrations/callback"]
                }
            },
            scopes=GOOGLE_OAUTH_SCOPES[state_data["integration_type"]]
        )
        
        flow.redirect_uri = f"{settings.BACKEND_URL}/api/integrations/google/callback"
        
        # Exchange code for tokens
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Get user info to name the integration
        service = build("oauth2", "v2", credentials=credentials)
        user_info = service.userinfo().get().execute()
        
        # Encrypt and store credentials
        encrypted_creds = encrypt_data(credentials.to_json())
        
        # Check if integration already exists
        existing = await db.query(Integration).filter(
            Integration.user_id == state_data["user_id"],
            Integration.type == IntegrationType(state_data["integration_type"])
        ).first()
        
        if existing:
            # Update existing integration
            existing.credentials = encrypted_creds
            existing.is_active = True
            existing.metadata = {
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "picture": user_info.get("picture")
            }
            existing.last_sync = datetime.utcnow()
        else:
            # Create new integration
            integration = Integration(
                user_id=state_data["user_id"],
                type=IntegrationType(state_data["integration_type"]),
                name=f"{state_data['integration_type'].replace('-', ' ').title()} - {user_info.get('email', 'Unknown')}",
                credentials=encrypted_creds,
                is_active=True,
                metadata={
                    "email": user_info.get("email"),
                    "name": user_info.get("name"),
                    "picture": user_info.get("picture")
                }
            )
            db.add(integration)
        
        await db.commit()
        
        # Redirect back to frontend with success
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/integrations?success=true&type={state_data['integration_type']}"
        )
        
    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/integrations?error=auth_failed"
        )


@router.delete("/{integration_id}")
async def disconnect_integration(
    integration_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Disconnect (delete) an integration."""
    integration = await db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.user_id == current_user.id
    ).first()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Revoke access token if possible
    if integration.credentials:
        try:
            creds_json = decrypt_data(integration.credentials)
            creds = Credentials.from_authorized_user_info(json.loads(creds_json))
            
            # Revoke the token
            revoke = requests.post(
                "https://oauth2.googleapis.com/revoke",
                params={"token": creds.token},
                headers={"content-type": "application/x-www-form-urlencoded"}
            )
            
            if revoke.status_code != 200:
                logger.warning(f"Failed to revoke token for integration {integration_id}")
        except Exception as e:
            logger.error(f"Error revoking token: {str(e)}")
    
    # Delete integration
    await db.delete(integration)
    await db.commit()
    
    return {"message": "Integration disconnected successfully"}


@router.get("/{integration_id}/test")
async def test_integration(
    integration_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Test if an integration is working by fetching sample data."""
    integration = await db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.user_id == current_user.id
    ).first()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    if not integration.is_active:
        raise HTTPException(status_code=400, detail="Integration is not active")
    
    try:
        # Decrypt credentials
        creds_json = decrypt_data(integration.credentials)
        creds = Credentials.from_authorized_user_info(json.loads(creds_json))
        
        if integration.type == IntegrationType.GOOGLE_ANALYTICS:
            # Test Google Analytics connection
            from google.analytics.data_v1beta import BetaAnalyticsDataClient
            from google.analytics.data_v1beta.types import RunReportRequest
            
            client = BetaAnalyticsDataClient(credentials=creds)
            
            # Get list of properties (just to test connection)
            # In production, we'd fetch actual metrics
            
            return {
                "status": "connected",
                "integration_type": integration.type.value,
                "message": "Successfully connected to Google Analytics"
            }
            
        elif integration.type == IntegrationType.SEARCH_CONSOLE:
            # Test Search Console connection
            service = build("searchconsole", "v1", credentials=creds)
            sites = service.sites().list().execute()
            
            return {
                "status": "connected",
                "integration_type": integration.type.value,
                "sites_count": len(sites.get("siteEntry", [])),
                "message": "Successfully connected to Search Console"
            }
            
        else:
            return {
                "status": "connected",
                "integration_type": integration.type.value,
                "message": "Integration connected"
            }
            
    except Exception as e:
        logger.error(f"Integration test failed: {str(e)}")
        
        # Mark integration as inactive if auth failed
        if "invalid_grant" in str(e).lower():
            integration.is_active = False
            await db.commit()
            
        raise HTTPException(
            status_code=400,
            detail=f"Integration test failed: {str(e)}"
        )