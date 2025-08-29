"""
PostHog Analytics Integration for Backend
Tracks API usage, analysis performance, and errors
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime
import posthog
import structlog
from functools import wraps
import asyncio
import time

logger = structlog.get_logger()

# Initialize PostHog
POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY", "")
POSTHOG_HOST = os.getenv("POSTHOG_HOST", "https://app.posthog.com")

if POSTHOG_API_KEY:
    posthog.api_key = POSTHOG_API_KEY
    posthog.host = POSTHOG_HOST
    posthog.debug = os.getenv("ENV", "production") == "development"
    logger.info("PostHog analytics initialized")
else:
    logger.warning("PostHog API key not configured - analytics disabled")


class Analytics:
    """Backend analytics tracking"""
    
    @staticmethod
    def track_event(
        event_name: str,
        properties: Optional[Dict[str, Any]] = None,
        distinct_id: Optional[str] = None
    ):
        """Track a custom event"""
        if not POSTHOG_API_KEY:
            return
        
        try:
            # Use session ID or anonymous ID if no distinct_id provided
            if not distinct_id:
                distinct_id = "anonymous"
            
            # Add timestamp and environment
            if properties is None:
                properties = {}
            
            properties.update({
                "timestamp": datetime.utcnow().isoformat(),
                "environment": os.getenv("ENV", "production"),
                "app": "keelo-backend"
            })
            
            posthog.capture(
                distinct_id=distinct_id,
                event=event_name,
                properties=properties
            )
        except Exception as e:
            logger.error(f"Failed to track event {event_name}: {e}")
    
    @staticmethod
    def track_analysis(
        domain: str,
        conversation_id: str,
        status: str,
        duration: Optional[float] = None,
        issues_found: Optional[int] = None,
        error: Optional[str] = None
    ):
        """Track website analysis events"""
        properties = {
            "domain": domain,
            "conversation_id": str(conversation_id),
            "status": status
        }
        
        if duration:
            properties["duration_seconds"] = duration
        if issues_found is not None:
            properties["issues_found"] = issues_found
        if error:
            properties["error"] = error
        
        Analytics.track_event(
            f"analysis_{status}",
            properties,
            distinct_id=str(conversation_id)
        )
    
    @staticmethod
    def track_websocket(
        event_type: str,
        session_id: str,
        properties: Optional[Dict[str, Any]] = None
    ):
        """Track WebSocket events"""
        if properties is None:
            properties = {}
        
        properties["session_id"] = session_id
        
        Analytics.track_event(
            f"websocket_{event_type}",
            properties,
            distinct_id=session_id
        )
    
    @staticmethod
    def track_api_request(
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: float,
        error: Optional[str] = None
    ):
        """Track API request performance"""
        properties = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "success": 200 <= status_code < 400
        }
        
        if error:
            properties["error"] = error
        
        Analytics.track_event("api_request", properties)
    
    @staticmethod
    def track_analyzer_performance(
        analyzer_name: str,
        domain: str,
        duration: float,
        success: bool,
        error: Optional[str] = None
    ):
        """Track individual analyzer performance"""
        properties = {
            "analyzer": analyzer_name,
            "domain": domain,
            "duration_seconds": duration,
            "success": success
        }
        
        if error:
            properties["error"] = error
        
        Analytics.track_event("analyzer_executed", properties)
    
    @staticmethod
    def identify_user(
        user_id: str,
        properties: Optional[Dict[str, Any]] = None
    ):
        """Identify a user with properties"""
        if not POSTHOG_API_KEY:
            return
        
        try:
            if properties is None:
                properties = {}
            
            properties["identified_at"] = datetime.utcnow().isoformat()
            
            posthog.identify(
                distinct_id=user_id,
                properties=properties
            )
        except Exception as e:
            logger.error(f"Failed to identify user {user_id}: {e}")
    
    @staticmethod
    def track_feature_usage(
        feature_name: str,
        user_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ):
        """Track feature usage"""
        if properties is None:
            properties = {}
        
        properties["feature"] = feature_name
        
        Analytics.track_event(
            "feature_used",
            properties,
            distinct_id=user_id or "anonymous"
        )
    
    @staticmethod
    def track_error(
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Track errors for monitoring"""
        properties = {
            "error_type": error_type,
            "error_message": error_message[:500],  # Limit message length
        }
        
        if context:
            properties["context"] = context
        
        Analytics.track_event("error_occurred", properties)


def track_performance(func):
    """Decorator to track function performance"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        error = None
        result = None
        
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            error = str(e)
            raise
        finally:
            duration = (time.time() - start_time) * 1000  # Convert to ms
            
            Analytics.track_event(
                "function_executed",
                {
                    "function": func.__name__,
                    "duration_ms": duration,
                    "success": error is None,
                    "error": error
                }
            )
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        error = None
        result = None
        
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error = str(e)
            raise
        finally:
            duration = (time.time() - start_time) * 1000  # Convert to ms
            
            Analytics.track_event(
                "function_executed",
                {
                    "function": func.__name__,
                    "duration_ms": duration,
                    "success": error is None,
                    "error": error
                }
            )
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


# Feature flags support
class FeatureFlags:
    """Check feature flags from PostHog"""
    
    @staticmethod
    def is_enabled(
        flag_name: str,
        distinct_id: str = "anonymous"
    ) -> bool:
        """Check if a feature flag is enabled"""
        if not POSTHOG_API_KEY:
            return False  # Default to disabled if not configured
        
        try:
            return posthog.feature_enabled(
                flag_name,
                distinct_id=distinct_id
            )
        except Exception as e:
            logger.error(f"Failed to check feature flag {flag_name}: {e}")
            return False
    
    @staticmethod
    def get_flag_payload(
        flag_name: str,
        distinct_id: str = "anonymous"
    ) -> Optional[Any]:
        """Get feature flag payload (for multivariate flags)"""
        if not POSTHOG_API_KEY:
            return None
        
        try:
            return posthog.get_feature_flag_payload(
                flag_name,
                distinct_id=distinct_id
            )
        except Exception as e:
            logger.error(f"Failed to get flag payload {flag_name}: {e}")
            return None


# Middleware for automatic request tracking
async def track_request_middleware(request, call_next):
    """Middleware to automatically track API requests"""
    start_time = time.time()
    
    # Track request start
    Analytics.track_event(
        "request_started",
        {
            "path": request.url.path,
            "method": request.method,
            "query_params": dict(request.query_params)
        }
    )
    
    try:
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000
        
        # Track request completion
        Analytics.track_api_request(
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code,
            duration_ms=duration
        )
        
        return response
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        
        # Track request error
        Analytics.track_api_request(
            endpoint=request.url.path,
            method=request.method,
            status_code=500,
            duration_ms=duration,
            error=str(e)
        )
        
        raise