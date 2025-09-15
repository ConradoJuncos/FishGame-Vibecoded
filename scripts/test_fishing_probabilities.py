#!/usr/bin/env python3
"""
Test Fishing Probabilities
Test script to validate the fish rarity distribution.
"""

import random
import sys
import os

# Add the parent directory to path to import from test_connection
sys.path.append(os.path.dirname(__file__))

from test_connection import FISH_TYPES, FISH_PROBABILITIES, catch_fish

def test_fish_probabilities(num_catches=1000):
    """Test fish catching probabilities over many attempts"""
    print(f"=== Testing Fish Probabilities ===")
    print(f"Testing {num_catches} fish catches...")
    print(f"Expected probabilities: {dict(zip(FISH_TYPES, FISH_PROBABILITIES))}")
    
    # Count catches
    catch_counts = {fish: 0 for fish in FISH_TYPES}
    
    for _ in range(num_catches):
        caught_fish = catch_fish()
        catch_counts[caught_fish] += 1
    
    # Calculate actual probabilities
    print(f"\n--- Results ---")
    for fish in FISH_TYPES:
        expected = FISH_PROBABILITIES[FISH_TYPES.index(fish)] * 100
        actual = (catch_counts[fish] / num_catches) * 100
        difference = abs(expected - actual)
        
        print(f"Fish '{fish}': {catch_counts[fish]:4d} catches ({actual:5.1f}%) - Expected: {expected:5.1f}% - Diff: {difference:4.1f}%")
    
    print(f"\nTotal catches: {sum(catch_counts.values())}")
    print("Test completed! ✅")

def test_fishing_simulation(seconds=60):
    """Simulate fishing for a number of seconds with 5% chance per second"""
    print(f"\n=== Fishing Simulation ===")
    print(f"Simulating {seconds} seconds of fishing (5% chance per second)...")
    
    total_fish = 0
    catch_counts = {fish: 0 for fish in FISH_TYPES}
    
    for second in range(seconds):
        if random.random() < 0.05:  # 5% chance
            caught_fish = catch_fish()
            catch_counts[caught_fish] += 1
            total_fish += 1
            print(f"⏰ Second {second + 1}: 🐟 Caught fish '{caught_fish}'!")
    
    print(f"\n--- Fishing Results ---")
    print(f"Total fishing time: {seconds} seconds")
    print(f"Total fish caught: {total_fish}")
    print(f"Average catch rate: {(total_fish/seconds)*100:.1f}% per second")
    print(f"Expected catches: ~{seconds * 0.05:.1f}")
    
    if total_fish > 0:
        print(f"\nFish distribution:")
        for fish in FISH_TYPES:
            if catch_counts[fish] > 0:
                percentage = (catch_counts[fish] / total_fish) * 100
                print(f"  {fish}: {catch_counts[fish]} ({percentage:.1f}%)")
    
    print("Simulation completed! ✅")

if __name__ == "__main__":
    print("🎣 Fish Probability Testing Tool 🎣")
    
    # Test fish probabilities
    test_fish_probabilities(1000)
    
    # Test fishing simulation
    test_fishing_simulation(60)
    
    print("\n🎣 All tests completed!")
