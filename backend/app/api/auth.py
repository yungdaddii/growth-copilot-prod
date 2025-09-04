"""Authentication API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.database import get_db
from app.core.auth import get_current_user, get_optional_user, AuthService, FirebaseAuth
from app.models.user import User
from app.schemas.auth import (
    UserResponse,
    UserUpdate,
    LoginRequest,
    TokenResponse,
    SubscriptionUpdate
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login", response_model=UserResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with Firebase ID token.
    
    This endpoint verifies the Firebase ID token and returns user data.
    If the user doesn't exist, it creates a new user account.
    """
    try:
        # Import Firebase auth
        from firebase_admin import auth as firebase_auth
        import firebase_admin
        
        # Check if Firebase is initialized
        try:
            app = firebase_admin.get_app()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service not configured"
            )
        
        # Verify the Firebase ID token directly
        try:
            decoded_token = firebase_auth.verify_id_token(request.id_token)
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        # Get or create user
        firebase_uid = decoded_token.get("uid")
        email = decoded_token.get("email")
        
        if not firebase_uid or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token data"
            )
        
        result = await db.execute(
            select(User).where(User.firebase_uid == firebase_uid)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user
            from datetime import datetime
            from app.models.user import SubscriptionTier, SubscriptionStatus
            
            user = User(
                firebase_uid=firebase_uid,
                email=email,
                display_name=request.display_name or decoded_token.get("name"),
                photo_url=decoded_token.get("picture"),
                email_verified=decoded_token.get("email_verified", False),
                company_name=request.company_name,
                company_website=request.company_website,
                subscription_tier=SubscriptionTier.FREE,
                subscription_status=SubscriptionStatus.ACTIVE,
                monthly_analyses_limit=10,
                monthly_analyses_used=0,
                can_use_ai_chat=True,
                can_export_data=False,
                can_use_api=False,
                email_notifications=True,
                weekly_report=True,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_login_at=datetime.utcnow()
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"Created new user: {email} with company: {request.company_name}")
        else:
            # Update last login
            from datetime import datetime
            user.last_login_at = datetime.utcnow()
            await db.commit()
            await db.refresh(user)
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile."""
    updated_user = await AuthService.update_user_profile(
        current_user,
        update_data.dict(exclude_unset=True),
        db
    )
    return updated_user


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout current user.
    
    This revokes all refresh tokens for the user, effectively logging them out
    from all devices.
    """
    try:
        await FirebaseAuth.revoke_refresh_tokens(current_user.firebase_uid)
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.delete("/me")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete current user account.
    
    This soft-deletes the user account and revokes all tokens.
    """
    try:
        from datetime import datetime
        
        # Soft delete the user
        current_user.is_active = False
        current_user.deleted_at = datetime.utcnow()
        await db.commit()
        
        # Revoke all tokens
        await FirebaseAuth.revoke_refresh_tokens(current_user.firebase_uid)
        
        return {"message": "Account deleted successfully"}
    except Exception as e:
        logger.error(f"Account deletion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed"
        )


@router.get("/subscription", response_model=dict)
async def get_subscription(
    current_user: User = Depends(get_current_user)
):
    """Get current user's subscription details."""
    return {
        "tier": current_user.subscription_tier,
        "status": current_user.subscription_status,
        "trial_ends_at": current_user.trial_ends_at,
        "monthly_analyses_limit": current_user.monthly_analyses_limit,
        "monthly_analyses_used": current_user.monthly_analyses_used,
        "can_use_ai_chat": current_user.can_use_ai_chat,
        "can_export_data": current_user.can_export_data,
        "can_use_api": current_user.can_use_api
    }


@router.post("/subscription/update", response_model=UserResponse)
async def update_subscription(
    update_data: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user subscription (admin only).
    
    This endpoint should be protected and only accessible by admin users
    or through a webhook from the payment provider.
    """
    # TODO: Add admin authorization check
    
    stripe_data = {
        "customer_id": update_data.stripe_customer_id,
        "subscription_id": update_data.stripe_subscription_id
    }
    
    updated_user = await AuthService.update_subscription(
        current_user,
        update_data.tier,
        update_data.status,
        stripe_data if any(stripe_data.values()) else None,
        db
    )
    
    if update_data.trial_ends_at:
        updated_user.trial_ends_at = update_data.trial_ends_at
        await db.commit()
        await db.refresh(updated_user)
    
    return updated_user


@router.get("/check-rate-limit")
async def check_rate_limit(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check if user has exceeded their rate limit."""
    can_analyze = await AuthService.check_rate_limit(current_user, db)
    
    return {
        "can_analyze": can_analyze,
        "monthly_limit": current_user.monthly_analyses_limit,
        "monthly_used": current_user.monthly_analyses_used,
        "remaining": max(0, current_user.monthly_analyses_limit - current_user.monthly_analyses_used)
    }