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
            
            # Check if we have the v3.0 deployment
            if "v3.0-FIXED-DOCKER-CACHE" in data.get('deployment', ''):
                print("\n✅ DEPLOYMENT SUCCESSFUL - v3.0 with Docker cache fix is live!")
                print("The Google Ads POST method fix should now be active.")
                return True
            else:
                print(f"\n❌ Old deployment still active: {data.get('deployment')}")
                print("Railway may still be building. Wait a few minutes and try again.")
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