#!/usr/bin/env python3
"""
Test Google Ads REST API directly to find the correct endpoint format.
"""

import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_google_ads_endpoints():
    """Test different endpoint formats to find the correct one."""
    
    # Get environment variables
    developer_token = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", "kmnhAER2lmBDbboSpM1evA")
    
    # We need an access token - for testing, you'd need to get this from a valid OAuth flow
    # For now, we'll test the endpoint structure
    access_token = "YOUR_ACCESS_TOKEN_HERE"  # Replace with actual token
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "developer-token": developer_token,
        "Content-Type": "application/json"
    }
    
    # Test different endpoint formats
    endpoints = [
        # Format 1: What we're currently trying
        "https://googleads.googleapis.com/v17/customers:listAccessibleCustomers",
        
        # Format 2: With v18 (newer version)
        "https://googleads.googleapis.com/v18/customers:listAccessibleCustomers",
        
        # Format 3: Different path structure
        "https://googleads.googleapis.com/v17/customers/listAccessibleCustomers",
        
        # Format 4: Google's REST discovery format
        "https://googleads.googleapis.com/v17/customers:listAccessibleCustomers",
        
        # Format 5: Alternative without version in path
        "https://googleads.googleapis.com/customers:listAccessibleCustomers"
    ]
    
    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            try:
                print(f"\nTesting: {endpoint}")
                response = await client.get(endpoint, headers=headers)
                print(f"  Status: {response.status_code}")
                if response.status_code == 404:
                    print(f"  404 - Endpoint not found")
                elif response.status_code == 401:
                    print(f"  401 - Auth required (endpoint exists!)")
                elif response.status_code == 403:
                    print(f"  403 - Forbidden (endpoint exists, permission issue)")
                else:
                    print(f"  Response: {response.text[:200]}")
            except Exception as e:
                print(f"  Error: {e}")

if __name__ == "__main__":
    print("Testing Google Ads API endpoint formats...")
    print("=" * 60)
    asyncio.run(test_google_ads_endpoints())