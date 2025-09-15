#!/usr/bin/env python3
"""
Test Connection Script
Simple automated test to verify client-server connection and fishing functionality.
"""

import asyncio
import websockets
import json
import logging
import time
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Fish rarity configuration
FISH_TYPES = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
FISH_PROBABILITIES = [0.4, 0.2, 0.15, 0.12, 0.08, 0.03, 0.02]  # Probabilities that sum to 1.0

def catch_fish():
    """Generate a random fish based on rarity probabilities"""
    return random.choices(FISH_TYPES, weights=FISH_PROBABILITIES)[0]

def trigger_excitement():
    """Trigger the excitement mark (!) - placeholder for character window integration"""
    print("🎣 FISH CAUGHT! (!) - Character should show excitement mark!")
    
    # Try to trigger excitement in character window via simple file signal
    # This is a simple inter-process communication method
    try:
        with open("fish_caught_signal.tmp", "w") as f:
            f.write(str(time.time()))
    except:
        pass  # Ignore if file can't be written

async def fishing_loop(websocket, fishing_duration=10):
    """
    Fishing loop that checks every second for fish catch (5% chance)
    
    Args:
        websocket: The websocket connection
        fishing_duration: How long to fish in seconds
    """
    print(f"🎣 Starting fishing for {fishing_duration} seconds...")
    
    # Send start fishing message
    start_fishing_msg = {
        "type": "player_action",
        "data": {
            "action": "start_fishing"
        }
    }
    await websocket.send(json.dumps(start_fishing_msg))
    
    for second in range(fishing_duration):
        await asyncio.sleep(1)  # Wait 1 second
        
        # 5% chance to catch a fish each second
        if random.random() < 0.05:
            caught_fish = catch_fish()
            print(f"🐟 Fish caught: {caught_fish}")
            trigger_excitement()
            
            # Optionally send fish catch to server (if server supports it)
            fish_catch_msg = {
                "type": "player_action", 
                "data": {
                    "action": "fish_caught",
                    "fish_type": caught_fish
                }
            }
            await websocket.send(json.dumps(fish_catch_msg))
        else:
            print(f"⏰ Fishing... ({second + 1}s) - No fish yet")
    
    # Send stop fishing message
    stop_fishing_msg = {
        "type": "player_action",
        "data": {
            "action": "stop_fishing"
        }
    }
    await websocket.send(json.dumps(stop_fishing_msg))
    print("🎣 Fishing session ended.")

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
                "text": "Hello from fishing test script!"
            }
            await websocket.send(json.dumps(chat_msg))
            
            # Start fishing loop (10 seconds of fishing)
            print("Starting fishing test...")
            await fishing_loop(websocket, fishing_duration=10)
            
            # Listen for server messages
            print("Listening for server messages...")
            for i in range(5):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    print(f"Received: {data.get('type', 'unknown')} - {data}")
                except asyncio.TimeoutError:
                    print("No message received (timeout)")
                    break
            
            print("✅ Fishing test completed successfully!")
            
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
