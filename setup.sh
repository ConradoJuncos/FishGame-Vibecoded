#!/bin/bash
echo "🎣 FISHING GAME - FIRST TIME SETUP 🎣"
echo "==================================="
echo
echo "This will install the required Python packages..."
echo
read -p "Press Enter to continue..."

echo "Installing dependencies..."
pip install -r requirements.txt

echo
echo "✅ Setup complete!"
echo
echo "You can now run:"
echo "- ./start_server.sh (to start server)"
echo "- ./start_client.sh (to start client)"
echo "- ./start_floating_character.sh (for character window)"
echo "- ./run_tests.sh (to run tests)"
echo
echo "Note: You may need to run 'chmod +x *.sh' first on some systems"
