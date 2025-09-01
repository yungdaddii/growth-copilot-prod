#!/usr/bin/env python3
"""
Test if the method override is working correctly.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.integrations.google_ads.google_ads_rest_api_client import GoogleAdsRESTAPIClient
from app.integrations.base_integration_client import BaseIntegrationClient


async def test_override():
    """Test if our override is being called."""
    
    print("=" * 60)
    print("TESTING METHOD OVERRIDE")
    print("=" * 60)
    
    # Create an instance
    client = GoogleAdsRESTAPIClient("test_session")
    
    # Check the class hierarchy
    print(f"\nClass: {client.__class__.__name__}")
    print(f"Base classes: {[c.__name__ for c in client.__class__.__bases__]}")
    
    # Check which make_api_request method is bound
    method = client.make_api_request
    print(f"\nMethod: {method}")
    print(f"Method module: {method.__module__}")
    print(f"Method qualname: {method.__qualname__}")
    
    # Check the source
    import inspect
    source = inspect.getsource(method)
    print(f"\nFirst line of method source: {source.split(chr(10))[0]}")
    print(f"Has v2.2 logging: {'v2.2' in source}")
    
    # Check API version
    print(f"\nAPI_VERSION: {client.API_VERSION}")
    print(f"API_BASE_URL: {client.API_BASE_URL}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS:")
    if "v2.2" in source:
        print("✅ Override is working - we have v2.2 logging")
    else:
        print("❌ Override NOT working - base class method is being used")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_override())