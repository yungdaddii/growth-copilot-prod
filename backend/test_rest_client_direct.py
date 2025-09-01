#!/usr/bin/env python3
"""
Test the REST client directly to see if the override works.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.integrations.google_ads.google_ads_rest_api_client import GoogleAdsRESTAPIClient

async def test_direct():
    """Test direct instantiation and method call."""
    
    print("=" * 60)
    print("TESTING DIRECT REST CLIENT")
    print("=" * 60)
    
    # Create client
    client = GoogleAdsRESTAPIClient("test_session")
    
    # Check the method
    import inspect
    method = client.make_api_request
    source = inspect.getsource(method)
    
    print(f"\nMethod: {method}")
    print(f"Has v2.2 logging: {'v2.2' in source}")
    
    # Mock the http_client to avoid actual API calls
    class MockHttpClient:
        headers = {}
        async def request(self, **kwargs):
            print(f"MockHttpClient.request called with: {kwargs}")
            class MockResponse:
                status_code = 404
                text = "Mock 404 response"
                def json(self):
                    return {}
            return MockResponse()
    
    client.http_client = MockHttpClient()
    client.access_token = "mock_token"
    
    # Try to call the method
    print("\n" + "=" * 60)
    print("CALLING make_api_request directly:")
    print("=" * 60)
    
    result = await client.make_api_request(
        method="POST",
        endpoint="customers:listAccessibleCustomers",
        json_data={}
    )
    
    print(f"\nResult: {result}")
    print("\n" + "=" * 60)
    print("CHECK THE OUTPUT ABOVE:")
    print("If you see '[Google Ads REST v2.2]' → Override works")
    print("If you see '[google_ads]' → Base class method is used")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_direct())