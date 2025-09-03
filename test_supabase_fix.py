#!/usr/bin/env python3
"""Test if Supabase migration fixed the issue."""

import asyncio
import json
import websockets
import uuid

async def test():
    # Your Railway backend URL
    uri = "wss://growthcopilot-production-5851.up.railway.app/ws/chat?session_id=" + str(uuid.uuid4())
    
    print("Testing WebSocket after Supabase migration...")
    
    # Skip SSL verification for testing
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        async with websockets.connect(uri, ssl=ssl_context) as ws:
            print("✅ Connected to backend")
            
            # Wait for connection confirmation
            resp = await asyncio.wait_for(ws.recv(), timeout=5.0)
            print("✅ Got connection confirmation")
            
            # Send test message
            await ws.send(json.dumps({
                "type": "chat",
                "payload": {"content": "test after migration", "message_id": str(uuid.uuid4())}
            }))
            print("📤 Sent test message")
            
            # Wait for response
            print("⏳ Waiting for response...")
            while True:
                resp = await asyncio.wait_for(ws.recv(), timeout=30.0)
                data = json.loads(resp)
                
                if data.get('type') == 'error':
                    print(f"❌ Still getting error: {data.get('payload', {}).get('message')}")
                    print("Migration may not have been run yet")
                    break
                elif data.get('type') == 'chat':
                    print("✅✅ SUCCESS! Chat is working!")
                    print("The migration fixed the issue!")
                    break
                elif data.get('type') == 'typing':
                    print("💬 Bot is typing... (good sign!)")
                    
    except asyncio.TimeoutError:
        print("❌ Timeout - migration might not be complete")
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(test())