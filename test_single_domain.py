#!/usr/bin/env python3
"""Test WebSocket with a single domain analysis."""

import asyncio
import json
import websockets
import uuid

async def test_single_domain():
    """Test WebSocket connection with a single domain."""
    session_id = str(uuid.uuid4())
    uri = f"ws://localhost:8000/ws/chat?session_id={session_id}"
    
    print(f"Connecting to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            # Wait for connection confirmation
            response = await websocket.recv()
            print(f"📥 Connection confirmed")
            
            # Send a single domain analysis request
            message = {
                "type": "chat",
                "payload": {
                    "content": "analyze stripe.com",
                    "message_id": str(uuid.uuid4())
                }
            }
            
            print(f"📤 Sending: analyze stripe.com")
            await websocket.send(json.dumps(message))
            
            # Wait for responses
            print("⏳ Waiting for analysis...")
            
            updates_received = 0
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=90.0)
                    data = json.loads(response)
                    
                    if data.get('type') == 'typing':
                        print("💬 Bot is typing...")
                    elif data.get('type') == 'analysis_update':
                        payload = data.get('payload', {})
                        updates_received += 1
                        status = payload.get('status', '')
                        message = payload.get('message', '')
                        progress = payload.get('progress', 0)
                        print(f"[{progress}%] {status}: {message}")
                    elif data.get('type') == 'chat':
                        print(f"\n✅ Analysis complete! ({updates_received} progress updates)")
                        content = data.get('payload', {}).get('content', '')
                        
                        # Show response statistics
                        lines = content.split('\n')
                        print(f"Response length: {len(content)} chars, {len(lines)} lines")
                        
                        # Show first part of response
                        print("\n--- Response Preview ---")
                        preview = '\n'.join(lines[:30])
                        print(preview)
                        
                        # Check for key metrics in response
                        if "score" in content.lower():
                            print("\n✅ Response contains scores")
                        if "competitor" in content.lower():
                            print("✅ Response contains competitor data")
                        if "recommendation" in content.lower():
                            print("✅ Response contains recommendations")
                        
                        break
                    elif data.get('type') == 'error':
                        error = data.get('payload', {})
                        print(f"❌ Error: {error.get('message', 'Unknown error')}")
                        if error.get('details'):
                            print(f"Details: {error['details'][:500]}")
                        break
                    else:
                        print(f"❓ Unknown message type: {data.get('type')}")
                        
                except asyncio.TimeoutError:
                    print("❌ TIMEOUT: No response within 90 seconds")
                    break
                    
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_single_domain())