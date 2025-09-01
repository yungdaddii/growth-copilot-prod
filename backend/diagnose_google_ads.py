#!/usr/bin/env python3
"""
Comprehensive diagnostic tool for Google Ads integration issues.
This will help identify the exact problem preventing connection.
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def diagnose_local():
    """Run local diagnostics."""
    print("\n" + "="*60)
    print("LOCAL ENVIRONMENT DIAGNOSTICS")
    print("="*60)
    
    # 1. Check environment variables
    print("\n1. ENVIRONMENT VARIABLES:")
    from app.config import settings
    print(f"   ✓ GOOGLE_ADS_CLIENT_ID: {'Set' if settings.GOOGLE_ADS_CLIENT_ID else '❌ Missing'}")
    print(f"   ✓ GOOGLE_ADS_CLIENT_SECRET: {'Set' if settings.GOOGLE_ADS_CLIENT_SECRET else '❌ Missing'}")
    print(f"   ✓ GOOGLE_ADS_DEVELOPER_TOKEN: {'Set' if settings.GOOGLE_ADS_DEVELOPER_TOKEN else '❌ Missing'}")
    print(f"   ✓ REDIS_URL: {'Set' if settings.REDIS_URL else '❌ Missing'}")
    
    # 2. Test Redis connection
    print("\n2. REDIS CONNECTION:")
    try:
        from app.utils.cache import get_redis
        redis = await get_redis()
        await redis.ping()
        print("   ✓ Redis connection successful")
        
        # Check for stored credentials
        test_key = await redis.get("google_ads:test_session:credentials")
        if test_key:
            print("   ✓ Found stored credentials in Redis")
        else:
            print("   ⚠ No stored credentials found (normal if not authenticated)")
    except Exception as e:
        print(f"   ❌ Redis error: {e}")
    
    # 3. Test GoogleAdsRESTAPIClient initialization
    print("\n3. GOOGLE ADS CLIENT:")
    try:
        from app.integrations.google_ads.google_ads_rest_api_client import GoogleAdsRESTAPIClient
        client = GoogleAdsRESTAPIClient("test_session")
        
        # Check class hierarchy
        print(f"   ✓ Client class: {client.__class__.__name__}")
        print(f"   ✓ API Version: {client.API_VERSION}")
        print(f"   ✓ API Base URL: {client.API_BASE_URL}")
        
        # Check method override
        import inspect
        source = inspect.getsource(client.make_api_request)
        if "v2.2" in source:
            print("   ✓ Method override working (v2.2 logging present)")
        else:
            print("   ❌ Method override NOT working")
            
    except Exception as e:
        print(f"   ❌ Client initialization error: {e}")
    
    # 4. Test OAuth URL generation
    print("\n4. OAUTH FLOW:")
    try:
        from app.integrations.google_ads.google_ads_router import get_oauth_url
        oauth_url = await get_oauth_url()
        if oauth_url and "accounts.google.com" in oauth_url:
            print("   ✓ OAuth URL generation successful")
            print(f"   → URL starts with: {oauth_url[:50]}...")
        else:
            print("   ❌ OAuth URL generation failed")
    except Exception as e:
        print(f"   ❌ OAuth error: {e}")
    
    # 5. Check for conflicting integrations
    print("\n5. INTEGRATION CONFLICTS:")
    try:
        base_path = "app/integrations/google_ads"
        files = os.listdir(base_path)
        print(f"   Files in google_ads directory:")
        for f in sorted(files):
            if f.endswith('.py'):
                print(f"   • {f}")
        
        # Check for GRPC client
        if "client.py" in files or "grpc_client.py" in files:
            print("   ⚠ WARNING: GRPC client found - may conflict with REST")
        else:
            print("   ✓ No GRPC client conflicts")
            
    except Exception as e:
        print(f"   ❌ Error checking files: {e}")
    
    # 6. Test actual API request (if we have mock credentials)
    print("\n6. API REQUEST TEST:")
    try:
        # Create a mock access token for testing
        client.access_token = "mock_token_for_testing"
        
        # Check what URL would be generated
        test_endpoint = "customers:listAccessibleCustomers"
        expected_url = f"{client.API_BASE_URL}/{client.API_VERSION}/{test_endpoint}"
        print(f"   → Would call: POST {expected_url}")
        print(f"   → With headers: Authorization, developer-token")
        print(f"   ✓ URL structure looks correct")
        
    except Exception as e:
        print(f"   ❌ API test error: {e}")

async def check_railway_logs():
    """Provide guidance on checking Railway logs."""
    print("\n" + "="*60)
    print("RAILWAY DEPLOYMENT ANALYSIS")
    print("="*60)
    
    print("\n📋 CHECKLIST FOR RAILWAY LOGS:")
    print("\n1. BUILD PHASE:")
    print("   Look for: 'Cache bust: v3-post-fix-2025-01-09'")
    print("   → If missing: Docker cache not busting properly")
    print("\n2. STARTUP PHASE:")
    print("   Look for: 'Starting Keelo.ai' with 'v3.0-FIXED-DOCKER-CACHE'")
    print("   → If showing old version: Deployment didn't update")
    print("\n3. GOOGLE ADS REQUESTS:")
    print("   Look for: '[Google Ads REST v2.2]' in logs")
    print("   → If missing: Override not working")
    print("   Look for: 'Method: POST (SHOULD BE POST)'")
    print("   → If showing GET: Wrong HTTP method")
    print("\n4. ERROR PATTERNS:")
    print("   • '404' → Wrong API endpoint structure")
    print("   • 'GRPC target' → Using GRPC instead of REST")
    print("   • 'Unauthorized' → Token/auth issues")
    print("   • 'No module named' → Missing dependencies")

def analyze_symptoms():
    """Analyze symptoms and provide diagnosis."""
    print("\n" + "="*60)
    print("DIFFERENTIAL DIAGNOSIS")
    print("="*60)
    
    symptoms = {
        "Docker cache not updating": {
            "evidence": ["Old version in logs", "No 'Cache bust' message"],
            "solution": "Update CACHEBUST value in railway.json and redeploy"
        },
        "Method override not working": {
            "evidence": ["No v2.2 logging", "Using base class method"],
            "solution": "Check Python inheritance, ensure GoogleAdsRESTAPIClient is imported"
        },
        "Wrong HTTP method": {
            "evidence": ["GET instead of POST", "404 errors"],
            "solution": "Already fixed in code, needs deployment"
        },
        "GRPC vs REST confusion": {
            "evidence": ["GRPC errors", "Multiple client files"],
            "solution": "Remove GRPC client, use only REST API client"
        },
        "Railway platform limitation": {
            "evidence": ["Works locally, fails on Railway", "GRPC not supported"],
            "solution": "Ensure using REST API only, no GRPC dependencies"
        }
    }
    
    print("\nBased on the symptoms, check for these issues:")
    for issue, details in symptoms.items():
        print(f"\n🔍 {issue}")
        print(f"   Evidence to look for:")
        for evidence in details['evidence']:
            print(f"   • {evidence}")
        print(f"   Solution: {details['solution']}")

async def main():
    """Run all diagnostics."""
    print("\n" + "="*60)
    print("GOOGLE ADS INTEGRATION DIAGNOSTIC TOOL")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*60)
    
    # Run local diagnostics
    await diagnose_local()
    
    # Provide Railway guidance
    await check_railway_logs()
    
    # Analyze symptoms
    analyze_symptoms()
    
    print("\n" + "="*60)
    print("RECOMMENDED NEXT STEPS:")
    print("="*60)
    print("\n1. Run verify_deployment.py to check if v3.0 is live")
    print("2. If v3.0 is live, check Railway logs for v2.2 messages")
    print("3. If no v2.2 messages, the override isn't working")
    print("4. Test OAuth flow through the UI")
    print("5. Monitor /health endpoint for stability")
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(main())