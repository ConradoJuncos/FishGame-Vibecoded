# 🎣 Fishing Game - Quick Setup Guide

This guide helps you get the fishing game running on any system after cloning the repository.

## 📋 Prerequisites

- **Python 3.8+** installed on your system
- **Git** (to clone the repository)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/FishGame.git
cd FishGame
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Game

#### On Windows:
```cmd
# Start server
start_server.bat

# Start client (in another terminal)
start_client.bat

# Start character window (optional)
start_floating_character.bat

# Run tests
run_tests.bat
```

#### On Linux/Mac:
```bash
# Make scripts executable (first time only)
chmod +x *.sh

# Start server
./start_server.sh

# Start client (in another terminal)
./start_client.sh

# Start character window (optional)
./start_floating_character.sh

# Run tests
./run_tests.sh
```

#### Manual Commands (Works on all systems):
```bash
# Server
python server.py

# Client
python client.py

# Character window
python scripts/simple_character.py

# Tests
python scripts/unified_test.py
```

## 🌐 Multiplayer Setup

### For Local Network Play:
1. **Host**: Start server with `python server.py`
2. **Players**: Connect using host's **local IP** (e.g., `192.168.1.100`)
3. **Port**: Use `8765` (default)

### For Internet Play:
1. **Option A**: Port forward port `8765` on router
2. **Option B**: Use cloud hosting (Replit, Heroku, etc.)

## 🐛 Troubleshooting

### Python Not Found:
- Make sure Python is installed and in your PATH
- Try `python3` instead of `python`

### Module Not Found:
```bash
pip install -r requirements.txt
```

### Permission Denied (Linux/Mac):
```bash
chmod +x *.sh
```

### Character Window Not Showing:
- Make sure `images/idle_character.png` exists
- Install Pillow: `pip install Pillow`

## 📁 Project Structure
```
FishGame/
├── server.py                    # Game server
├── client.py                    # Game client
├── requirements.txt             # Dependencies
├── start_*.bat                  # Windows launchers
├── start_*.sh                   # Linux/Mac launchers
├── images/                      # Character sprites
│   ├── idle_character.png       # Normal state
│   └── caught_character.png     # Excited state
└── scripts/                     # Utilities and tests
    ├── unified_test.py          # Test suite
    ├── simple_character.py      # Character window
    └── ...                      # Other utilities
```

## 🎮 How to Play
1. Run server and note the **lobby code**
2. Run client and enter the **lobby code**
3. Use `/fish` to start fishing
4. Use `/stop` to stop fishing
5. Watch character window change when you catch fish!

## 🤝 Contributing
Feel free to submit issues and pull requests!
