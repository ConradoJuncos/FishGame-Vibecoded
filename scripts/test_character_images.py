#!/usr/bin/env python3
"""
Test Character Image Switching
Quick test to verify the caught_character.png image switching works.
"""

import os
import time
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_image_switching():
    """Test the character image switching functionality"""
    print("🎣 Testing Character Image Switching")
    print("====================================")
    
    # Check if images exist
    base_path = os.path.dirname(os.path.dirname(__file__))
    normal_image = os.path.join(base_path, "images", "idle_character.png")
    caught_image = os.path.join(base_path, "images", "caught_character.png")
    
    print(f"Checking for normal character image: {normal_image}")
    if os.path.exists(normal_image):
        print("✅ Normal character image found")
    else:
        print("❌ Normal character image NOT found")
        return False
    
    print(f"Checking for caught character image: {caught_image}")
    if os.path.exists(caught_image):
        print("✅ Caught character image found")
    else:
        print("❌ Caught character image NOT found")
        return False
    
    print("\n🎯 Simulating fish catch...")
    
    # Simulate fish catch by creating signal file every 5 seconds
    signal_file = os.path.join(base_path, "fish_caught_signal.tmp")
    
    for i in range(3):
        print(f"Creating fish caught signal {i+1}/3...")
        with open(signal_file, "w") as f:
            f.write(str(time.time()))
        
        print("✅ Signal created! Character should switch to caught_character.png")
        print("   (Signal will be processed by character window if running)")
        
        time.sleep(3)  # Wait 3 seconds between signals
    
    print("\n🎉 Test completed!")
    print("If character window is running, you should have seen:")
    print("1. Character image switch from idle_character.png to caught_character.png")
    print("2. Character revert back to normal after 2 seconds")
    print("3. This should have happened 3 times")
    
    return True

if __name__ == "__main__":
    test_image_switching()
