#!/usr/bin/env python3
"""Test production authentication."""

import requests
import json

# Your production Railway URL
BACKEND_URL = "https://growth-copilot-prod-production.up.railway.app"

print("Testing Production Authentication Setup")
print("=" * 50)

# Test 1: Check if backend is accessible
print("\n1. Testing backend availability...")
try:
    response = requests.get(f"{BACKEND_URL}/docs", timeout=5)
    if response.status_code == 200:
        print("✅ Backend is accessible")
    else:
        print(f"⚠️ Backend returned status: {response.status_code}")
except Exception as e:
    print(f"❌ Cannot reach backend: {e}")

# Test 2: Check Firebase health
print("\n2. Checking Firebase configuration...")
try:
    response = requests.get(f"{BACKEND_URL}/health/firebase", timeout=5)
    data = response.json()
    
    if data.get("status") == "operational":
        print("✅ Firebase Admin SDK is configured properly!")
        print("   Authentication should be working!")
    elif data.get("status") == "degraded":
        print("❌ Firebase Admin SDK is NOT configured")
        print(f"   Recommendation: {data.get('recommendation', 'Add FIREBASE_SERVICE_ACCOUNT_JSON to Railway')}")
    else:
        print(f"❌ Firebase status: {data.get('status')}")
        print(f"   Error: {data.get('error', 'Unknown')}")
except Exception as e:
    print(f"❌ Health check failed: {e}")

# Test 3: Check configuration
print("\n3. Checking overall configuration...")
try:
    response = requests.get(f"{BACKEND_URL}/health/config", timeout=5)
    data = response.json()
    
    if data.get("status") == "healthy":
        print("✅ All configurations are healthy")
    else:
        print(f"⚠️ Configuration status: {data.get('status')}")
        missing = data.get("missing_critical", [])
        if missing:
            print(f"   Missing: {', '.join(filter(None, missing))}")
except Exception as e:
    print(f"❌ Config check failed: {e}")

# Test 4: Test auth endpoint
print("\n4. Testing auth endpoint...")
try:
    response = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json={"id_token": "test_token"},
        timeout=5
    )
    
    if response.status_code == 401:
        print("✅ Auth endpoint is responding (rejected invalid token as expected)")
    elif response.status_code == 503:
        print("❌ Auth service not configured (Firebase Admin SDK missing)")
    else:
        print(f"⚠️ Unexpected response: {response.status_code}")
except Exception as e:
    print(f"❌ Auth endpoint test failed: {e}")

print("\n" + "=" * 50)
print("\nSUMMARY:")
print("If Firebase is 'degraded' or 'not configured', you need to:")
print("1. Go to Railway Dashboard")
print("2. Add FIREBASE_SERVICE_ACCOUNT_JSON environment variable")
print("3. Paste your Firebase service account JSON (minified)")
print("4. Railway will auto-restart and auth will work!")