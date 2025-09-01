#!/usr/bin/env python3
"""
Direct test of Google Ads REST API to understand what's failing.
This will help us understand the exact requirements.
"""

import asyncio
import httpx
import json
import os
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.utils.cache import get_redis


async def test_google_ads_rest_api():
    """Test the Google Ads REST API directly with different configurations."""
    
    print("=" * 60)
    print("GOOGLE ADS REST API DIRECT TEST")
    print("=" * 60)
    
    # Get credentials from Redis (use your actual session ID)
    session_id = "2c683457-3287-43b4-ae89-bdb59efdf57e"  # From your logs
    
    print(f"\n1. Getting credentials for session: {session_id}")
    redis = await get_redis()
    if not redis:
        print("❌ Redis not available")
        return
    
    key = f"google_ads:credentials:{session_id}"
    creds_json = await redis.get(key)
    
    if not creds_json:
        print(f"❌ No credentials found for session {session_id}")
        print("\nChecking all Google Ads keys in Redis...")
        all_keys = await redis.keys("google_ads:*")
        for k in all_keys:
            key_str = k.decode() if isinstance(k, bytes) else k
            print(f"  - {key_str}")
        return
    
    creds = json.loads(creds_json)
    print("✅ Found credentials")
    print(f"  - Has token: {bool(creds.get('token'))}")
    print(f"  - Has refresh token: {bool(creds.get('refresh_token'))}")
    
    # Check if token is expired
    if creds.get('expiry'):
        expiry = datetime.fromisoformat(creds['expiry'])
        is_expired = expiry < datetime.utcnow()
        print(f"  - Token expiry: {expiry} ({'EXPIRED' if is_expired else 'VALID'})")
        
        if is_expired:
            print("\n⚠️ Token is expired, needs refresh")
    
    access_token = creds.get('token')
    developer_token = settings.GOOGLE_ADS_DEVELOPER_TOKEN
    
    print(f"\n2. Configuration:")
    print(f"  - Developer token: {developer_token[:10]}...")
    print(f"  - Access token: {access_token[:20]}..." if access_token else "  - Access token: MISSING")
    
    if not access_token or not developer_token:
        print("\n❌ Missing required tokens")
        return
    
    print("\n3. Testing different API configurations:")
    print("-" * 40)
    
    # Test configurations
    test_cases = [
        {
            "name": "GET with v17",
            "method": "GET",
            "url": "https://googleads.googleapis.com/v17/customers:listAccessibleCustomers",
            "headers": {
                "Authorization": f"Bearer {access_token}",
                "developer-token": developer_token,
                "Content-Type": "application/json"
            }
        },
        {
            "name": "POST with v17 (empty body)",
            "method": "POST", 
            "url": "https://googleads.googleapis.com/v17/customers:listAccessibleCustomers",
            "headers": {
                "Authorization": f"Bearer {access_token}",
                "developer-token": developer_token,
                "Content-Type": "application/json"
            },
            "json": {}
        },
        {
            "name": "GET with v18",
            "method": "GET",
            "url": "https://googleads.googleapis.com/v18/customers:listAccessibleCustomers",
            "headers": {
                "Authorization": f"Bearer {access_token}",
                "developer-token": developer_token,
                "Content-Type": "application/json"
            }
        },
        {
            "name": "Without Content-Type",
            "method": "GET",
            "url": "https://googleads.googleapis.com/v17/customers:listAccessibleCustomers",
            "headers": {
                "Authorization": f"Bearer {access_token}",
                "developer-token": developer_token
            }
        },
        {
            "name": "With login-customer-id (even though not needed)",
            "method": "GET",
            "url": "https://googleads.googleapis.com/v17/customers:listAccessibleCustomers",
            "headers": {
                "Authorization": f"Bearer {access_token}",
                "developer-token": developer_token,
                "Content-Type": "application/json",
                "login-customer-id": ""  # Empty for listAccessibleCustomers
            }
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_cases:
            print(f"\nTest: {test['name']}")
            print(f"  Method: {test['method']}")
            print(f"  URL: {test['url']}")
            
            try:
                if test['method'] == 'GET':
                    response = await client.get(
                        test['url'],
                        headers=test['headers']
                    )
                else:
                    response = await client.post(
                        test['url'],
                        headers=test['headers'],
                        json=test.get('json', {})
                    )
                
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("  ✅ SUCCESS!")
                    data = response.json()
                    print(f"  Response: {json.dumps(data, indent=2)[:500]}")
                    break  # Stop on first success
                elif response.status_code == 401:
                    print("  ❌ 401 Unauthorized - Token issue")
                    print(f"  Error: {response.text[:200]}")
                elif response.status_code == 403:
                    print("  ❌ 403 Forbidden - Permission or developer token issue")
                    print(f"  Error: {response.text[:200]}")
                elif response.status_code == 404:
                    print("  ❌ 404 Not Found - Endpoint doesn't exist")
                    print(f"  Error: {response.text[:200]}")
                else:
                    print(f"  ❌ Unexpected status")
                    print(f"  Error: {response.text[:200]}")
                    
            except Exception as e:
                print(f"  ❌ Exception: {e}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    print("Testing Google Ads REST API directly...")
    asyncio.run(test_google_ads_rest_api())