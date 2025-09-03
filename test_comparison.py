#!/usr/bin/env python3
"""Test WebSocket with a comparison request."""

import asyncio
import json
import websockets
import uuid

async def test_comparison():
    """Test WebSocket connection with a comparison."""
    session_id = str(uuid.uuid4())
    uri = f"ws://localhost:8000/ws/chat?session_id={session_id}"
    
    print(f"Connecting to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            # Wait for connection confirmation
            response = await websocket.recv()
            print(f"📥 Received: {response}")
            
            # Send a comparison request
            message = {
                "type": "chat",
                "payload": {
                    "content": "compare stripe.com vs square.com",
                    "message_id": str(uuid.uuid4())
                }
            }
            
            print(f"📤 Sending comparison request")
            await websocket.send(json.dumps(message))
            
            # Wait for responses
            print("⏳ Waiting for responses...")
            
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=60.0)
                    data = json.loads(response)
                    
                    if data.get('type') == 'typing':
                        print("💬 Bot is typing...")
                    elif data.get('type') == 'analysis_update':
                        payload = data.get('payload', {})
                        print(f"📊 Update: {payload.get('status')} - {payload.get('message')}")
                    elif data.get('type') == 'chat':
                        print("\n✅ Got response!")
                        content = data.get('payload', {}).get('content', '')
                        print("Response preview:")
                        print(content[:1000] if len(content) > 1000 else content)
                        break
                    elif data.get('type') == 'error':
                        print(f"❌ Error: {data.get('payload', {}).get('details', 'Unknown error')}")
                        break
                    else:
                        print(f"❓ Unknown message type: {data.get('type')}")
                        
                except asyncio.TimeoutError:
                    print("❌ TIMEOUT: No response within 60 seconds")
                    break
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_comparison())