#!/usr/bin/env python3
"""
Test Google Ads REST API endpoints directly with curl commands.
This will help identify which endpoints work and which don't.
"""

import os
import subprocess
import json

# You need to set these environment variables or replace with actual values
DEVELOPER_TOKEN = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", "YOUR_DEV_TOKEN")
ACCESS_TOKEN = os.getenv("GOOGLE_ADS_ACCESS_TOKEN", "YOUR_ACCESS_TOKEN")
CUSTOMER_ID = os.getenv("GOOGLE_ADS_CUSTOMER_ID", "YOUR_CUSTOMER_ID")

def test_endpoint(name, method, url, data=None):
    """Test a single endpoint."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Method: {method}")
    print(f"URL: {url}")
    print('-'*60)
    
    cmd = [
        "curl", "-X", method,
        url,
        "-H", f"Authorization: Bearer {ACCESS_TOKEN}",
        "-H", f"developer-token: {DEVELOPER_TOKEN}",
        "-H", "Content-Type: application/json",
        "-s", "-o", "-", "-w", "\nHTTP_CODE:%{http_code}"
    ]
    
    if data:
        cmd.extend(["-d", json.dumps(data)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout
        
        # Extract HTTP code
        if "HTTP_CODE:" in output:
            parts = output.split("HTTP_CODE:")
            response_body = parts[0]
            http_code = parts[1].strip()
            
            print(f"Status: {http_code}")
            
            if http_code == "200":
                print("✅ SUCCESS!")
                try:
                    data = json.loads(response_body)
                    print(f"Response preview: {json.dumps(data, indent=2)[:500]}")
                except:
                    print(f"Response: {response_body[:500]}")
            else:
                print(f"❌ FAILED with {http_code}")
                print(f"Response: {response_body[:500]}")
        else:
            print("Error: Could not get HTTP code")
            print(f"Output: {output[:500]}")
            
    except Exception as e:
        print(f"Error running curl: {e}")

def main():
    print("="*60)
    print("GOOGLE ADS REST API ENDPOINT TESTS")
    print("="*60)
    
    if DEVELOPER_TOKEN == "YOUR_DEV_TOKEN":
        print("\n⚠️ WARNING: Set environment variables first:")
        print("export GOOGLE_ADS_DEVELOPER_TOKEN='your-token'")
        print("export GOOGLE_ADS_ACCESS_TOKEN='your-oauth-token'")
        print("export GOOGLE_ADS_CUSTOMER_ID='your-customer-id'")
        print("\nOr edit this script with actual values.")
        return
    
    # Test different API versions
    for version in ["v17", "v18", "v19", "v20", "v21"]:
        test_endpoint(
            f"List Accessible Customers ({version})",
            "GET",
            f"https://googleads.googleapis.com/{version}/customers:listAccessibleCustomers"
        )
    
    # Test searchStream with different versions
    if CUSTOMER_ID != "YOUR_CUSTOMER_ID":
        query = {
            "query": "SELECT customer.id, customer.descriptive_name FROM customer LIMIT 1"
        }
        
        for version in ["v17", "v18"]:
            test_endpoint(
                f"SearchStream ({version})",
                "POST",
                f"https://googleads.googleapis.com/{version}/customers/{CUSTOMER_ID}/googleAds:searchStream",
                query
            )
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("Check which endpoints returned 200 OK above.")
    print("Those are the working endpoints for your account.")

if __name__ == "__main__":
    main()