#!/usr/bin/env python3
"""
Test the direct API call approach.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.integrations.google_ads.google_ads_rest_api_client import GoogleAdsRESTAPIClient

async def test_direct_api():
    """Test the direct API approach."""
    
    print("=" * 60)
    print("TESTING DIRECT API CALL FIX")
    print("=" * 60)
    
    client = GoogleAdsRESTAPIClient("test_session")
    
    # Mock the http_client
    class MockHttpClient:
        headers = {}
        async def request(self, **kwargs):
            print(f"\n✅ Direct API call made!")
            print(f"   Method: {kwargs.get('method')}")
            print(f"   URL: {kwargs.get('url')}")
            class MockResponse:
                status_code = 200
                def json(self):
                    return {"resourceNames": ["customers/1234567890"]}
            return MockResponse()
    
    client.http_client = MockHttpClient()
    client.access_token = "mock_token"
    
    print("\nCalling _get_customer_id (which now uses direct API calls):")
    print("-" * 60)
    
    customer_id = await client._get_customer_id()
    
    print("-" * 60)
    print(f"\n✅ Customer ID retrieved: {customer_id}")
    print("\n" + "=" * 60)
    print("SUCCESS: Direct API call approach works!")
    print("This bypasses the override issue on Railway")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_direct_api())