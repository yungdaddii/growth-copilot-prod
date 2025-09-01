#!/usr/bin/env python3
"""
Verify that the Railway deployment has the correct Google Ads fixes.
Run this against the Railway endpoint to confirm deployment.
"""

import requests
import json

# Replace with your Railway URL
RAILWAY_URL = "https://growth-copilot-prod-production.up.railway.app"

def verify_deployment():
    """Check if Railway has the updated code."""
    
    print("=" * 60)
    print("VERIFYING RAILWAY DEPLOYMENT")
    print("=" * 60)
    
    # Check root endpoint for version info
    try:
        response = requests.get(f"{RAILWAY_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ API is responding")
            print(f"Deployment: {data.get('deployment', 'unknown')}")
            print(f"Google Ads Fix: {data.get('google_ads_fix', 'unknown')}")
            print(f"Docker Fix: {data.get('docker_fix', 'unknown')}")
            
            # Check if we have the v3.2 deployment
            if "v3.2-DIRECT-API-CALLS" in data.get('deployment', ''):
                print("\n✅ DEPLOYMENT SUCCESSFUL - v3.2 with direct API calls is live!")
                print("The Google Ads fixes are now active:")
                print("  • Direct API calls (bypass override issues)")
                print("  • GRPC fallback removed")
                print("  • API version v17")
                print("  • POST method for listAccessibleCustomers")
                return True
            elif "v3.1" in data.get('deployment', ''):
                print(f"\n⚠️ Old v3.1 deployment still active")
                print("Waiting for v3.2 deployment...")
                return False
            elif "v3.0" in data.get('deployment', ''):
                print(f"\n⚠️ Old v3.0 deployment still active")
                print("Waiting for v3.2 deployment...")
                return False
            else:
                print(f"\n❌ Unknown deployment: {data.get('deployment')}")
                return False
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking deployment: {e}")
        return False

if __name__ == "__main__":
    success = verify_deployment()
    print("\n" + "=" * 60)
    if success:
        print("NEXT STEPS:")
        print("1. Test Google Ads connection through the UI")
        print("2. Check Railway logs for 'v2.2' logging messages")
        print("3. Look for successful listAccessibleCustomers POST requests")
    else:
        print("ACTION REQUIRED:")
        print("1. Check Railway build logs for errors")
        print("2. Wait for deployment to complete (usually 2-3 minutes)")
        print("3. Run this script again to verify")
    print("=" * 60)