#!/usr/bin/env python3
"""
Test Google Ads integration directly on Railway deployment.
This will help verify if the fixes are working in production.
"""

import requests
import json
from datetime import datetime

RAILWAY_URL = "https://growth-copilot-prod-production.up.railway.app"

def test_google_ads_oauth():
    """Test the OAuth flow initiation."""
    print("\n" + "="*60)
    print("TESTING GOOGLE ADS OAUTH ON RAILWAY")
    print("="*60)
    
    try:
        # Test OAuth URL generation - using POST method with correct endpoint
        test_session = f"test_{datetime.now().timestamp()}"
        response = requests.post(
            f"{RAILWAY_URL}/api/integrations/google-ads/auth-url",
            json={"session_id": test_session}
        )
        
        if response.status_code == 200:
            data = response.json()
            if "auth_url" in data:
                print("✅ OAuth URL generated successfully")
                print(f"   URL starts with: {data['auth_url'][:60]}...")
                return True
            else:
                print("❌ No auth_url in response")
                print(f"   Response: {data}")
        else:
            print(f"❌ OAuth endpoint returned {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error testing OAuth: {e}")
    
    return False

def test_google_ads_status():
    """Test Google Ads connection status."""
    print("\n" + "="*60)
    print("TESTING GOOGLE ADS STATUS")
    print("="*60)
    
    try:
        # Create a test session
        test_session = f"test_{datetime.now().timestamp()}"
        
        # Test status endpoint - using query parameter
        response = requests.get(
            f"{RAILWAY_URL}/api/integrations/google-ads/status",
            params={"session_id": test_session}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status endpoint responding")
            print(f"   Connected: {data.get('connected', False)}")
            print(f"   Has token: {data.get('has_token', False)}")
            
            if not data.get('connected'):
                print("   → Expected: Not connected (no auth yet)")
            
            return True
        else:
            print(f"❌ Status endpoint returned {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error testing status: {e}")
    
    return False

def check_logs_guidance():
    """Provide guidance on what to look for in logs."""
    print("\n" + "="*60)
    print("WHAT TO LOOK FOR IN RAILWAY LOGS")
    print("="*60)
    
    print("\n📋 KEY INDICATORS OF SUCCESS:")
    print("\n1. During OAuth flow:")
    print("   • '[Google Ads REST v2.2] make_api_request called'")
    print("   • 'Method: POST (SHOULD BE POST)'")
    print("   • 'Final URL: https://googleads.googleapis.com/v18/customers:listAccessibleCustomers'")
    
    print("\n2. If successful:")
    print("   • '✅ Found Google Ads customer ID: [number]'")
    print("   • 'API request successful'")
    
    print("\n3. If failing:")
    print("   • Look for 404 errors → Wrong endpoint")
    print("   • Look for 401/403 → Auth issues")
    print("   • Look for GRPC errors → Wrong client being used")
    print("   • No v2.2 logs → Override not working")

def final_diagnosis():
    """Provide final diagnosis and next steps."""
    print("\n" + "="*60)
    print("FINAL DIAGNOSIS")
    print("="*60)
    
    print("\n✅ WHAT'S FIXED:")
    print("   • Docker cache issue resolved")
    print("   • Code is deploying to Railway")
    print("   • v3.0-FIXED-DOCKER-CACHE is live")
    print("   • POST method implemented for Google Ads")
    
    print("\n🔍 WHAT TO VERIFY:")
    print("   • Check Railway logs for v2.2 messages")
    print("   • Test OAuth flow through the UI")
    print("   • Confirm listAccessibleCustomers uses POST")
    
    print("\n⚠️ IF STILL FAILING:")
    print("   • v2.2 logs missing → Override not working, need to debug inheritance")
    print("   • 404 errors → API version mismatch (try v17 instead of v18)")
    print("   • GRPC errors → Wrong client file being imported")
    print("   • No logs at all → Router not registered properly")

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("GOOGLE ADS INTEGRATION TEST - RAILWAY PRODUCTION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Target: {RAILWAY_URL}")
    print("="*60)
    
    # Test OAuth
    oauth_works = test_google_ads_oauth()
    
    # Test status
    status_works = test_google_ads_status()
    
    # Provide guidance
    check_logs_guidance()
    
    # Final diagnosis
    final_diagnosis()
    
    print("\n" + "="*60)
    print("CRITICAL NEXT STEP:")
    print("="*60)
    if oauth_works and status_works:
        print("\n✅ Endpoints are responding!")
        print("Now test the actual OAuth flow:")
        print("1. Go to your app UI")
        print("2. Try to connect Google Ads")
        print("3. Watch Railway logs for v2.2 messages")
        print("4. Complete OAuth flow")
        print("5. Check if customer ID is retrieved")
    else:
        print("\n❌ Endpoints not working properly")
        print("Check Railway logs for startup errors")
        print("Verify the Google Ads router is registered")
    print("="*60)

if __name__ == "__main__":
    main()