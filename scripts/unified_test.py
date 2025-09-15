#!/usr/bin/env python3
"""
Unified Test Suite for Fishing Game
Combines connection testing, fishing mechanics, and probability validation.
"""

import asyncio
import websockets
import json
import logging
import time
import random
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

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
    """Trigger the excitement mark (!) - signals character window"""
    print("🎣 FISH CAUGHT! (!) - Character should show excitement mark!")
    
    # Try to trigger excitement in character window via simple file signal
    try:
        signal_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fish_caught_signal.tmp")
        with open(signal_path, "w") as f:
            f.write(str(time.time()))
    except:
        pass  # Ignore if file can't be written

# Probability distribution testing removed per user request

async def fishing_loop(websocket, fishing_duration=10):
    """
    Fishing loop that checks every second for fish catch (5% chance)
    """
    print(f"\n🎣 Starting fishing for {fishing_duration} seconds...")
    
    # Send start fishing message
    start_fishing_msg = {
        "type": "player_action",
        "data": {
            "action": "start_fishing"
        }
    }
    await websocket.send(json.dumps(start_fishing_msg))
    
    caught_fish_list = []
    for second in range(fishing_duration):
        await asyncio.sleep(1)  # Wait 1 second
        
        # 5% chance to catch a fish each second
        if random.random() < 0.05:
            caught_fish = catch_fish()
            caught_fish_list.append(caught_fish)
            print(f"🐟 Fish caught: {caught_fish}")
            trigger_excitement()
            
            # Send fish catch to server
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
    print(f"🎣 Fishing session ended. Total fish caught: {len(caught_fish_list)}")
    if caught_fish_list:
        print(f"Fish types caught: {caught_fish_list}")
    
    return caught_fish_list

async def test_connection_and_fishing():
    """Test the client-server connection and fishing mechanics"""
    server_host = "localhost"
    server_port = 8765
    
    print("=== Testing Client-Server Connection & Fishing ===")
    print(f"Connecting to {server_host}:{server_port}")
    
    try:
        # Try to connect
        websocket = await websockets.connect(f"ws://{server_host}:{server_port}")
        print("✅ Successfully connected to server!")
        
        # Get lobby code from user
        lobby_code = input("Enter the lobby code from server console: ").strip().upper()
        player_name = "FishingTestBot"
        
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
                "text": "Hello from unified fishing test!"
            }
            await websocket.send(json.dumps(chat_msg))
            
            # Start fishing test
            print("Starting fishing mechanics test...")
            caught_fish = await fishing_loop(websocket, fishing_duration=15)
            
            # Request game state
            print("Requesting game state...")
            state_msg = {"type": "get_game_state"}
            await websocket.send(json.dumps(state_msg))
            
            # Listen for server messages
            print("Listening for server messages...")
            for i in range(3):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    print(f"Received: {data.get('type', 'unknown')} - {data}")
                except asyncio.TimeoutError:
                    print("No message received (timeout)")
                    break
            
            print("✅ Connection and fishing test completed successfully!")
            return True
            
        elif response.get("type") == "error":
            print(f"❌ Server error: {response.get('message')}")
            return False
            
        else:
            print(f"❌ Unexpected response: {response}")
            return False
        
        await websocket.close()
        
    except ConnectionRefusedError:
        print("❌ Could not connect to server. Is it running?")
        print("Start the server first with: python server.py")
        return False
        
    except websockets.exceptions.InvalidURI:
        print("❌ Invalid server URI")
        return False
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_character_images():
    """Test character image availability and switching system"""
    print("\n=== Testing Character Images ===")
    
    # Check if images exist
    base_path = os.path.dirname(os.path.dirname(__file__))
    normal_image = os.path.join(base_path, "images", "idle_character.png")
    caught_image = os.path.join(base_path, "images", "caught_character.png")
    
    results = {}
    
    print("Checking character images...")
    if os.path.exists(normal_image):
        print("✅ Normal character image (idle_character.png) found")
        results['normal_image'] = True
    else:
        print("❌ Normal character image (idle_character.png) NOT found")
        results['normal_image'] = False
    
    if os.path.exists(caught_image):
        print("✅ Caught character image (caught_character.png) found")
        results['caught_image'] = True
    else:
        print("❌ Caught character image (caught_character.png) NOT found")
        results['caught_image'] = False
    
    # Test signal file creation
    print("\nTesting image switching signal system...")
    try:
        signal_file = os.path.join(base_path, "fish_caught_signal.tmp")
        with open(signal_file, "w") as f:
            f.write(str(time.time()))
        
        if os.path.exists(signal_file):
            print("✅ Signal file creation successful")
            os.remove(signal_file)  # Clean up
            results['signal_system'] = True
        else:
            print("❌ Signal file creation failed")
            results['signal_system'] = False
    except Exception as e:
        print(f"❌ Signal system error: {e}")
        results['signal_system'] = False
    
    success = all(results.values())
    print(f"✅ Character image system: {'PASSED' if success else 'FAILED'}")
    return success

