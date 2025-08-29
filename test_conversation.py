#!/usr/bin/env python3
"""Test conversational flow"""

import asyncio
import websockets
import json

async def test_conversation():
    uri = "ws://localhost:8000/ws/chat"
    
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")
        
        # Step 1: Analyze a domain
        print("\n1. Sending domain for analysis...")
        await websocket.send(json.dumps({
            "type": "chat",
            "payload": {
                "content": "stripe.com"
            }
        }))
        
        # Receive responses until analysis is complete
        analysis_complete = False
        while not analysis_complete:
            response = await websocket.recv()
            data = json.loads(response)
            
            if data["type"] == "analysis_update":
                print(f"   Analysis: {data['payload']['message']}")
                if data['payload'].get('status') == 'complete':
                    analysis_complete = True
            elif data["type"] == "chat":
                print(f"   Response: {data['payload']['content'][:100]}...")
                analysis_complete = True
        
        # Wait a moment
        await asyncio.sleep(1)
        
        # Step 2: Ask about forms
        print("\n2. Asking about forms...")
        await websocket.send(json.dumps({
            "type": "chat",
            "payload": {
                "content": "tell me about the forms"
            }
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        if data["type"] == "chat":
            print(f"   Response: {data['payload']['content'][:200]}...")
        
        # Wait a moment
        await asyncio.sleep(1)
        
        # Step 3: Ask about pricing
        print("\n3. Asking about pricing...")
        await websocket.send(json.dumps({
            "type": "chat",
            "payload": {
                "content": "what about pricing?"
            }
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        if data["type"] == "chat":
            print(f"   Response: {data['payload']['content'][:200]}...")
        
        # Step 4: Ask for quick wins
        print("\n4. Asking for quick wins...")
        await websocket.send(json.dumps({
            "type": "chat",
            "payload": {
                "content": "show me quick wins"
            }
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        if data["type"] == "chat":
            print(f"   Response: {data['payload']['content'][:200]}...")
        
        print("\n✅ Conversational flow test complete!")

if __name__ == "__main__":
    asyncio.run(test_conversation())