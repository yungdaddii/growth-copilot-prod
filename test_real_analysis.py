#!/usr/bin/env python3
"""Test what data we're actually getting from analysis."""

import asyncio
import json
import websockets
import uuid
import ssl

async def test_analysis(domain):
    session_id = str(uuid.uuid4())
    uri = f"wss://growth-copilot-prod-production.up.railway.app/ws/chat?session_id={session_id}"
    
    print(f"Testing analysis for: {domain}")
    print("=" * 50)
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        async with websockets.connect(uri, ssl=ssl_context) as ws:
            # Wait for connection
            await ws.recv()
            
            # Send analysis request
            message = {
                "type": "chat",
                "payload": {
                    "content": f"analyze {domain}",
                    "message_id": str(uuid.uuid4())
                }
            }
            
            await ws.send(json.dumps(message))
            
            # Collect all messages
            updates = []
            final_response = None
            
            while True:
                try:
                    resp = await asyncio.wait_for(ws.recv(), timeout=60.0)
                    data = json.loads(resp)
                    
                    if data.get('type') == 'analysis_update':
                        payload = data.get('payload', {})
                        updates.append(f"[{payload.get('progress')}%] {payload.get('message')}")
                        
                    elif data.get('type') == 'chat':
                        final_response = data.get('payload', {}).get('content', '')
                        break
                        
                except asyncio.TimeoutError:
                    print("Timeout!")
                    break
            
            # Print progress updates
            print("\nProgress Updates:")
            for update in updates:
                print(f"  {update}")
            
            # Analyze response content
            if final_response:
                print("\nResponse Analysis:")
                print("-" * 40)
                
                # Check for real data indicators
                checks = {
                    "Has specific numbers": any(char.isdigit() for char in final_response),
                    "Mentions PageSpeed": "pagespeed" in final_response.lower() or "performance" in final_response.lower(),
                    "Mentions competitors": "competitor" in final_response.lower(),
                    "Has AI search info": "ai search" in final_response.lower() or "gptbot" in final_response.lower(),
                    "Has actionable fixes": "fix" in final_response.lower() or "recommend" in final_response.lower(),
                    "Shows real metrics": "score" in final_response.lower() or "%" in final_response,
                }
                
                for check, result in checks.items():
                    status = "✅" if result else "❌"
                    print(f"{status} {check}")
                
                # Show first 500 chars of response
                print("\nResponse Preview:")
                print("-" * 40)
                print(final_response[:500])
                
                # Look for specific data points
                print("\nData Points Found:")
                print("-" * 40)
                
                lines = final_response.split('\n')
                for line in lines:
                    if any(keyword in line.lower() for keyword in ['score', 'time', 'missing', 'blocking', '%', 'visitors']):
                        print(f"  • {line.strip()[:100]}")
                
    except Exception as e:
        print(f"Error: {e}")

async def main():
    # Test multiple domains
    domains = ["stripe.com", "mirantis.com"]
    
    for domain in domains:
        await test_analysis(domain)
        print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())