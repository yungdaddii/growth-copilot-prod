#!/usr/bin/env python3
"""
Test the fixed REST API with GET method.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.integrations.google_ads.google_ads_rest_api_client import GoogleAdsRESTAPIClient

async def test_rest_get():
    """Test the GET method for listAccessibleCustomers."""
    
    print("=" * 60)
    print("TESTING GOOGLE ADS REST API WITH GET METHOD")
    print("=" * 60)
    
    client = GoogleAdsRESTAPIClient("test_session")
    
    # Mock the http_client
    class MockHttpClient:
        headers = {}
        async def request(self, **kwargs):
            print(f"\n✅ REST API call made!")
            print(f"   Method: {kwargs.get('method')}")
            print(f"   URL: {kwargs.get('url')}")
            
            # Check if it's the correct GET request
            if kwargs.get('method') == 'GET' and 'listAccessibleCustomers' in kwargs.get('url', ''):
                print("   ✅ CORRECT: Using GET method for listAccessibleCustomers!")
                class MockResponse:
                    status_code = 200
                    def json(self):
                        return {"resourceNames": ["customers/9876543210"]}
                return MockResponse()
            else:
                print("   ❌ WRONG: Still using POST or wrong endpoint")
                class MockResponse:
                    status_code = 404
                    text = "Not found"
                    def json(self):
                        return {}
                return MockResponse()
    
    client.http_client = MockHttpClient()
    client.access_token = "mock_token"
    
    print("\nCalling _get_customer_id with fixed GET method:")
    print("-" * 60)
    
    customer_id = await client._get_customer_id()
    
    print("-" * 60)
    
    if customer_id and customer_id != "1234567890":  # Not the mock ID
        print(f"\n✅ SUCCESS: Real customer ID retrieved: {customer_id}")
        print("The GET method fix works!")
    else:
        print(f"\n❌ FAILED: Got mock/fallback ID: {customer_id}")
        print("The fix didn't work")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_rest_get())