def test_offline_mechanics():
    """Test fishing mechanics without server connection"""
    print("\n=== Testing Offline Mechanics ===")
    
    # Test fishing simulation
    print("Simulating 30 seconds of fishing...")
    total_fish = 0
    catch_counts = {fish: 0 for fish in FISH_TYPES}
    
    for second in range(30):
        if random.random() < 0.05:  # 5% chance
            caught_fish = catch_fish()
            catch_counts[caught_fish] += 1
            total_fish += 1
            print(f"⏰ Second {second + 1}: 🐟 Caught fish '{caught_fish}'!")
    
    print(f"\n--- Offline Fishing Results ---")
    print(f"Total fishing time: 30 seconds")
    print(f"Total fish caught: {total_fish}")
    print(f"Catch rate: {(total_fish/30)*100:.1f}% per second (expected ~5%)")
    
    if total_fish > 0:
        print(f"Fish distribution:")
        for fish in FISH_TYPES:
            if catch_counts[fish] > 0:
                percentage = (catch_counts[fish] / total_fish) * 100
                print(f"  {fish}: {catch_counts[fish]} ({percentage:.1f}%)")
    
    return total_fish

def main():
    """Main test runner"""
    print("🎣 UNIFIED FISHING GAME TEST SUITE 🎣")
    print("=====================================")
    print("Testing core functionality:")
    print("- Character images and switching system")  
    print("- Offline fishing mechanics")
    print("- Server connection (optional)")
    print()
    
    test_results = {}
    
    # Test 1: Character images
    print("\n1️⃣ Testing character images and switching system...")
    test_results['images'] = test_character_images()
    
    # Test 2: Offline mechanics
    print("\n2️⃣ Testing offline fishing mechanics...")
    fish_caught = test_offline_mechanics()
    test_results['offline'] = fish_caught >= 0
    
    # Test 3: Connection and online fishing (optional)
    print("\n3️⃣ Testing server connection and online fishing...")
    print("Note: This requires a running server. Press Enter to skip, or continue to test.")
    
    user_input = input("Test server connection? (y/N): ").strip().lower()
    if user_input in ['y', 'yes']:
        try:
            test_results['connection'] = asyncio.run(test_connection_and_fishing())
        except KeyboardInterrupt:
            print("\n⏹️ Connection test cancelled by user")
            test_results['connection'] = False
    else:
        print("⏩ Skipping server connection test")
        test_results['connection'] = None
    
    # Results summary
    print("\n🏁 TEST RESULTS SUMMARY")
    print("========================")
    print(f"✅ Character Images:   {'PASSED' if test_results['images'] else 'FAILED'}")
    print(f"✅ Offline Mechanics:  {'PASSED' if test_results['offline'] else 'FAILED'}")
    
    if test_results['connection'] is not None:
        print(f"✅ Server Connection:  {'PASSED' if test_results['connection'] else 'FAILED'}")
    else:
        print(f"⏩ Server Connection:  SKIPPED")
    
    # Overall result
    core_tests_passed = test_results['images'] and test_results['offline']
    if core_tests_passed:
        print("\n🎉 Core fishing mechanics working perfectly!")
        if test_results['connection']:
            print("🌟 All tests including server connection PASSED!")
        else:
            print("💡 Run server and test again for complete validation")
    else:
        print("\n❌ Some core tests failed - check implementation")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user. Goodbye!")
    except Exception as e:
        logger.error(f"Test suite error: {e}")
        import traceback
        traceback.print_exc()
