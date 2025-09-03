#!/usr/bin/env python3
"""Test WebSocket connection and message flow."""

import asyncio
import json
import websockets
import uuid

async def test_websocket():
    """Test WebSocket connection and send a message."""
    session_id = str(uuid.uuid4())
    uri = f"ws://localhost:8000/ws/chat?session_id={session_id}"
    
    print(f"Connecting to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            # Wait for connection confirmation
            response = await websocket.recv()
            print(f"📥 Received: {response}")
            
            # Send a test message
            message = {
                "type": "chat",
                "payload": {
                    "content": "Find revenue leaks on stripe.com",
                    "message_id": str(uuid.uuid4())
                }
            }
            
            print(f"📤 Sending: {json.dumps(message)}")
            await websocket.send(json.dumps(message))
            
            # Wait for response
            print("⏳ Waiting for response...")
            response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            print(f"📥 Response: {response}")
            
            # Parse and display
            data = json.loads(response)
            if data.get('type') == 'chat':
                print("\n✅ SUCCESS! Got chat response:")
                print(data.get('payload', {}).get('content', 'No content')[:500])
            else:
                print(f"\n❓ Got response type: {data.get('type')}")
                print(json.dumps(data, indent=2))
                
    except asyncio.TimeoutError:
        print("❌ TIMEOUT: No response within 30 seconds")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connection closed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())