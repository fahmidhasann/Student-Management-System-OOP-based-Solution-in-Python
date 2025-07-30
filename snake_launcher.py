#!/usr/bin/env python3
"""
Snake Game Launcher
Choose between the original autonomous snake game and the enhanced version.
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required packages."""
    try:
        import pygame
        print("✓ Pygame is installed")
    except ImportError:
        print("Installing pygame...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
            print("✓ Pygame installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install pygame with pip. Trying system package manager...")
            try:
                subprocess.check_call(["sudo", "apt", "install", "-y", "python3-pygame"])
                print("✓ Pygame installed via apt!")
            except subprocess.CalledProcessError:
                print("❌ Failed to install pygame. Please install manually.")
                return False
    
    # Check for numpy (needed for enhanced version with sounds)
    try:
        import numpy
        print("✓ NumPy is available")
        return True
    except ImportError:
        print("NumPy not found. Enhanced version will run without sound effects.")
        return True

def show_menu():
    """Display the game selection menu."""
    print("\n" + "="*60)
    print("🐍 AUTONOMOUS SNAKE GAME LAUNCHER 🐍")
    print("="*60)
    print()
    print("Choose your experience:")
    print()
    print("1. 🎮 Original Game")
    print("   • Two autonomous snakes compete")
    print("   • No game over on collisions")
    print("   • Simple, clean gameplay")
    print()
    print("2. ⭐ Enhanced Game")
    print("   • Everything from original PLUS:")
    print("   • 🎯 Multiple food items")
    print("   • 💎 Power-ups (speed, growth, invincibility, etc.)")
    print("   • 🧠 Snake personalities (aggressive vs defensive)")
    print("   • ✨ Visual effects (trails, particles, glow)")
    print("   • 🔊 Procedural sound effects")
    print("   • 📊 Game statistics")
    print("   • ⏸️  Pause/Resume (SPACE)")
    print("   • 🔄 Reset game (R)")
    print()
    print("3. 🧪 Run Tests")
    print("   • Verify game functionality")
    print()
    print("4. ❌ Exit")
    print()
    
def run_original_game():
    """Run the original snake game."""
    print("\n🎮 Starting Original Autonomous Snake Game...")
    print("Press ESC to quit")
    try:
        from autonomous_snake_game import Game
        game = Game()
        game.run()
    except Exception as e:
        print(f"❌ Error running original game: {e}")

def run_enhanced_game():
    """Run the enhanced snake game."""
    print("\n⭐ Starting Enhanced Autonomous Snake Game...")
    print("Controls:")
    print("  ESC - Quit")
    print("  SPACE - Pause/Resume")
    print("  R - Reset game")
    
    try:
        # Check if numpy is available for sound
        try:
            import numpy
            print("🔊 Sound effects enabled!")
        except ImportError:
            print("🔇 Running without sound effects (NumPy not available)")
        
        from enhanced_snake_game import EnhancedGame
        game = EnhancedGame()
        game.run()
    except Exception as e:
        print(f"❌ Error running enhanced game: {e}")
        print("Falling back to original game...")
        run_original_game()

def run_tests():
    """Run the test suite."""
    print("\n🧪 Running Game Tests...")
    try:
        subprocess.run([sys.executable, "test_game.py"])
    except Exception as e:
        print(f"❌ Error running tests: {e}")

def main():
    """Main launcher function."""
    # Check dependencies
    if not install_dependencies():
        print("❌ Cannot proceed without required dependencies.")
        sys.exit(1)
    
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == "1":
                run_original_game()
            elif choice == "2":
                run_enhanced_game()
            elif choice == "3":
                run_tests()
            elif choice == "4":
                print("\n👋 Thanks for playing! Goodbye!")
                break
            else:
                print("\n❌ Invalid choice. Please enter 1, 2, 3, or 4.")
                input("Press Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()