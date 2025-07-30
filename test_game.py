#!/usr/bin/env python3
"""
Test script for the autonomous snake game.
This tests the game logic without requiring a display.
"""

import os
import sys

# Set SDL to dummy driver for headless testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'

# Import the game components
from autonomous_snake_game import Snake, Food, Direction, GRID_WIDTH, GRID_HEIGHT

def test_snake_movement():
    """Test basic snake movement."""
    print("Testing snake movement...")
    snake = Snake(5, 5, (255, 0, 0), "Test Snake")
    
    initial_pos = snake.body[0]
    snake.direction = Direction.RIGHT
    snake.move()
    
    new_pos = snake.body[0]
    assert new_pos[0] == initial_pos[0] + 1, "Snake should move right"
    print("✓ Snake movement works")

def test_wall_wrapping():
    """Test that snakes wrap around walls."""
    print("Testing wall wrapping...")
    snake = Snake(GRID_WIDTH - 1, 5, (255, 0, 0), "Test Snake")
    snake.direction = Direction.RIGHT
    snake.move()
    
    new_pos = snake.body[0]
    assert new_pos[0] == 0, f"Snake should wrap to x=0, got {new_pos[0]}"
    print("✓ Wall wrapping works")

def test_food_spawning():
    """Test food spawning mechanics."""
    print("Testing food spawning...")
    snake1 = Snake(5, 5, (255, 0, 0), "Snake 1")
    snake2 = Snake(10, 10, (0, 0, 255), "Snake 2")
    
    food = Food()
    food.respawn(snake1, snake2)
    
    # Food should not spawn on either snake
    assert food.position not in snake1.body, "Food spawned on snake1"
    assert food.position not in snake2.body, "Food spawned on snake2"
    print("✓ Food spawning works")

def test_ai_decision_making():
    """Test AI decision making."""
    print("Testing AI decision making...")
    snake1 = Snake(5, 5, (255, 0, 0), "Snake 1")
    snake2 = Snake(15, 15, (0, 0, 255), "Snake 2")
    
    # Place food to the right of snake1
    food_pos = (7, 5)
    
    # Snake should try to move towards food
    best_direction = snake1.find_best_direction(food_pos, snake2, 0)
    
    # Should prefer moving towards the food
    assert best_direction in [Direction.RIGHT], f"AI should choose RIGHT, got {best_direction}"
    print("✓ AI decision making works")

def test_scoring():
    """Test scoring system."""
    print("Testing scoring...")
    snake = Snake(5, 5, (255, 0, 0), "Test Snake")
    
    initial_score = snake.score
    snake.grow()
    
    assert snake.score == initial_score + 1, "Score should increase when growing"
    assert len(snake.body) > 1, "Snake body should grow"
    print("✓ Scoring system works")

def simulate_game_loop():
    """Simulate a few game steps."""
    print("Simulating game loop...")
    
    snake1 = Snake(GRID_WIDTH // 4, GRID_HEIGHT // 2, (255, 0, 0), "Snake 1")
    snake2 = Snake(3 * GRID_WIDTH // 4, GRID_HEIGHT // 2, (0, 0, 255), "Snake 2")
    
    food = Food()
    food.respawn(snake1, snake2)
    
    # Simulate 10 steps
    for step in range(10):
        # Update AI decisions
        snake1.direction = snake1.find_best_direction(food.position, snake2, step * 100)
        snake2.direction = snake2.find_best_direction(food.position, snake1, step * 100)
        
        # Move snakes
        snake1.move()
        snake2.move()
        
        # Check for food collision
        if snake1.body[0] == food.position:
            snake1.grow()
            food.respawn(snake1, snake2)
        elif snake2.body[0] == food.position:
            snake2.grow()
            food.respawn(snake1, snake2)
        
        # Handle collisions
        if snake1.check_self_collision() or snake1.check_other_snake_collision(snake2):
            snake1.handle_collision()
        
        if snake2.check_self_collision() or snake2.check_other_snake_collision(snake1):
            snake2.handle_collision()
    
    print(f"After 10 steps: Snake1 score={snake1.score}, Snake2 score={snake2.score}")
    print("✓ Game loop simulation works")

def main():
    """Run all tests."""
    print("=== Testing Autonomous Snake Game ===\n")
    
    try:
        test_snake_movement()
        test_wall_wrapping()
        test_food_spawning()
        test_ai_decision_making()
        test_scoring()
        simulate_game_loop()
        
        print(f"\n🎉 All tests passed! The game is working correctly.")
        print(f"To run the actual game (with graphics), use: python3 run_game.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()