#!/usr/bin/env python3
"""
Google Ads Connection Diagnostic Script

This script helps identify where the Google Ads connection is failing.
Run this locally to test each component of the integration.
"""

import asyncio
import os
import sys
import json
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import structlog
from app.config import settings
from app.utils.cache import get_redis

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


async def check_environment():
    """Check if required environment variables are set."""
    print("\n" + "="*60)
    print("1. CHECKING ENVIRONMENT VARIABLES")
    print("="*60)
    
    required_vars = {
        "GOOGLE_ADS_CLIENT_ID": settings.GOOGLE_ADS_CLIENT_ID,
        "GOOGLE_ADS_CLIENT_SECRET": settings.GOOGLE_ADS_CLIENT_SECRET,
        "GOOGLE_ADS_DEVELOPER_TOKEN": settings.GOOGLE_ADS_DEVELOPER_TOKEN,
        "GOOGLE_ADS_REDIRECT_URI": settings.GOOGLE_ADS_REDIRECT_URI,
        "BACKEND_URL": settings.BACKEND_URL,
        "FRONTEND_URL": settings.FRONTEND_URL,
    }
    
    all_set = True
    for var_name, var_value in required_vars.items():
        if var_value:
            # Show partial value for security
            display_value = var_value[:10] + "..." if len(var_value) > 10 else var_value
            print(f"✅ {var_name}: {display_value}")
        else:
            print(f"❌ {var_name}: NOT SET")
            all_set = False
    
    return all_set


async def check_redis_connection():
    """Check if Redis is accessible."""
    print("\n" + "="*60)
    print("2. CHECKING REDIS CONNECTION")
    print("="*60)
    
    try:
        redis = await get_redis()
        if redis:
            # Test basic operations
            await redis.set("test_key", "test_value")
            value = await redis.get("test_key")
            await redis.delete("test_key")
            
            print(f"✅ Redis connected at: {settings.REDIS_URL}")
            print(f"✅ Basic operations working")
            return True
        else:
            print(f"❌ Redis connection failed")
            return False
    except Exception as e:
        print(f"❌ Redis error: {e}")
        return False


async def check_stored_credentials(session_id: str):
    """Check if credentials are stored for a session."""
    print("\n" + "="*60)
    print("3. CHECKING STORED CREDENTIALS")
    print("="*60)
    print(f"Session ID: {session_id}")
    print("-"*60)
    
    try:
        redis = await get_redis()
        if not redis:
            print("❌ Redis not available")
            return False
        
        # List all Google Ads credential keys
        all_keys = await redis.keys("google_ads:credentials:*")
        if all_keys:
            print(f"Found {len(all_keys)} Google Ads credential keys:")
            for key in all_keys:
                key_str = key.decode() if isinstance(key, bytes) else key
                print(f"  - {key_str}")
        else:
            print("No Google Ads credentials found in Redis")
        
        # Check specific session
        key = f"google_ads:credentials:{session_id}"
        creds_json = await redis.get(key)
        
        if creds_json:
            creds = json.loads(creds_json)
            print(f"\n✅ Credentials found for session {session_id}")
            print(f"  - Has token: {bool(creds.get('token'))}")
            print(f"  - Has refresh token: {bool(creds.get('refresh_token'))}")
            print(f"  - Client ID: {creds.get('client_id', '')[:20]}...")
            print(f"  - Scopes: {creds.get('scopes', [])}")
            
            if creds.get('expiry'):
                expiry = datetime.fromisoformat(creds['expiry'])
                is_expired = expiry < datetime.utcnow()
                print(f"  - Token expiry: {expiry} ({'EXPIRED' if is_expired else 'VALID'})")
            
            return True
        else:
            print(f"❌ No credentials found for session {session_id}")
            
            # Check for OAuth completion marker
            oauth_marker = await redis.get(f"google_ads:oauth_complete:{session_id}")
            if oauth_marker:
                print(f"  ℹ️ OAuth completion marker found (simple client)")
            
            return False
            
    except Exception as e:
        print(f"❌ Error checking credentials: {e}")
        return False


