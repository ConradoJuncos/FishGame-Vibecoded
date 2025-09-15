#!/usr/bin/env python3
"""Simple test to verify client commands work"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client import GameClient

async def test_commands():
    client = GameClient()
    
    # Connect to server
    success = await client.connect(
        server_host="localhost",
        server_port=8765,
        lobby_code="82HMOF",  # Current lobby code
        player_name="TestCommands"
    )
    
    if not success:
        print("❌ Failed to connect")
        return
    
    print("✅ Connected successfully!")
    
    # Test commands
    print("Testing chat message...")
    await client.send_chat_message("Hello from test!")
    
    print("Testing start fishing...")  
    await client.start_fishing()
    
    print("Waiting 10 seconds to see if we catch any fish...")
    await asyncio.sleep(10)
    
    print("Testing game state request...")
    await client.request_game_state()
    
    print("Testing stop fishing...")
    await client.stop_fishing()
    
    # Wait a moment to see responses
    await asyncio.sleep(2)
    
    print("✅ All commands sent successfully!")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_commands())
