#!/usr/bin/env python3
"""
Example: Basic Fishing Game Logic Extension
This shows how to extend the networking system with actual game mechanics.
"""

import random
import time
import asyncio
from server import GameServer  # Import our base server

class FishingGameServer(GameServer):
    """Extended game server with fishing mechanics"""
    
    def __init__(self, host="localhost", port=8765):
        super().__init__(host, port)
        
        # Game-specific state
        self.fish = []
        self.game_settings = {
            "world_width": 800,
            "world_height": 600,
            "max_fish": 20,
            "fish_spawn_rate": 0.3,  # Fish per second
            "catch_radius": 30
        }
        
        # Initialize with some fish
        self._spawn_initial_fish()
        
        # Start game loop
        asyncio.create_task(self._game_loop())
    
    def _spawn_initial_fish(self):
        """Spawn initial fish in the world"""
        for _ in range(10):
            self._spawn_fish()
    
    def _spawn_fish(self):
        """Spawn a single fish at random location"""
        fish_types = ["bass", "trout", "salmon", "tuna", "goldfish"]
        fish = {
            "id": f"fish_{len(self.fish) + 1}_{int(time.time())}",
            "type": random.choice(fish_types),
            "x": random.randint(50, self.game_settings["world_width"] - 50),
            "y": random.randint(100, self.game_settings["world_height"] - 50),
            "size": random.uniform(0.5, 2.0),
            "speed": random.uniform(10, 50),
            "direction": random.uniform(0, 360),
            "spawned_at": time.time()
        }
        
        # Different fish have different catch difficulties and scores
        fish_stats = {
            "goldfish": {"difficulty": 0.1, "score": 1},
            "bass": {"difficulty": 0.3, "score": 5},
            "trout": {"difficulty": 0.5, "score": 10},
            "salmon": {"difficulty": 0.7, "score": 20},
            "tuna": {"difficulty": 0.9, "score": 50}
        }
        
        fish.update(fish_stats.get(fish["type"], {"difficulty": 0.5, "score": 10}))
        self.fish.append(fish)
        
        # Notify clients of new fish
        asyncio.create_task(self.broadcast_message({
            "type": "fish_spawned",
            "fish": fish
        }))
    
    def _move_fish(self, delta_time):
        """Update fish positions"""
        for fish in self.fish:
            # Simple movement pattern
            fish["x"] += fish["speed"] * delta_time * random.uniform(-0.5, 0.5)
            fish["y"] += fish["speed"] * delta_time * random.uniform(-0.5, 0.5)
            
            # Keep fish in bounds
            fish["x"] = max(0, min(self.game_settings["world_width"], fish["x"]))
            fish["y"] = max(0, min(self.game_settings["world_height"], fish["y"]))
    
    def _calculate_distance(self, pos1, pos2):
        """Calculate distance between two positions"""
        return ((pos1["x"] - pos2["x"]) ** 2 + (pos1["y"] - pos2["y"]) ** 2) ** 0.5
    
    async def _attempt_catch_fish(self, client_id, cast_position):
        """Attempt to catch fish near the cast position"""
        caught_fish = []
        
        for fish in self.fish[:]:  # Use slice to avoid modification during iteration
            distance = self._calculate_distance(cast_position, fish)
            
            if distance <= self.game_settings["catch_radius"]:
                # Check if catch is successful based on fish difficulty
                catch_chance = max(0.1, 1.0 - fish["difficulty"])
                
                if random.random() < catch_chance:
                    # Successfully caught the fish!
                    caught_fish.append(fish)
                    self.fish.remove(fish)
                    
                    # Update player score
                    if client_id in self.game_state["players"]:
                        self.game_state["players"][client_id]["score"] += fish["score"]
                    
                    # Notify all clients
                    await self.broadcast_message({
                        "type": "fish_caught",
                        "client_id": client_id,
                        "fish": fish,
                        "new_score": self.game_state["players"][client_id]["score"]
                    })
        
        if not caught_fish:
            # No fish caught
            await self.send_message_to_client(client_id, {
                "type": "cast_result",
                "success": False,
                "message": "No fish caught this time!"
            })
    
    async def send_message_to_client(self, client_id, message):
        """Send message to a specific client by ID"""
        for websocket, ws_client_id in self.clients.items():
            if ws_client_id == client_id:
                await self.send_message(websocket, message)
                break
    
    async def handle_player_action(self, websocket, client_id, action_data):
        """Extended player action handler with fishing logic"""
        action_type = action_data.get("action", "")
        
        if action_type == "cast_line":
            # Handle fishing with game logic
            cast_x = action_data.get("x", 0)
            cast_y = action_data.get("y", 0)
            cast_position = {"x": cast_x, "y": cast_y}
            
            # Broadcast the cast action
            await self.broadcast_message({
                "type": "player_cast_line",
                "client_id": client_id,
                "cast_position": cast_position
            })
            
            # Attempt to catch fish
            await self._attempt_catch_fish(client_id, cast_position)
        
        else:
            # Use parent class for other actions
            await super().handle_player_action(websocket, client_id, action_data)
    
    async def _game_loop(self):
        """Main game loop for fish AI and spawning"""
        last_time = time.time()
        last_spawn = time.time()
        
        while True:
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time
            
            # Move fish
            self._move_fish(delta_time)
            
            # Spawn new fish occasionally
            if (current_time - last_spawn) > (1.0 / self.game_settings["fish_spawn_rate"]):
                if len(self.fish) < self.game_settings["max_fish"]:
                    self._spawn_fish()
                    last_spawn = current_time
            
            # Broadcast fish positions every 2 seconds
            if int(current_time) % 2 == 0:
                await self.broadcast_message({
                    "type": "fish_update",
                    "fish": self.fish
                })
            
            # Sleep to maintain reasonable tick rate
            await asyncio.sleep(0.1)  # 10 FPS game loop

# Example usage
if __name__ == "__main__":
    import logging
    
    logging.basicConfig(level=logging.INFO)
    server = FishingGameServer(host="localhost", port=8765)
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logging.info("Fishing game server shutting down...")
    except Exception as e:
        logging.error(f"Server error: {e}")
