# Fishing Game - Multiplayer Networking System

A secure WebSocket-based multiplayer networking system for a 2D fishing game, built with Python.

## Features

### Security
- **Lobby Code System**: Random 6-character codes prevent unauthorized connections
- **Rate Limiting**: Automatic disconnection of spamming clients (15 messages/second limit)
- **Safe Message Handling**: All messages use JSON - no `eval()` or unsafe parsing
- **Input Validation**: Basic validation on all incoming data

### Networking
- **WebSocket Protocol**: More reliable than raw sockets for game networking
- **Structured Messages**: All communication uses JSON format
- **Connection Management**: Automatic cleanup of disconnected clients
- **Error Handling**: Comprehensive error handling and logging

### Game Features (Extensible)
- **Player Management**: Join/leave notifications, player tracking
- **Game State Synchronization**: Shareable game state between clients
- **Movement System**: Player position updates
- **Fishing Actions**: Cast line functionality ready for game logic
- **Chat System**: In-game text communication

## Quick Start

### 1. Start the Server

```bash
# Navigate to the game directory
cd "c:\Users\Conrado\Desktop\FishGame"

# Run the server
C:/Users/Conrado/Desktop/FishGame/.venv/Scripts/python.exe server.py
```

The server will:
- Generate a random lobby code (displayed in console)
- Start listening on `localhost:8765`
- Wait for players to connect

### 2. Connect Clients

```bash
# In a new terminal, run the client
C:/Users/Conrado/Desktop/FishGame/.venv/Scripts/python.exe client.py
```

The client will prompt for:
- **Server host** (default: localhost)
- **Server port** (default: 8765)
- **Lobby code** (get this from the server console)
- **Player name** (your display name)

### 3. Interactive Commands

Once connected, you can use these commands:

- `/chat <message>` - Send a chat message
- `/move <x> <y>` - Move your player to coordinates
- `/cast <x> <y>` - Cast fishing line at coordinates
- `/state` - Request current game state
- `/quit` - Disconnect and exit

## Architecture

### Server (`server.py`)

**Main Components:**
- `GameServer`: Main server class handling connections and game state
- `RateLimiter`: Spam protection with configurable limits
- **Message Types**:
  - `join_lobby`: Client registration with lobby code
  - `player_action`: Game actions (move, cast line, etc.)
  - `chat_message`: Text communication
  - `ping/pong`: Connection keep-alive

**Security Features:**
- Lobby code validation before registration
- Rate limiting (15 messages/second per client)
- JSON-only message parsing
- Input sanitization and bounds checking
- Maximum 2 players per lobby (configurable)

### Client (`client.py`)

**Main Components:**
- `GameClient`: Core client networking class
- `InteractiveClient`: Command-line interface for testing
- **Custom Handlers**: Extensible message handling system

**Features:**
- Automatic reconnection handling
- Threaded input system
- Ping/pong keep-alive
- Custom message handler registration

## Extending for Game Logic

### Adding New Message Types

**Server Side:**
```python
# In GameServer.handle_message()
elif message_type == "new_action":
    # Handle new action
    await self.handle_new_action(websocket, client_id, message)
```

**Client Side:**
```python
# Add custom handler
def handle_new_action(message):
    # Process the action
    pass

client.add_message_handler("new_action", handle_new_action)
```

### Game State Extension

The `game_state` dictionary can be extended with:
```python
self.game_state = {
    "players": {},  # Player data
    "fish": [],     # Fish positions
    "weather": "sunny",
    "time_of_day": "morning",
    "game_started": False
}
```

### Adding Game Logic

Common extensions:
1. **Fish Spawning**: Add fish objects with positions and types
2. **Fishing Mechanics**: Implement catch probability, fish difficulty
3. **Scoring System**: Track catches, competitions, leaderboards
4. **World State**: Weather, time, seasonal effects
5. **Power-ups**: Special abilities, equipment, upgrades

## Configuration

### Server Settings
```python
# In server.py
server = GameServer(
    host="localhost",     # Server host
    port=8765,           # Server port
)

# Rate limiter settings
RateLimiter(
    max_messages=15,     # Messages per window
    window_seconds=1     # Time window
)
```

### Client Settings
```python
# Connection timeout, ping intervals, etc.
# See GameClient.__init__() for options
```

## Network Protocol

### Message Format
All messages use JSON format:
```json
{
    "type": "message_type",
    "data": {
        // Message-specific data
    }
}
```

### Key Message Types

**Connection:**
- `join_lobby`: Initial connection with lobby code
- `welcome`: Server confirmation of connection
- `error`: Error messages

**Game Actions:**
- `player_action`: Player input (move, cast, etc.)
- `player_moved`: Position update broadcast
- `player_cast_line`: Fishing action broadcast

**Communication:**
- `chat_message`: Text messages
- `ping/pong`: Keep-alive

**State:**
- `get_game_state`: Request current state
- `game_state`: Full state response

## Security Notes

1. **No Gameplay Validation**: The system focuses on network security, not anti-cheat
2. **Trusted Players**: Players can send any valid game actions
3. **Malicious Protection**: Prevents random connections and spam attacks
4. **Local Network**: Designed for LAN play or trusted connections

## Development Notes

- **Python 3.8+** required
- **Dependencies**: `websockets`, `asyncio` (standard library)
- **Platform**: Windows/Linux/macOS compatible
- **Threading**: Uses asyncio for networking, threading only for user input
- **Logging**: Comprehensive logging for debugging

## Batch Files (Windows)

For easier startup, use the provided batch files:

