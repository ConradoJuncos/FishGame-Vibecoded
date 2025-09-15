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
        lobby_code="613MJO",  # Current lobby code
        player_name="TestCommands"
    )
    
    if not success:
        print("❌ Failed to connect")
        return
    
    print("✅ Connected successfully!")
    
    # Test commands
    print("Testing chat message...")
    await client.send_chat_message("Hello from test!")
    
    print("Testing player movement...")  
    await client.move_player(100.0, 200.0)
    
    print("Testing fishing cast...")
    await client.cast_fishing_line(150.0, 250.0)
    
    print("Testing game state request...")
    await client.request_game_state()
    
    # Wait a moment to see responses
    await asyncio.sleep(3)
    
    print("✅ All commands sent successfully!")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_commands())
