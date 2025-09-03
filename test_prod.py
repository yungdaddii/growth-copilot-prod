#!/usr/bin/env python3
"""Test production WebSocket."""

import asyncio
import json
import websockets
import uuid

async def test():
    # Replace with your Railway URL
    uri = "wss://growthcopilot-production-5851.up.railway.app/ws/chat?session_id=" + str(uuid.uuid4())
    
    print(f"Testing: {uri}")
    
    try:
        async with websockets.connect(uri) as ws:
            print("✅ Connected")
            
            # Get connection confirmation
            resp = await asyncio.wait_for(ws.recv(), timeout=5.0)
            print(f"Got: {json.loads(resp).get('type')}")
            
            # Send test
            await ws.send(json.dumps({
                "type": "chat",
                "payload": {"content": "test", "message_id": str(uuid.uuid4())}
            }))
            
            # Wait for response
            while True:
                resp = await asyncio.wait_for(ws.recv(), timeout=30.0)
                data = json.loads(resp)
                print(f"Type: {data.get('type')}")
                
                if data.get('type') == 'error':
                    print(f"Error: {data.get('payload', {}).get('details', '')[:200]}")
                    break
                elif data.get('type') == 'chat':
                    print("✅ Got response!")
                    break
                    
    except asyncio.TimeoutError:
        print("❌ Timeout - check if database migration was run")
    except Exception as e:
        print(f"❌ {e}")

asyncio.run(test())