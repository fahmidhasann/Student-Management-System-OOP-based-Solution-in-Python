#!/usr/bin/env python3
"""
Autonomous Snake Game Runner
Run this script to start the autonomous snake competition.
"""

import subprocess
import sys
import os

def install_pygame():
    """Install pygame if not available."""
    try:
        import pygame
        print("Pygame is already installed.")
        return True
    except ImportError:
        print("Pygame not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
            print("Pygame installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install pygame. Please install it manually with: pip install pygame")
            return False

def main():
    print("=== Autonomous Snake Competition ===")
    print("Two AI snakes compete for food!")
    print("- Snakes wrap around walls instead of dying")
    print("- Collisions reverse direction instead of ending the game")
    print("- Press ESC to quit\n")
    
    # Check and install pygame if needed
    if not install_pygame():
        return
    
    # Import and run the game
    try:
        from autonomous_snake_game import Game
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error running the game: {e}")
        print("Make sure all files are in the same directory.")

if __name__ == "__main__":
    main()