import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/chat"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket")
            
            # Wait for connection message
            response = await websocket.recv()
            print(f"Received: {response}")
            
            # Send a test message
            message = {
                "type": "chat",
                "payload": {
                    "content": "test message"
                }
            }
            await websocket.send(json.dumps(message))
            print(f"Sent: {message}")
            
            # Wait for response
            response = await websocket.recv()
            print(f"Received: {response}")
            
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test_websocket())