#!/usr/bin/env python3
"""Test the correct Railway WebSocket endpoint."""

import asyncio
import json
import websockets
import uuid
import ssl

async def test():
    # Your actual Railway backend URL
    session_id = str(uuid.uuid4())
    uri = f"wss://growth-copilot-prod-production.up.railway.app/ws/chat?session_id={session_id}"
    
    print(f"Testing Railway WebSocket at: {uri}")
    
    # Skip SSL verification for testing
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        async with websockets.connect(uri, ssl=ssl_context) as ws:
            print("✅ Connected to Railway backend!")
            
            # Wait for connection confirmation
            try:
                resp = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(resp)
                print(f"✅ Got connection confirmation: {data.get('type')}")
            except asyncio.TimeoutError:
                print("⚠️ No connection confirmation (but connected)")
            
            # Send test message
            message = {
                "type": "chat",
                "payload": {
                    "content": "test websocket connection",
                    "message_id": str(uuid.uuid4())
                }
            }
            
            print("📤 Sending test message...")
            await ws.send(json.dumps(message))
            
            # Wait for response
            print("⏳ Waiting for response...")
            response_count = 0
            
            while response_count < 10:  # Wait for up to 10 messages
                try:
                    resp = await asyncio.wait_for(ws.recv(), timeout=30.0)
                    data = json.loads(resp)
                    response_count += 1
                    
                    if data.get('type') == 'error':
                        error = data.get('payload', {})
                        print(f"\n❌ ERROR from backend:")
                        print(f"Message: {error.get('message')}")
                        
                        # Check for specific database errors
                        details = error.get('details', '')
                        if 'column' in details and 'does not exist' in details:
                            print("\n🔴 DATABASE SCHEMA ISSUE!")
                            print("The Supabase migration needs to be run.")
                            print("Missing column in database.")
                        elif 'relation' in details and 'does not exist' in details:
                            print("\n🔴 DATABASE TABLE MISSING!")
                            print("A required table doesn't exist.")
                        
                        print(f"\nDetails: {details[:500]}")
                        break
                        
                    elif data.get('type') == 'chat':
                        print("\n✅✅ SUCCESS! Got chat response!")
                        content = data.get('payload', {}).get('content', '')
                        print(f"Response preview: {content[:200]}...")
                        print("\n🎉 WebSocket is working! The migration fixed it!")
                        break
                        
                    elif data.get('type') == 'typing':
                        print("💬 Bot is typing... (good sign!)")
                        
                    elif data.get('type') == 'analysis_update':
                        payload = data.get('payload', {})
                        print(f"📊 Progress: {payload.get('message')}")
                    
                    else:
                        print(f"📥 Received: {data.get('type')}")
                        
                except asyncio.TimeoutError:
                    print("\n❌ TIMEOUT after 30 seconds")
                    print("Possible issues:")
                    print("1. Database migration not run on Supabase")
                    print("2. Redis connection issues")
                    print("3. OpenAI API key issues")
                    break
                    
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ WebSocket connection rejected: {e}")
        print("The backend might not have the /ws/chat endpoint")
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test())