#!/usr/bin/env python3
"""
Fishing Game - Multiplayer Client
A secure WebSocket client for connecting to the fishing game server.
"""

import asyncio
import websockets
import json
import threading
import time
import logging
from typing import Optional, Callable, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GameClient:
    """Main game client for connecting to the fishing game server"""
    
    def __init__(self):
        self.websocket: Optional[Any] = None
        self.connected = False
        self.client_id: Optional[str] = None
        self.player_name: Optional[str] = None
        self.lobby_code: Optional[str] = None
        self.game_state = {}
        self.message_handlers = {}
        self.running = False
    
    def add_message_handler(self, message_type: str, handler: Callable):
        """Add a handler for specific message types"""
        self.message_handlers[message_type] = handler
    
    async def connect(self, server_host: str, server_port: int, lobby_code: str, player_name: str) -> bool:
        """Connect to the game server"""
        try:
            uri = f"ws://{server_host}:{server_port}"
            logger.info(f"Connecting to {uri}...")
            
            self.websocket = await websockets.connect(uri)
            
            # Send join lobby request directly (before setting connected=True)
            join_message = {
                "type": "join_lobby",
                "lobby_code": lobby_code.strip().upper(),
                "player_name": player_name.strip()
            }
            
            logger.info("Sending join lobby request...")
            await self.websocket.send(json.dumps(join_message))
            
            # Wait for response
            response_msg = await self.websocket.recv()
            response = json.loads(response_msg)
            
            if response.get("type") == "welcome":
                self.connected = True
                self.client_id = response.get("client_id")
                self.player_name = response.get("player_name")
                self.lobby_code = response.get("lobby_code")
                
                logger.info(f"Successfully connected! Client ID: {self.client_id}")
                logger.info(f"Player Name: {self.player_name}")
                logger.info(f"Lobby Code: {self.lobby_code}")
                
                return True
            
            elif response.get("type") == "error":
                error_msg = response.get("message", "Unknown error")
                logger.error(f"Connection failed: {error_msg}")
                await self.websocket.close()
                return False
            
            else:
                logger.error("Unexpected response from server")
                await self.websocket.close()
                return False
                
        except websockets.exceptions.InvalidURI:
            logger.error("Invalid server URI")
            return False
        except ConnectionRefusedError:
            logger.error("Could not connect to server. Is it running?")
            return False
        except json.JSONDecodeError:
            logger.error("Received invalid JSON from server")
            return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the server"""
        if self.websocket and self.connected:
            self.running = False
            self.connected = False
            await self.websocket.close()
            logger.info("Disconnected from server")
    
    async def send_message(self, message: dict):
        """Send a JSON message to the server"""
        if not self.websocket:
            logger.warning("Cannot send message: no websocket connection")
            return False
        
        if not self.connected:
            logger.warning("Cannot send message: not connected to server")
            return False
        
        try:
            await self.websocket.send(json.dumps(message))
            logger.debug(f"Sent message: {message.get('type', 'unknown')}")
            return True
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Connection closed while sending message")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.connected = False
            return False
    
    async def handle_message(self, message: dict):
        """Handle incoming messages from the server"""
        message_type = message.get("type", "unknown")
        
        # Call custom handler if available
        if message_type in self.message_handlers:
            try:
                self.message_handlers[message_type](message)
            except Exception as e:
                logger.error(f"Error in custom handler for {message_type}: {e}")
        
        # Built-in message handling
        if message_type == "error":
            error_msg = message.get("message", "Unknown error")
            logger.error(f"Server error: {error_msg}")
        
        elif message_type == "player_joined":
            player_name = message.get("player_name", "Unknown")
            total_players = message.get("total_players", 0)
            logger.info(f"Player '{player_name}' joined the game (Total: {total_players})")
        
        elif message_type == "player_left":
            player_name = message.get("player_name", "Unknown")
            total_players = message.get("total_players", 0)
            logger.info(f"Player '{player_name}' left the game (Total: {total_players})")
        
        elif message_type == "game_state":
            self.game_state = message.get("state", {})
            logger.debug("Received game state update")
        
        elif message_type == "player_started_fishing":
            player_name = message.get("player_name", "Unknown")
            logger.info(f"🎣 {player_name} started fishing!")
        
        elif message_type == "player_stopped_fishing":
            player_name = message.get("player_name", "Unknown")
            logger.info(f"🛑 {player_name} stopped fishing")
        
        elif message_type == "fish_caught":
            player_name = message.get("player_name", "Unknown")
            fish_type = message.get("fish_type", "unknown")
            new_score = message.get("new_score", 0)
            logger.info(f"🐟 {player_name} caught a fish '{fish_type}'! Score: {new_score}")
        
        elif message_type == "chat_message":
            player_name = message.get("player_name", "Unknown")
            text = message.get("text", "")
            timestamp = message.get("timestamp", time.time())
            logger.info(f"[CHAT] {player_name}: {text}")
        
        elif message_type == "pong":
            logger.debug("Received pong from server")
        
        else:
            logger.debug(f"Unhandled message type: {message_type}")
    
    async def listen_for_messages(self):
        """Listen for incoming messages from the server"""
        if not self.websocket:
            logger.error("No websocket connection to listen on")
            return
            
        try:
            while self.connected and self.websocket:
                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                    try:
                        data = json.loads(message)
                        await self.handle_message(data)
                    except json.JSONDecodeError:
                        logger.warning("Received invalid JSON from server")
                    except Exception as e:
                        logger.error(f"Error handling message: {e}")
                except asyncio.TimeoutError:
                    # Timeout is normal, just continue listening
                    continue
                except websockets.exceptions.ConnectionClosed:
                    logger.info("Server connection closed")
                    self.connected = False
                    break
                except Exception as e:
                    logger.error(f"Error receiving message: {e}")
                    break
        except Exception as e:
            logger.error(f"Error in message listener: {e}")
        finally:
            self.connected = False
    
    async def ping_server(self):
        """Send periodic ping to keep connection alive"""
        while self.connected and self.running:
            await asyncio.sleep(30)  # Ping every 30 seconds
            if self.connected and self.websocket:
                success = await self.send_message({"type": "ping"})
                if not success:
                    logger.warning("Failed to send ping, connection may be lost")
                    self.connected = False
                    break
    
    async def run(self):
        """Main client loop"""
        if not self.connected:
            logger.error("Cannot run: not connected to server")
            return
        
        self.running = True
        logger.info("Client is running. Type commands to interact...")
        
        # Start background tasks
        listen_task = asyncio.create_task(self.listen_for_messages())
        ping_task = asyncio.create_task(self.ping_server())
        
        try:
            # Wait for either task to complete (usually means disconnection)
            done, pending = await asyncio.wait(
                [listen_task, ping_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel remaining tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.error(f"Error canceling task: {e}")
                
        except Exception as e:
            logger.error(f"Error in client main loop: {e}")
        finally:
            logger.info("Client loop ended")
            self.running = False
            self.connected = False
    
    # Game-specific methods
    async def send_chat_message(self, text: str) -> bool:
        """Send a chat message"""
        return await self.send_message({
            "type": "chat_message",
            "text": text
        })
    
    async def start_fishing(self) -> bool:
        """Start fishing"""
        return await self.send_message({
            "type": "player_action",
            "data": {
                "action": "start_fishing"
            }
        })
    
    async def stop_fishing(self) -> bool:
        """Stop fishing"""
        return await self.send_message({
            "type": "player_action",
            "data": {
                "action": "stop_fishing"
            }
        })
    
    async def request_game_state(self) -> bool:
        """Request current game state from server"""
        return await self.send_message({"type": "get_game_state"})

# Interactive client for testing
class InteractiveClient:
    """Interactive command-line client for testing"""
    
    def __init__(self):
        self.client = GameClient()
        self.input_thread = None
        self.running = False
        self.loop = None
    
    def setup_handlers(self):
        """Setup custom message handlers"""
        def on_game_state(message):
            state = message.get("state", {})
            players = state.get("players", {})
            print(f"\n--- 🎣 Fishing Game State ---")
            print(f"Players online: {len(players)}")
            for client_id, player_data in players.items():
                name = player_data.get("name", "Unknown")
                score = player_data.get("score", 0)
                is_fishing = player_data.get("is_fishing", False)
                fish_caught = player_data.get("fish_caught", [])
                fishing_status = "🎣 FISHING" if is_fishing else "⏸️ Not fishing"
                print(f"  {name}: {fishing_status} | Score: {score} | Fish: {fish_caught}")
            print("----------------------------\n")
        
        self.client.add_message_handler("game_state", on_game_state)
    
    def input_handler(self):
        """Handle user input in a separate thread"""
        print("\n=== Fishing Game Client ===")
        print("Commands:")
        print("  /chat <message>  - Send chat message")
        print("  /fish            - Start fishing")
        print("  /stop            - Stop fishing")
        print("  /state           - Request game state")
        print("  /quit            - Disconnect and quit")
        print("============================\n")
        
        while self.running:
            try:
                command = input().strip()
                if not command:
                    continue
                
                if command.startswith("/chat "):
                    message = command[6:]
                    if self.client.connected and self.loop:
                        asyncio.run_coroutine_threadsafe(
                            self.client.send_chat_message(message),
                            self.loop
                        )
                    else:
                        print("Not connected to server!")
                
                elif command == "/fish":
                    if self.client.connected and self.loop:
                        asyncio.run_coroutine_threadsafe(
                            self.client.start_fishing(),
                            self.loop
                        )
                    else:
                        print("Not connected to server!")
                
                elif command == "/stop":
                    if self.client.connected and self.loop:
                        asyncio.run_coroutine_threadsafe(
                            self.client.stop_fishing(),
                            self.loop
                        )
                    else:
                        print("Not connected to server!")
                
                elif command == "/state":
                    if self.client.connected and self.loop:
                        asyncio.run_coroutine_threadsafe(
                            self.client.request_game_state(),
                            self.loop
                        )
                    else:
                        print("Not connected to server!")
                
                elif command == "/quit":
                    self.running = False
                    if self.loop:
                        asyncio.run_coroutine_threadsafe(
                            self.client.disconnect(),
                            self.loop
                        )
                    break
                
                else:
                    print("Unknown command. Type /quit to exit.")
                    
            except EOFError:
                break
            except Exception as e:
                logger.error(f"Error in input handler: {e}")
    
    async def start_interactive(self):
        """Start interactive client session"""
        # Get connection details
        print("=== Fishing Game Client ===")
        server_host = input("Server host (default: localhost): ").strip() or "localhost"
        
        try:
            server_port = int(input("Server port (default: 8765): ").strip() or "8765")
        except ValueError:
            server_port = 8765
        
        lobby_code = input("Lobby code: ").strip()
        player_name = input("Your player name: ").strip() or f"Player_{int(time.time())}"
        
        # Setup handlers
        self.setup_handlers()
        
        # Connect to server
        if await self.client.connect(server_host, server_port, lobby_code, player_name):
            self.running = True
            self.loop = asyncio.get_running_loop()  # Store the current event loop
            
            # Start input handler thread
            self.input_thread = threading.Thread(target=self.input_handler, daemon=True)
            self.input_thread.start()
            
            # Run client
            await self.client.run()
        else:
            print("Failed to connect to server.")

# Main execution
if __name__ == "__main__":
    interactive_client = InteractiveClient()
    
    try:
        asyncio.run(interactive_client.start_interactive())
    except KeyboardInterrupt:
        logger.info("Client shutting down...")
    except Exception as e:
        logger.error(f"Client error: {e}")
