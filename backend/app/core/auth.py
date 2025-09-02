"""Firebase Authentication module for user authentication and authorization."""

import os
from typing import Optional, Dict, Any
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models.user import User, SubscriptionTier, SubscriptionStatus
from app.schemas.auth import UserCreate, UserResponse

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
cred_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

if cred_json:
    # Use JSON string from environment variable (for Railway)
    import json
    try:
        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized from JSON env var")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase from JSON: {e}")
elif cred_path and os.path.exists(cred_path):
    # Use file path (for local development)
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    logger.info("Firebase Admin SDK initialized from file")
else:
    # Initialize with default credentials (for Google Cloud environments)
    try:
        firebase_admin.initialize_app()
        logger.info("Firebase Admin SDK initialized with default credentials")
    except ValueError:
        # App already initialized
        pass
    except Exception as e:
        logger.warning(f"Firebase Admin SDK not initialized: {e}")

# HTTP Bearer token security
security = HTTPBearer(auto_error=False)


class FirebaseAuth:
    """Firebase Authentication handler."""
    
    @staticmethod
    async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Verify Firebase ID token and return decoded token."""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No authentication credentials provided"
            )
        
        try:
            # Verify the Firebase ID token
            decoded_token = firebase_auth.verify_id_token(credentials.credentials)
            return decoded_token
        except firebase_admin.exceptions.FirebaseError as e:
            logger.error(f"Firebase token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )
    
    @staticmethod
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> User:
        """Get current user from database or create if not exists."""
        # First verify the token
        token = await FirebaseAuth.verify_token(credentials)
        
        firebase_uid = token.get("uid")
        email = token.get("email")
        
        if not firebase_uid or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token data"
            )
        
        # Get or create user
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        
        if not user:
            # Create new user
            user = User(
                firebase_uid=firebase_uid,
                email=email,
                display_name=token.get("name"),
                photo_url=token.get("picture"),
                email_verified=token.get("email_verified", False),
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
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user: {email}")
        else:
            # Update last login
            user.last_login_at = datetime.utcnow()
            db.commit()
        
        return user
    
    @staticmethod
    async def get_optional_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db)
    ) -> Optional[User]:
        """Get current user if authenticated, otherwise return None."""
        if not credentials:
            return None
        
        try:
            # Verify token and get user
            token = await FirebaseAuth.verify_token(credentials)
            
            firebase_uid = token.get("uid")
            email = token.get("email")
            
            if not firebase_uid or not email:
                return None
            
            # Get or create user
            user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
            
            if not user:
                # Create new user
                user = User(
                    firebase_uid=firebase_uid,
                    email=email,
                    display_name=token.get("name"),
                    photo_url=token.get("picture"),
                    email_verified=token.get("email_verified", False),
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
                db.commit()
                db.refresh(user)
            else:
                # Update last login
                user.last_login_at = datetime.utcnow()
                db.commit()
            
            return user
        except HTTPException:
            return None
        except Exception:
            return None
    
    @staticmethod
    async def create_custom_token(uid: str, claims: Optional[Dict[str, Any]] = None) -> str:
        """Create a custom Firebase token with additional claims."""
        try:
            return firebase_auth.create_custom_token(uid, developer_claims=claims)
        except Exception as e:
            logger.error(f"Failed to create custom token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create authentication token"
            )
    
    @staticmethod
    async def set_custom_claims(uid: str, claims: Dict[str, Any]) -> None:
        """Set custom claims for a user."""
        try:
            firebase_auth.set_custom_user_claims(uid, claims)
        except Exception as e:
            logger.error(f"Failed to set custom claims: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user claims"
            )
    
    @staticmethod
    async def revoke_refresh_tokens(uid: str) -> None:
        """Revoke all refresh tokens for a user (effectively logging them out)."""
        try:
            firebase_auth.revoke_refresh_tokens(uid)
        except Exception as e:
            logger.error(f"Failed to revoke refresh tokens: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to revoke tokens"
            )


# Dependency injection shortcuts
verify_token = FirebaseAuth.verify_token
get_current_user = FirebaseAuth.get_current_user
get_optional_user = FirebaseAuth.get_optional_user


class AuthService:
    """Service for authentication-related operations."""
    
    @staticmethod
    async def update_user_profile(
        user: User,
        profile_data: Dict[str, Any],
        db: Session
    ) -> User:
        """Update user profile information."""
        updateable_fields = [
            "display_name", "photo_url", "phone_number",
            "company_name", "company_website", "company_size",
            "industry", "role", "email_notifications", "weekly_report"
        ]
        
        for field in updateable_fields:
            if field in profile_data and profile_data[field] is not None:
                setattr(user, field, profile_data[field])
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    async def update_subscription(
        user: User,
        tier: SubscriptionTier,
        status: SubscriptionStatus,
        stripe_data: Optional[Dict[str, Any]],
        db: Session
    ) -> User:
        """Update user subscription information."""
        user.subscription_tier = tier
        user.subscription_status = status
        
        if stripe_data:
            user.stripe_customer_id = stripe_data.get("customer_id")
            user.stripe_subscription_id = stripe_data.get("subscription_id")
        
        # Update feature flags based on tier
        if tier == SubscriptionTier.FREE:
            user.monthly_analyses_limit = 10
            user.can_export_data = False
            user.can_use_api = False
        elif tier == SubscriptionTier.STARTER:
            user.monthly_analyses_limit = 50
            user.can_export_data = True
            user.can_use_api = False
        elif tier == SubscriptionTier.PRO:
            user.monthly_analyses_limit = 200
            user.can_export_data = True
            user.can_use_api = True
        elif tier == SubscriptionTier.ENTERPRISE:
            user.monthly_analyses_limit = -1  # Unlimited
            user.can_export_data = True
            user.can_use_api = True
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    async def check_rate_limit(user: User, db: Session) -> bool:
        """Check if user has exceeded their rate limit."""
        if user.subscription_tier == SubscriptionTier.ENTERPRISE:
            return True  # No limits for enterprise
        
        if user.monthly_analyses_used >= user.monthly_analyses_limit:
            return False
        
        return True
    
    @staticmethod
    async def increment_usage(user: User, db: Session) -> None:
        """Increment user's usage counter."""
        user.monthly_analyses_used += 1
        user.last_active_at = datetime.utcnow()
        db.commit()