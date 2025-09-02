"""Health check and status endpoints."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import os
import firebase_admin
from firebase_admin import auth as firebase_auth
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "keelo-backend"}


@router.get("/health/firebase")
async def firebase_status() -> Dict[str, Any]:
    """Check Firebase Admin SDK initialization status."""
    try:
        # Check if Firebase app is initialized
        app = firebase_admin.get_app()
        
        # Get configuration details
        config_status = {
            "initialized": True,
            "project_id": app.project_id if hasattr(app, 'project_id') else "unknown",
            "has_credentials": bool(app.credential) if hasattr(app, 'credential') else False,
        }
        
        # Check environment variables
        env_status = {
            "FIREBASE_SERVICE_ACCOUNT_JSON": bool(os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")),
            "SERVICE_ACCOUNT_JSON": bool(os.getenv("SERVICE_ACCOUNT_JSON")),
            "FIREBASE_SERVICE_ACCOUNT_PATH": bool(os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")),
            "GOOGLE_CLOUD_PROJECT": os.getenv("GOOGLE_CLOUD_PROJECT", "not set"),
        }
        
        # Try to verify a test token (this will fail but shows if auth is configured)
        auth_functional = False
        auth_error = None
        try:
            # This will fail with invalid token, but if auth isn't configured it will fail differently
            firebase_auth.verify_id_token("test_token")
        except firebase_admin.exceptions.FirebaseError as e:
            # This is expected - invalid token
            auth_functional = True
            auth_error = "Auth configured (test token invalid as expected)"
        except Exception as e:
            # This suggests auth isn't properly configured
            auth_functional = False
            auth_error = str(e)
        
        return {
            "status": "operational" if config_status["initialized"] and auth_functional else "degraded",
            "firebase_app": config_status,
            "environment_variables": env_status,
            "auth_functional": auth_functional,
            "auth_test": auth_error,
            "recommendation": None if auth_functional else "Please set FIREBASE_SERVICE_ACCOUNT_JSON environment variable with your Firebase service account JSON"
        }
        
    except ValueError as e:
        # Firebase not initialized
        return {
            "status": "error",
            "initialized": False,
            "error": str(e),
            "environment_variables": {
                "FIREBASE_SERVICE_ACCOUNT_JSON": bool(os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")),
                "SERVICE_ACCOUNT_JSON": bool(os.getenv("SERVICE_ACCOUNT_JSON")),
                "FIREBASE_SERVICE_ACCOUNT_PATH": bool(os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")),
                "GOOGLE_CLOUD_PROJECT": os.getenv("GOOGLE_CLOUD_PROJECT", "not set"),
            },
            "recommendation": "Firebase Admin SDK not initialized. Please set FIREBASE_SERVICE_ACCOUNT_JSON environment variable."
        }
    except Exception as e:
        logger.error(f"Firebase status check error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/health/config")
async def config_status() -> Dict[str, Any]:
    """Check overall configuration status."""
    
    # Check critical environment variables
    config = {
        "database": {
            "configured": bool(os.getenv("DATABASE_URL")),
            "url_pattern": "postgresql://..." if os.getenv("DATABASE_URL") else "not set"
        },
        "redis": {
            "configured": bool(os.getenv("REDIS_URL")),
            "url_pattern": "redis://..." if os.getenv("REDIS_URL") else "not set"
        },
        "openai": {
            "configured": bool(os.getenv("OPENAI_API_KEY")),
            "key_pattern": "sk-..." if os.getenv("OPENAI_API_KEY") else "not set"
        },
        "firebase": {
            "service_account_json": bool(os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON") or os.getenv("SERVICE_ACCOUNT_JSON")),
            "project_id": os.getenv("GOOGLE_CLOUD_PROJECT", "not set")
        },
        "cors": {
            "frontend_url": os.getenv("FRONTEND_URL", "not set"),
            "allowed_origins": os.getenv("CORS_ORIGINS", "not set")
        }
    }
    
    # Determine overall health
    critical_configs = [
        config["database"]["configured"],
        config["openai"]["configured"],
        config["firebase"]["service_account_json"]
    ]
    
    all_configured = all(critical_configs)
    
    return {
        "status": "healthy" if all_configured else "incomplete",
        "configuration": config,
        "missing_critical": [] if all_configured else [
            "DATABASE_URL" if not config["database"]["configured"] else None,
            "OPENAI_API_KEY" if not config["openai"]["configured"] else None,
            "FIREBASE_SERVICE_ACCOUNT_JSON" if not config["firebase"]["service_account_json"] else None
        ],
        "recommendation": "All critical services configured" if all_configured else "Please configure missing environment variables in Railway"
    }