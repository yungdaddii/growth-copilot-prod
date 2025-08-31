"""
Google Ads API Router

Handles OAuth callbacks and API endpoints for Google Ads integration.
"""

from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
import structlog

from app.integrations import is_integration_enabled
from .google_ads_oauth_handler import GoogleAdsOAuthHandler

logger = structlog.get_logger()
router = APIRouter(prefix="/api/integrations/google-ads", tags=["google-ads"])

class AuthRequest(BaseModel):
    session_id: str


@router.post("/auth-url")
async def generate_auth_url(request: AuthRequest):
    """
    Generate OAuth authorization URL for user to grant access.
    
    Args:
        request: Contains session_id for tracking
        
    Returns:
        Authorization URL to redirect user to
    """
    # Temporarily disabled check for testing
    # if not is_integration_enabled("google_ads"):
    #     raise HTTPException(status_code=403, detail="Google Ads integration is disabled")
    
    try:
        oauth_handler = GoogleAdsOAuthHandler()
        result = await oauth_handler.generate_auth_url(request.session_id)
        
        return JSONResponse(content={
            "auth_url": result["auth_url"],
            "state": result["state"]
        })
        
    except Exception as e:
        logger.error(f"Failed to generate auth URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/oauth/callback")
async def oauth_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="State token for verification")
):
    """
    Handle OAuth callback from Google.
    
    This endpoint is called by Google after user grants permission.
    """
    # Temporarily disabled check for testing
    # if not is_integration_enabled("google_ads"):
    #     raise HTTPException(status_code=403, detail="Google Ads integration is disabled")
    
    try:
        oauth_handler = GoogleAdsOAuthHandler()
        result = await oauth_handler.handle_callback(code, state)
        
        # Get frontend URL once
        frontend_url = settings.FRONTEND_URL
        
        if result["success"]:
            # Mark OAuth as complete in simple system
            from .google_ads_simple_client import SimpleGoogleAdsClient
            session_id = result.get("session_id")
            if session_id:
                client = SimpleGoogleAdsClient(session_id)
                await client.mark_oauth_complete()
                logger.info(f"Marked OAuth complete for session {session_id}")
            
            # Redirect to frontend with success message
            return RedirectResponse(
                url=f"{frontend_url}?google_ads_connected=true&message=Google+Ads+connected+successfully"
            )
        else:
            # Redirect with error
            return RedirectResponse(
                url=f"{frontend_url}?google_ads_connected=false&error={result.get('error', 'Connection failed')}"
            )
            
    except Exception as e:
        import traceback
        logger.error(f"OAuth callback failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Include more specific error in redirect for debugging
        error_msg = str(e).replace(" ", "+").replace(":", "")[:100]  # Sanitize for URL
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}?google_ads_connected=false&error={error_msg}"
        )


@router.get("/status")
async def check_connection_status(session_id: str = Query(...)):
    """
    Check if Google Ads is connected for a session.
    
    Args:
        session_id: User's session ID
        
    Returns:
        Connection status
    """
    # Temporarily disabled check for testing
    # if not is_integration_enabled("google_ads"):
    #     return JSONResponse(
    #         content={"connected": False, "error": "Integration disabled"},
    #         status_code=403
    #     )
    
    try:
        # Use simple client to check connection status
        from .google_ads_simple_client import SimpleGoogleAdsClient
        client = SimpleGoogleAdsClient(session_id)
        connected = await client.has_credentials()
        
        return {
            "connected": connected,
            "platform": "google_ads"
        }
        
    except Exception as e:
        logger.error(f"Failed to check connection status: {e}")
        return {
            "connected": False,
            "error": str(e)
        }


class DisconnectRequest(BaseModel):
    session_id: str

@router.post("/disconnect")
async def disconnect(request: DisconnectRequest):
    """
    Disconnect Google Ads for a session.
    
    Args:
        request: Request containing session_id
        
    Returns:
        Disconnection result
    """
    session_id = request.session_id
    # Temporarily disabled check for testing
    # if not is_integration_enabled("google_ads"):
    #     raise HTTPException(status_code=403, detail="Google Ads integration is disabled")
    
    try:
        oauth_handler = GoogleAdsOAuthHandler()
        success = await oauth_handler.disconnect(session_id)
        
        return {
            "success": success,
            "message": "Google Ads disconnected" if success else "No connection found"
        }
        
    except Exception as e:
        logger.error(f"Failed to disconnect: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Import settings at the end to avoid circular imports
from app.config import settings