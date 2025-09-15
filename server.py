#!/usr/bin/env python3
"""
Fishing Game - Multiplayer Server
A secure WebSocket server for a 2D fishing game with lobby system and spam protection.
"""

import asyncio
import websockets
import json
import random
import string
import time
from typing import Dict, Set, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple rate limiter to prevent spam"""
    def __init__(self, max_messages: int = 10, window_seconds: int = 1):
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self.message_times: Dict[str, list] = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to send a message (not rate limited)"""
        current_time = time.time()
        
        if client_id not in self.message_times:
            self.message_times[client_id] = []
        
        # Clean old messages outside the window
        self.message_times[client_id] = [
            msg_time for msg_time in self.message_times[client_id]
            if current_time - msg_time < self.window_seconds
        ]
        
        # Check if under limit
        if len(self.message_times[client_id]) >= self.max_messages:
            return False
        
        # Add current message time
        self.message_times[client_id].append(current_time)
        return True
    
    def remove_client(self, client_id: str):
        """Remove client from rate limiter"""
        if client_id in self.message_times:
            del self.message_times[client_id]

class GameServer:
    """Main game server handling lobby and client connections"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.lobby_code = self._generate_lobby_code()
        self.clients: Dict[Any, str] = {}  # websocket -> client_id
        self.rate_limiter = RateLimiter(max_messages=15, window_seconds=1)  # 15 messages per second max
        self.game_state = {
            "players": {},
            "game_started": False
        }
    
    def _generate_lobby_code(self) -> str:
        """Generate a random 6-character lobby code"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    async def register_client(self, websocket: Any, client_data: dict) -> bool:
        """Register a new client after lobby code verification"""
        try:
            provided_code = client_data.get("lobby_code", "").strip().upper()
            player_name = client_data.get("player_name", f"Player_{len(self.clients) + 1}")
            
            # Validate lobby code
            if provided_code != self.lobby_code:
                await self.send_message(websocket, {
                    "type": "error",
                    "message": "Invalid lobby code"
                })
                return False
            
            # Check if server is full (max 2 players for now)
            if len(self.clients) >= 2:
                await self.send_message(websocket, {
                    "type": "error",
                    "message": "Lobby is full"
                })
                return False
            
            # Generate unique client ID
            client_id = f"client_{len(self.clients) + 1}_{int(time.time())}"
            self.clients[websocket] = client_id
            
            # Add player to game state
            self.game_state["players"][client_id] = {
                "name": player_name,
                "score": 0,
                "position": {"x": 0, "y": 0},
                "connected_at": time.time()
            }
            
            # Send welcome message
            await self.send_message(websocket, {
                "type": "welcome",
                "client_id": client_id,
                "player_name": player_name,
                "lobby_code": self.lobby_code
            })
            
            # Notify other players
            await self.broadcast_message({
                "type": "player_joined",
                "player_name": player_name,
                "client_id": client_id,
                "total_players": len(self.clients)
            }, exclude=websocket)
            
            logger.info(f"Client {client_id} ({player_name}) joined the lobby")
            return True
            
        except Exception as e:
            logger.error(f"Error registering client: {e}")
            return False
    
    async def unregister_client(self, websocket: Any):
        """Unregister a client when they disconnect"""
        if websocket in self.clients:
            client_id = self.clients[websocket]
            player_name = self.game_state["players"].get(client_id, {}).get("name", "Unknown")
            
            # Remove from tracking
            del self.clients[websocket]
            if client_id in self.game_state["players"]:
                del self.game_state["players"][client_id]
            
            self.rate_limiter.remove_client(client_id)
            
            # Notify other players
            await self.broadcast_message({
                "type": "player_left",
                "player_name": player_name,
                "client_id": client_id,
                "total_players": len(self.clients)
            })
            
            logger.info(f"Client {client_id} ({player_name}) left the lobby")
    
    async def send_message(self, websocket: Any, message: dict):
        """Send a JSON message to a specific client"""
        try:
            await websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Attempted to send message to closed connection")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def broadcast_message(self, message: dict, exclude: Optional[Any] = None):
        """Broadcast a JSON message to all connected clients"""
        if not self.clients:
            return
        
        disconnected = []
        for websocket in self.clients:
            if websocket != exclude:
                try:
                    await websocket.send(json.dumps(message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected.append(websocket)
                except Exception as e:
                    logger.error(f"Error broadcasting to client: {e}")
                    disconnected.append(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected:
            await self.unregister_client(websocket)
    
    async def handle_message(self, websocket: Any, message: dict):
        """Handle incoming messages from clients"""
        client_id = self.clients.get(websocket)
        if not client_id:
            return
        
        # Rate limiting check
        if not self.rate_limiter.is_allowed(client_id):
            await self.send_message(websocket, {
                "type": "error",
                "message": "Rate limit exceeded. Slow down!"
            })
            logger.warning(f"Rate limit exceeded for client {client_id}")
            return
        
        message_type = message.get("type", "unknown")
        
        try:
            if message_type == "ping":
                await self.send_message(websocket, {"type": "pong"})
            
            elif message_type == "get_game_state":
                await self.send_message(websocket, {
                    "type": "game_state",
                    "state": self.game_state
                })
            
            elif message_type == "player_action":
                # Handle game actions (e.g., movement, fishing)
                action_data = message.get("data", {})
                await self.handle_player_action(websocket, client_id, action_data)
            
            elif message_type == "chat_message":
                # Handle chat messages
                chat_text = message.get("text", "").strip()
                if chat_text and len(chat_text) <= 200:  # Basic validation
                    player_name = self.game_state["players"][client_id]["name"]
                    await self.broadcast_message({
                        "type": "chat_message",
                        "player_name": player_name,
                        "client_id": client_id,
                        "text": chat_text,
                        "timestamp": time.time()
                    })
            
            else:
                logger.warning(f"Unknown message type '{message_type}' from client {client_id}")
                
        except Exception as e:
            logger.error(f"Error handling message from client {client_id}: {e}")
            await self.send_message(websocket, {
                "type": "error",
                "message": "Server error processing your request"
            })
    
    async def handle_player_action(self, websocket: Any, client_id: str, action_data: dict):
        """Handle player game actions (to be extended with game logic)"""
        action_type = action_data.get("action", "")
        
        if action_type == "move":
            # Update player position
            new_x = action_data.get("x", 0)
            new_y = action_data.get("y", 0)
            
            # Basic bounds checking (extend as needed)
            new_x = max(0, min(800, new_x))  # Assuming 800px width
            new_y = max(0, min(600, new_y))  # Assuming 600px height
            
            self.game_state["players"][client_id]["position"] = {"x": new_x, "y": new_y}
            
            # Broadcast position update
            await self.broadcast_message({
                "type": "player_moved",
                "client_id": client_id,
                "position": {"x": new_x, "y": new_y}
            })
        
        elif action_type == "cast_line":
            # Handle fishing action
            cast_x = action_data.get("x", 0)
            cast_y = action_data.get("y", 0)
            
            await self.broadcast_message({
                "type": "player_cast_line",
                "client_id": client_id,
                "cast_position": {"x": cast_x, "y": cast_y}
            })
        
        # Add more game actions as needed
    
    async def handle_client(self, websocket: Any, path: str = ""):
        """Handle a client connection"""
        client_registered = False
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    # First message should be registration
                    if not client_registered:
                        if data.get("type") == "join_lobby":
                            client_registered = await self.register_client(websocket, data)
                            if not client_registered:
                                await websocket.close(code=1008, reason="Registration failed")
                                return
                        else:
                            await self.send_message(websocket, {
                                "type": "error",
                                "message": "First message must be join_lobby"
                            })
                            await websocket.close(code=1008, reason="Invalid handshake")
                            return
                    else:
                        await self.handle_message(websocket, data)
                        
                except json.JSONDecodeError:
                    logger.warning("Received invalid JSON from client")
                    await self.send_message(websocket, {
                        "type": "error",
                        "message": "Invalid JSON format"
                    })
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected")
        except Exception as e:
            logger.error(f"Error in client handler: {e}")
        finally:
            await self.unregister_client(websocket)
    
    async def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"Starting Fishing Game Server...")
        logger.info(f"Lobby Code: {self.lobby_code}")
        logger.info(f"Server will run on {self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info("Server is running! Waiting for players...")
            await asyncio.Future()  # Run forever

# Main execution
if __name__ == "__main__":
    server = GameServer(host="localhost", port=8765)
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
