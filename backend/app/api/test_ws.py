from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

router = APIRouter()

@router.websocket("/test")
async def test_websocket(websocket: WebSocket):
    await websocket.accept()
    print("TEST WS: Connection accepted")
    
    try:
        # Send initial message
        await websocket.send_json({
            "type": "connection",
            "payload": {"status": "connected", "message": "Test WebSocket connected"}
        })
        print("TEST WS: Initial message sent")
        
        while True:
            # Echo messages back
            data = await websocket.receive_text()
            print(f"TEST WS: Received: {data}")
            
            message = json.loads(data)
            response = {
                "type": "echo",
                "payload": {
                    "original": message,
                    "echoed_at": "now"
                }
            }
            
            await websocket.send_json(response)
            print(f"TEST WS: Sent echo response")
            
    except WebSocketDisconnect:
        print("TEST WS: Client disconnected")
    except Exception as e:
        print(f"TEST WS: Error: {e}")
        await websocket.close()