async def test_api_clients(session_id: str):
    """Test each API client to see which works."""
    print("\n" + "="*60)
    print("4. TESTING API CLIENTS")
    print("="*60)
    
    # Test REST API Client
    print("\n--- Testing REST API Client ---")
    try:
        from app.integrations.google_ads.google_ads_rest_api_client import GoogleAdsRESTAPIClient
        
        rest_client = GoogleAdsRESTAPIClient(session_id)
        initialized = await rest_client.initialize()
        
        if initialized:
            print("✅ REST client initialized")
            
            # Try to get account info
            account_info = await rest_client.get_account_info()
            if account_info:
                print(f"✅ Account info retrieved: {account_info}")
            else:
                print("⚠️ No account info returned")
                
            # Try to get performance
            performance = await rest_client.get_account_performance()
            if performance:
                print(f"✅ Performance data retrieved")
            else:
                print("⚠️ No performance data returned")
        else:
            print("❌ REST client failed to initialize")
            
    except Exception as e:
        print(f"❌ REST client error: {e}")
    
    # Test GRPC Client
    print("\n--- Testing GRPC API Client ---")
    try:
        from app.integrations.google_ads.google_ads_api_client import GoogleAdsAPIClient
        
        grpc_client = GoogleAdsAPIClient(session_id)
        initialized = await grpc_client.initialize()
        
        if initialized:
            print("✅ GRPC client initialized")
            
            # Test connection
            connected = await grpc_client.test_connection()
            if connected:
                print("✅ GRPC connection test passed")
            else:
                print("❌ GRPC connection test failed")
        else:
            print("❌ GRPC client failed to initialize")
            
    except Exception as e:
        print(f"❌ GRPC client error: {e}")
    
    # Test Simple Client (Mock)
    print("\n--- Testing Simple Client (Mock) ---")
    try:
        from app.integrations.google_ads.google_ads_simple_client import SimpleGoogleAdsClient
        
        simple_client = SimpleGoogleAdsClient(session_id)
        has_creds = await simple_client.has_credentials()
        
        print(f"Has credentials (OAuth marker): {has_creds}")
        
        if has_creds:
            performance = await simple_client.get_account_performance()
            print(f"✅ Mock data available")
        else:
            print("ℹ️ No OAuth marker - would show connection prompt")
            
    except Exception as e:
        print(f"❌ Simple client error: {e}")


async def test_nlp_responder(session_id: str):
    """Test the NLP responder with fallback logic."""
    print("\n" + "="*60)
    print("5. TESTING NLP RESPONDER (TRIPLE FALLBACK)")
    print("="*60)
    
    try:
        from app.integrations.google_ads.google_ads_nlp_responder import GoogleAdsNLPResponder
        
        responder = GoogleAdsNLPResponder(session_id)
        
        # Test performance query
        print("\nTesting query: 'How are my Google Ads performing?'")
        response = await responder.respond_to_query("How are my Google Ads performing?")
        
        if response:
            print(f"✅ Response generated")
            print(f"  - Using mock data: {responder.using_mock}")
            print(f"  - Response type: {response['metadata'].get('type')}")
            print(f"  - First 200 chars: {response['content'][:200]}...")
        else:
            print("❌ No response generated")
            
    except Exception as e:
        print(f"❌ NLP responder error: {e}")


async def main():
    """Run all diagnostic tests."""
    print("\n" + "="*60)
    print("GOOGLE ADS CONNECTION DIAGNOSTIC")
    print("="*60)
    
    # Get session ID from command line or use default
    session_id = sys.argv[1] if len(sys.argv) > 1 else "test_session_123"
    
    print(f"\nUsing session ID: {session_id}")
    print("\nTo test with your actual session ID, run:")
    print(f"  python {sys.argv[0]} YOUR_SESSION_ID")
    
    # Run checks
    env_ok = await check_environment()
    redis_ok = await check_redis_connection()
    
    if redis_ok:
        has_creds = await check_stored_credentials(session_id)
        await test_api_clients(session_id)
        await test_nlp_responder(session_id)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if not env_ok:
        print("❌ Missing environment variables - check your .env file")
    elif not redis_ok:
        print("❌ Redis connection failed - check Redis is running")
    else:
        print("✅ Basic infrastructure is working")
        print("\nNext steps:")
        print("1. Check Railway logs for specific errors")
        print("2. Verify Google Cloud Console settings:")
        print("   - OAuth consent screen configured")
        print("   - Redirect URI matches your backend URL")
        print("   - Google Ads API enabled")
        print("3. Try reconnecting through the UI")


if __name__ == "__main__":
    asyncio.run(main())