#!/usr/bin/env python3
"""
Direct test of Google Ads API endpoints to determine what actually works.
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_google_ads_endpoints():
    """Test what actually works with Google Ads API."""
    
    # These are from your environment
    developer_token = "kmnhAER2lmBDbboSpM1evA"
    
    # You'll need a valid access token - get this from your OAuth flow
    # For testing, you can hardcode it temporarily
    access_token = "YOUR_ACCESS_TOKEN"  # Replace with actual token
    
    print("=" * 60)
    print("GOOGLE ADS API ENDPOINT TEST")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "REST API v17 - GET (original attempt)",
            "method": "GET",
            "url": "https://googleads.googleapis.com/v17/customers:listAccessibleCustomers",
        },
        {
            "name": "REST API v17 - POST (should work)",
            "method": "POST",
            "url": "https://googleads.googleapis.com/v17/customers:listAccessibleCustomers",
            "json": {}
        },
        {
            "name": "REST API v18 - POST",
            "method": "POST",
            "url": "https://googleads.googleapis.com/v18/customers:listAccessibleCustomers",
            "json": {}
        },
        {
            "name": "Discovery API format",
            "method": "POST",
            "url": "https://googleads.googleapis.com/v17/customers/listAccessibleCustomers",
            "json": {}
        },
        {
            "name": "Alternative format without colon",
            "method": "POST",
            "url": "https://googleads.googleapis.com/v17/customers/list",
            "json": {}
        }
    ]
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "developer-token": developer_token,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30) as client:
        for test in test_cases:
            print(f"\n{test['name']}")
            print("-" * 40)
            
            try:
                if test["method"] == "GET":
                    response = await client.get(test["url"], headers=headers)
                else:
                    response = await client.post(
                        test["url"], 
                        headers=headers,
                        json=test.get("json", {})
                    )
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ SUCCESS! This endpoint works!")
                    print(f"Response: {response.text[:200]}")
                elif response.status_code == 401:
                    print("⚠️ 401 - Need valid access token (but endpoint exists!)")
                elif response.status_code == 403:
                    print("⚠️ 403 - Auth issue (but endpoint exists!)")
                elif response.status_code == 404:
                    print("❌ 404 - Endpoint doesn't exist")
                else:
                    print(f"Status: {response.status_code}")
                    print(f"Body: {response.text[:200]}")
                    
            except Exception as e:
                print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS:")
    print("If all return 404, the REST API might not be publicly available")
    print("If POST returns 401/403, then POST is correct but we have auth issues")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_google_ads_endpoints())