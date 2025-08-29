#!/usr/bin/env python3
"""Test production deployment"""

import asyncio
import websockets
import json

async def test_websocket():
    """Test WebSocket connection to production"""
    uri = "wss://growth-copilot-prod-production.up.railway.app/ws/chat"
    
    try:
        print("🔌 Connecting to WebSocket...")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected!")
            
            # Send a test message
            test_message = {
                "type": "analyze",
                "content": "https://example.com"
            }
            
            print(f"📤 Sending: {test_message}")
            await websocket.send(json.dumps(test_message))
            
            # Wait for response
            print("⏳ Waiting for response...")
            response = await asyncio.wait_for(websocket.recv(), timeout=10)
            response_data = json.loads(response)
            
            print(f"📥 Received: {json.dumps(response_data, indent=2)[:200]}...")
            print("✅ WebSocket test successful!")
            
    except asyncio.TimeoutError:
        print("⏱️ Timeout waiting for response")
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

# Test basic HTTP endpoints
import requests

def test_http_endpoints():
    """Test HTTP endpoints"""
    base_url = "https://growth-copilot-prod-production.up.railway.app"
    
    print("\n🌐 Testing HTTP endpoints...")
    
    # Test health
    response = requests.get(f"{base_url}/health")
    print(f"  /health: {response.status_code} - {response.json()}")
    
    # Test root
    response = requests.get(f"{base_url}/")
    print(f"  /: {response.status_code} - {response.json()}")
    
    print("✅ HTTP endpoints working!")

if __name__ == "__main__":
    print("🚀 Testing Growth Copilot Production Deployment\n")
    
    # Test HTTP
    test_http_endpoints()
    
    # Test WebSocket
    print("\n📡 Testing WebSocket...")
    asyncio.run(test_websocket())
    
    print("\n✨ All tests complete!")