#!/usr/bin/env python3
"""
Test the Enhanced NLP via API
Run this after starting Docker Compose
"""

import requests
import json
import time

def test_enhanced_nlp():
    """Test the enhanced NLP endpoint"""
    
    print("\n" + "="*60)
    print("Testing Enhanced NLP API")
    print("="*60)
    
    # Check if server is running
    try:
        health = requests.get("http://localhost:8000/health")
        print(f"✅ Server is healthy: {health.json()}")
    except:
        print("❌ Server not running. Start with: docker-compose up")
        return
    
    # Check enhanced NLP status
    print("\n1. Checking Enhanced NLP status...")
    try:
        status = requests.get("http://localhost:8000/api/test/test-enhanced-status")
        status_data = status.json()
        print(f"   Enhanced Available: {status_data.get('enhanced_available')}")
        print(f"   Has Context: {status_data.get('has_context')}")
        print(f"   Has Enhanced NLP: {status_data.get('has_enhanced_nlp')}")
    except Exception as e:
        print(f"❌ Status check failed: {e}")
    
    # Test with a simple domain
    print("\n2. Testing with example.com...")
    test_data = {
        "domain": "example.com",
        "use_enhanced": True
    }
    
    try:
        print("   Sending request (this may take 30-60 seconds)...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8000/api/test/test-enhanced-nlp",
            json=test_data,
            timeout=120
        )
        
        elapsed = time.time() - start_time
        print(f"   Response received in {elapsed:.1f} seconds")
        
        result = response.json()
        
        if result.get("success"):
            print(f"✅ Test successful!")
            print(f"   Enhanced Used: {result.get('enhanced_used')}")
            print(f"   Response Length: {len(result.get('response', ''))} chars")
            
            # Show first 500 chars of response
            response_text = result.get('response', '')[:500]
            print(f"\n   Response Preview:")
            print("-"*40)
            print(response_text)
            print("-"*40)
            
            # Check response quality
            if len(result.get('response', '')) < 100:
                print("⚠️  Response seems too short")
            
            if "specific" not in response_text.lower() and len(response_text) > 50:
                print("⚠️  Response might be generic")
            
            # Show metadata
            metadata = result.get('metadata', {})
            if metadata:
                print(f"\n   Metadata: {json.dumps(metadata, indent=2)[:200]}...")
        else:
            print(f"❌ Test failed: {result.get('error')}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>120 seconds)")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("\n" + "="*60)
    print("Test Complete")
    print("="*60)

if __name__ == "__main__":
    test_enhanced_nlp()