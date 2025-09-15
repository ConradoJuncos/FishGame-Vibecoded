#!/usr/bin/env python3
"""
Test Connection Script
Simple automated test to verify client-server connection works.
"""

import asyncio
import websockets
import json
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_connection():
    """Test the client-server connection"""
    server_host = "localhost"
    server_port = 8765
    
    print("=== Testing Client-Server Connection ===")
    print(f"Connecting to {server_host}:{server_port}")
    
    # First, let's check if server is running
    try:
        # Try to connect
        websocket = await websockets.connect(f"ws://{server_host}:{server_port}")
        print("✅ Successfully connected to server!")
        
        # Get lobby code from user
        lobby_code = input("Enter the lobby code from server console: ").strip().upper()
        player_name = "TestPlayer"
        
        # Send join request
        join_message = {
            "type": "join_lobby",
            "lobby_code": lobby_code,
            "player_name": player_name
        }
        
        print(f"Sending join request with lobby code: {lobby_code}")
        await websocket.send(json.dumps(join_message))
        
        # Wait for response
        response_raw = await websocket.recv()
        response = json.loads(response_raw)
        
        print(f"Server response: {response}")
        
        if response.get("type") == "welcome":
            print("✅ Successfully joined lobby!")
            print(f"Client ID: {response.get('client_id')}")
            print(f"Player Name: {response.get('player_name')}")
            
            # Test sending a chat message
            print("Testing chat message...")
            chat_msg = {
                "type": "chat_message",
                "text": "Hello from test script!"
            }
            await websocket.send(json.dumps(chat_msg))
            
            # Test player movement
            print("Testing player movement...")
            move_msg = {
                "type": "player_action",
                "data": {
                    "action": "move",
                    "x": 100,
                    "y": 200
                }
            }
            await websocket.send(json.dumps(move_msg))
            
            # Test fishing cast
            print("Testing fishing cast...")
            cast_msg = {
                "type": "player_action",
                "data": {
                    "action": "cast_line",
                    "x": 150,
                    "y": 250
                }
            }
            await websocket.send(json.dumps(cast_msg))
            
            # Listen for a few messages
            print("Listening for server messages...")
            for i in range(3):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    print(f"Received: {data.get('type', 'unknown')} - {data}")
                except asyncio.TimeoutError:
                    print("No message received (timeout)")
                    break
            
            print("✅ Connection test completed successfully!")
            
        elif response.get("type") == "error":
            print(f"❌ Server error: {response.get('message')}")
            
        else:
            print(f"❌ Unexpected response: {response}")
        
        await websocket.close()
        
    except ConnectionRefusedError:
        print("❌ Could not connect to server. Is it running?")
        print("Start the server first with: python server.py")
        
    except websockets.exceptions.InvalidURI:
        print("❌ Invalid server URI")
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response: {e}")
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting connection test...")
    asyncio.run(test_connection())
