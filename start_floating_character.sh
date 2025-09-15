#!/bin/bash
echo "Starting Transparent Floating Character..."
echo
echo "Controls:"
echo "- Left-click and drag to move"
echo "- Right-click to toggle always-on-top"
echo "- Double-click to close"
echo
python scripts/simple_character.py &
echo "Character window launched with transparent background!"
