#!/usr/bin/env python3
"""
Comprehensive troubleshooting for Google Ads API integration.
This will help identify authentication and endpoint issues.
"""

import asyncio
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.utils.cache import get_redis
import httpx
import structlog

logger = structlog.get_logger()

class GoogleAdsTroubleshooter:
    def __init__(self, session_id: str = "test_session"):
        self.session_id = session_id
        self.results = []
        
    async def check_environment(self):
        """Check environment variables."""
        print("\n" + "="*60)
        print("1. ENVIRONMENT VARIABLES CHECK")
        print("="*60)
        
        checks = {
            "GOOGLE_ADS_CLIENT_ID": settings.GOOGLE_ADS_CLIENT_ID,
            "GOOGLE_ADS_CLIENT_SECRET": settings.GOOGLE_ADS_CLIENT_SECRET,
            "GOOGLE_ADS_DEVELOPER_TOKEN": settings.GOOGLE_ADS_DEVELOPER_TOKEN,
        }
        
        for name, value in checks.items():
            if value:
                print(f"✅ {name}: Set (starts with: {str(value)[:20]}...)")
                self.results.append((name, True))
            else:
                print(f"❌ {name}: NOT SET")
                self.results.append((name, False))
        
        return all(v for k, v in self.results if k != "REDIS_URL")
    
    async def check_stored_credentials(self):
        """Check if OAuth credentials are stored in Redis."""
        print("\n" + "="*60)
        print("2. STORED CREDENTIALS CHECK")
        print("="*60)
        
        try:
            redis = await get_redis()
            if not redis:
                print("❌ Redis not available")
                return False
            
            # Check for different possible credential keys
            patterns = [
                f"google_ads:credentials:{self.session_id}",
                f"google_ads:{self.session_id}:credentials",
                f"oauth:google_ads:credentials:{self.session_id}"
            ]
            
            found = False
            for pattern in patterns:
                creds = await redis.get(pattern)
                if creds:
                    print(f"✅ Found credentials at key: {pattern}")
                    creds_data = json.loads(creds)
                    print(f"   - Has token: {bool(creds_data.get('token'))}")
                    print(f"   - Has refresh_token: {bool(creds_data.get('refresh_token'))}")
                    print(f"   - Token preview: {creds_data.get('token', '')[:30]}...")
                    found = True
                    self.stored_creds = creds_data
                    break
            
            if not found:
                print("❌ No stored credentials found")
                print("   You need to complete OAuth flow first")
                
            return found
            
        except Exception as e:
            print(f"❌ Error checking credentials: {e}")
            return False
    
    async def test_api_endpoints(self):
        """Test different API endpoint variations."""
        print("\n" + "="*60)
        print("3. API ENDPOINT TESTS")
        print("="*60)
        
        if not hasattr(self, 'stored_creds'):
            print("⚠️ No credentials to test with")
            return
        
        developer_token = settings.GOOGLE_ADS_DEVELOPER_TOKEN
        access_token = self.stored_creds.get('token')
        
        if not developer_token:
            print("❌ No developer token available")
            return
            
        if not access_token:
            print("❌ No access token available")
            return
        
        # Test variations
        endpoints = [
            # Different versions
            ("v17", "GET", "https://googleads.googleapis.com/v17/customers:listAccessibleCustomers"),
            ("v18", "GET", "https://googleads.googleapis.com/v18/customers:listAccessibleCustomers"),
            ("v19", "GET", "https://googleads.googleapis.com/v19/customers:listAccessibleCustomers"),
            ("v20", "GET", "https://googleads.googleapis.com/v20/customers:listAccessibleCustomers"),
            
            # Try without version (shouldn't work but worth testing)
            ("no-version", "GET", "https://googleads.googleapis.com/customers:listAccessibleCustomers"),
            
            # Try POST (old assumption)
            ("v18-POST", "POST", "https://googleads.googleapis.com/v18/customers:listAccessibleCustomers"),
        ]
        
        async with httpx.AsyncClient() as client:
            for name, method, url in endpoints:
                print(f"\nTesting {name}: {method} {url}")
                print("-" * 40)
                
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "developer-token": developer_token,
                    "Content-Type": "application/json"
                }
                
                try:
                    if method == "GET":
                        response = await client.get(url, headers=headers)
                    else:
                        response = await client.post(url, headers=headers, json={})
                    
                    print(f"   Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"   ✅ SUCCESS! This endpoint works!")
                        data = response.json()
                        print(f"   Response: {json.dumps(data, indent=2)[:200]}")
                        self.working_endpoint = (name, method, url)
                    elif response.status_code == 401:
                        print(f"   ❌ Authentication failed - token might be expired")
                    elif response.status_code == 403:
                        print(f"   ❌ Forbidden - check developer token")
                    elif response.status_code == 404:
                        print(f"   ❌ Not found - wrong endpoint format")
                    else:
                        print(f"   ❌ Failed with: {response.status_code}")
                        print(f"   Response: {response.text[:200]}")
                        
                except Exception as e:
                    print(f"   ❌ Error: {e}")
    
    async def test_with_login_customer_id(self):
        """Test if login-customer-id header is needed."""
        print("\n" + "="*60)
        print("4. LOGIN-CUSTOMER-ID HEADER TEST")
        print("="*60)
        
        if not hasattr(self, 'working_endpoint'):
            print("⚠️ No working endpoint found to test with")
            return
        
        # If we found a working endpoint, test if login-customer-id affects it
        name, method, url = self.working_endpoint
        
        print("Testing with login-customer-id header...")
        # This would need a manager account ID
        # For now, just document that this might be needed
        
        print("\nNOTE: If you're using a manager account, you might need:")
        print('   headers["login-customer-id"] = "YOUR_MANAGER_ACCOUNT_ID"')
    
    async def check_token_validity(self):
        """Check if the OAuth token is still valid."""
        print("\n" + "="*60)
        print("5. TOKEN VALIDITY CHECK")
        print("="*60)
        
        if not hasattr(self, 'stored_creds'):
            print("⚠️ No credentials to check")
            return
        
        # Test the token with Google's tokeninfo endpoint
        access_token = self.stored_creds.get('token')
        if not access_token:
            print("❌ No access token found")
            return
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?access_token={access_token}"
            )
            
            if response.status_code == 200:
                info = response.json()
                print(f"✅ Token is valid")
                print(f"   - Email: {info.get('email', 'N/A')}")
                print(f"   - Scope: {info.get('scope', 'N/A')}")
                print(f"   - Expires in: {info.get('expires_in', 'N/A')} seconds")
                
                # Check if adwords scope is present
                if 'adwords' in info.get('scope', ''):
                    print(f"   ✅ Has Google Ads scope")
                else:
                    print(f"   ❌ Missing Google Ads scope!")
            else:
                print(f"❌ Token is invalid or expired")
                print(f"   You need to re-authenticate through OAuth")
    
    async def run_all_checks(self):
        """Run all troubleshooting checks."""
        print("\n" + "="*60)
        print("GOOGLE ADS API TROUBLESHOOTING")
        print("="*60)
        
        # Check environment
        env_ok = await self.check_environment()
        
        # Check stored credentials
        creds_ok = await self.check_stored_credentials()
        
        if creds_ok:
            # Check token validity
            await self.check_token_validity()
            
            # Test API endpoints
            await self.test_api_endpoints()
            
            # Test additional headers
            await self.test_with_login_customer_id()
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY & RECOMMENDATIONS")
        print("="*60)
        
        if not env_ok:
            print("\n1. ❌ FIX ENVIRONMENT VARIABLES:")
            print("   Set the missing environment variables in your .env file")
            
        if not creds_ok:
            print("\n2. ❌ COMPLETE OAUTH FLOW:")
            print("   You need to authenticate through the OAuth flow first")
            print("   Visit: /api/integrations/google-ads/auth-url")
        
        if hasattr(self, 'working_endpoint'):
            name, method, url = self.working_endpoint
            print(f"\n3. ✅ WORKING ENDPOINT FOUND:")
            print(f"   Use: {method} {url}")
            print(f"   Update the code to use this exact format")
        else:
            print("\n3. ❌ NO WORKING ENDPOINT:")
            print("   - Check if the OAuth token has expired")
            print("   - Verify the developer token is correct")
            print("   - Try completing OAuth flow again")
        
        print("\n" + "="*60)

async def main():
    troubleshooter = GoogleAdsTroubleshooter("2c683457-3287-43b4-ae89-bdb59efdf57e")  # Your session ID
    await troubleshooter.run_all_checks()

if __name__ == "__main__":
    asyncio.run(main())