- **`start_server.bat`**: Starts the game server
- **`start_client.bat`**: Starts a game client

Simply double-click these files to run them.

## Testing the System

1. **Run the server**: `start_server.bat` or manually with `python server.py`
2. **Note the lobby code** displayed in the server console
3. **Run the character window** (optional): `python scripts/simple_character.py` or `start_floating_character.bat`
4. **Run the client**: `start_client.bat` or manually with `python client.py`
5. **Connect** using the lobby code from step 2
6. **Test commands**: `/chat Hello!`, `/fish` (start fishing), `/stop` (stop fishing), `/state`

### Fishing Mechanics

The game now includes a realistic fishing system:

**Fish Types & Rarity**:
- `a`: 40% chance (most common)
- `b`: 20% chance
- `c`: 15% chance
- `d`: 12% chance
- `e`: 8% chance
- `f`: 3% chance
- `g`: 2% chance (rarest/legendary)

**Fishing Process**:
- Use `/fish` command to start fishing
- Every second: 5% chance to catch a fish
- When caught, fish rarity is determined by above probabilities
- Character window changes from `idle_character.png` to `caught_character.png` when fish are caught
- Character reverts to normal image after 2 seconds
- Use `/stop` to stop fishing

**Test Scripts**:
```bash
# Unified comprehensive test suite (recommended)
python scripts/unified_test.py
# OR use: run_tests.bat

# Individual test scripts:
python scripts/test_connection.py           # Connection and fishing mechanics
python scripts/test_fishing_probabilities.py  # Fish rarity distribution
python scripts/test_commands.py             # Automated command testing
```

## Example with Game Logic

See `fishing_game_example.py` for an extended version that includes:
- Fish spawning and movement
- Catch mechanics with difficulty levels  
- Scoring system
- Real-time fish position updates

This demonstrates how to build actual game features on top of the networking foundation.

## Next Steps

1. **Game Engine Integration**: Connect to pygame, pyglet, or other 2D engine
2. **Graphics**: Add sprite rendering, animations, UI
3. **Game Mechanics**: Implement fishing logic, scoring, progression
4. **Audio**: Sound effects, background music
5. **Polish**: Menus, settings, save system

## Troubleshooting

### "Cannot send message: not connected" Error
- **Fixed**: This was an issue with the initial connection handshake
- **Solution**: Updated client to handle lobby joining properly before setting connected state

### Client Commands Not Working  
- **Issue**: Threading and asyncio event loop conflicts
- **Solution**: Fixed event loop passing between main thread and input thread
- **Test**: Use `test_commands.py` to verify commands work programmatically

### Connection Test Scripts

- **`test_connection.py`**: Interactive test that prompts for lobby code
- **`test_commands.py`**: Automated test that verifies all client commands work

Run these scripts to verify your setup is working correctly.

## Floating Character Window

A draggable, always-on-top character window that displays your fishing character image anywhere on your screen!

### Features:
- **Always on Top**: Stays visible over other windows
- **Draggable**: Click and drag to move anywhere
- **Lightweight**: Minimal resource usage
- **Auto-resize**: Automatically fits your character image
- **Right-click Options**: Toggle always-on-top, transparency, etc.

### Usage:
```bash
# Simple floating character (recommended)
python simple_character.py
# OR double-click: start_floating_character.bat

# Full-featured version with launcher
python floating_character.py
```

### Controls:
- **Left-click + drag**: Move the window (automatically constrained to screen boundaries)
- **Right-click**: Toggle always-on-top (simple version) / Options menu (full version)
- **Double-click**: Close window (simple version)

### Visual Features:
- **Transparent Background**: Only your character image is visible, no white background
- **No Borders**: Clean, borderless appearance
- **Always on Top**: Stays visible over other applications
- **Screen Boundary Protection**: Window cannot be dragged off-screen
- **Dynamic Image Switching**: Changes from `idle_character.png` to `caught_character.png` when fish are caught

Your character images will be displayed as clean floating sprites that you can position anywhere on your screen!

## Project Structure

```
FishGame/
├── 📁 images/                    # Game assets
│   ├── idle_character.png        # Normal character sprite
│   └── caught_character.png      # Excited character sprite
├── 📁 scripts/                   # All test and utility scripts
│   ├── unified_test.py           # 🎯 Comprehensive test suite (recommended)
│   ├── test_connection.py        # Connection and fishing mechanics test
│   ├── test_fishing_probabilities.py  # Fish rarity distribution test
│   ├── test_commands.py          # Automated command testing
│   ├── simple_character.py       # Floating character window (lightweight)
│   ├── floating_character.py     # Advanced character window with features
│   └── fishing_game_example.py   # Extended game logic example
├── 📄 server.py                  # Main game server
├── 📄 client.py                  # Main game client
├── 📄 requirements.txt           # Python dependencies
├── 🚀 start_server.bat          # Launch server
├── 🚀 start_client.bat          # Launch client  
├── 🚀 start_floating_character.bat  # Simple character window
├── 🚀 start_advanced_character.bat  # Advanced character window
├── 🚀 run_tests.bat             # Run unified test suite
└── 📖 README.md                 # This documentation
```

**Quick Start Files:**
- **🎯 `run_tests.bat`**: Run comprehensive tests (recommended first step)
- **🚀 `start_server.bat`**: Launch the game server
- **🚀 `start_client.bat`**: Connect to the game
- **🚀 `start_floating_character.bat`**: Simple character window (fish catching, image switching)
- **🚀 `start_advanced_character.bat`**: Advanced character window (with options menu)

## Status: ✅ WORKING

The networking foundation is complete and ready for your game logic!
