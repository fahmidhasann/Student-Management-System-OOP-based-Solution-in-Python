Hey there!

Welcome to my "Student Management System project". I know it's a simple project, but I'm excited to share it with you! I've just finished a basic Python course, and I created this because I'm really curious about programming. It's my way of putting what I've learned into practice.

This Python-based Student Management System provides a simple yet effective way to manage student information and grades. It's designed for use by school administrators and teachers to keep track of student data and academic performance.

Features:

1.Add new students with unique IDs

2.Record and update student grades for various subjects

3.Calculate average grades for individual students

4.Retrieve information for specific students

5.List all student IDs in the system

6.Get a complete overview of all students and their information

How to Use:

Create an instance of the StudentManagementSystem class Use the following methods to manage student data:

-add_student(id, name, age): Add a new student to the system

-add_grade(id, subject, mark): Record a grade for a specific student and subject

-average_grade(id): Calculate the average grade for a student

-get_info(id): Retrieve information for a specific student

-get_all_id(): Get a list of all student IDs in the system

-get_all_info(): Get complete information for all students

# Autonomous Snake Competition Game

An autonomous snake game where two AI-controlled snakes compete for food. Unlike traditional snake games, the snakes don't die when hitting walls or each other - they continue playing indefinitely!

## Features

🐍 **Two Autonomous Snakes**: Red and Blue snakes controlled by AI
🎯 **Smart AI**: Snakes automatically navigate toward food using pathfinding
🔄 **No Game Over**: Snakes wrap around walls and reverse direction on collisions
🏆 **Real-time Scoring**: Track which snake is collecting more food
🎮 **Competitive Gameplay**: Watch the snakes compete against each other

## Game Mechanics

- **Wall Collision**: Snakes wrap around to the opposite side (like Pac-Man)
- **Snake Collision**: When snakes hit themselves or each other, they reverse direction
- **Food Collection**: First snake to reach the food gets the point and grows
- **AI Behavior**: Snakes use distance-based pathfinding to locate food
- **Collision Avoidance**: Snakes try to avoid immediate collisions when possible

## Requirements

- Python 3.x
- pygame library

## Installation & Running

### Option 1: Using the auto-installer (Recommended)
```bash
python3 run_game.py
```
This script will automatically install pygame if it's not available and then start the game.

### Option 2: Manual installation
```bash
# Install pygame
pip install pygame
# OR on Ubuntu/Debian:
sudo apt install python3-pygame

# Run the game
python3 autonomous_snake_game.py
```

## Controls

- **ESC**: Quit the game
- The snakes are fully autonomous - no manual controls needed!

## File Structure

- `autonomous_snake_game.py` - Main game file with all classes and game logic
- `run_game.py` - Auto-installer and game launcher
- `test_game.py` - Test suite to verify game functionality
- `requirements.txt` - Python dependencies

## How It Works

### Snake AI
Each snake uses a simple but effective AI algorithm:

1. **Target Acquisition**: Calculate distance to food from each possible move direction
2. **Collision Avoidance**: Avoid moves that would cause immediate collisions
3. **Pathfinding**: Choose the direction that minimizes distance to food
4. **Smooth Movement**: Prefer continuing in the current direction when distances are similar

### Collision Handling
- **Wall Collisions**: Use modulo arithmetic to wrap coordinates around screen boundaries
- **Snake Collisions**: Reverse direction instead of ending the game
- **Food Respawning**: Ensure food never spawns on either snake

## Technical Details

- **Grid-based Movement**: 40x30 grid (800x600 pixels with 20px cells)
- **Frame Rate**: 10 FPS for visible snake movement
- **Color Coding**: Red snake vs Blue snake, Green food
- **Scoring System**: Points awarded for each food item collected

## Testing

Run the test suite to verify game functionality:
```bash
python3 test_game.py
```

This tests:
- Snake movement mechanics
- Wall wrapping behavior
- Food spawning logic
- AI decision making
- Scoring system
- Complete game loop simulation

## Customization

You can easily modify the game by changing constants in `autonomous_snake_game.py`:

- `WINDOW_WIDTH/HEIGHT`: Change screen size
- `GRID_SIZE`: Adjust cell size
- `clock.tick(10)`: Change game speed
- Colors in the color constants section
- AI behavior in the `find_best_direction` method

## License

This project is open source and available under the MIT License.

---

Enjoy watching the autonomous snakes compete! 🐍🎮
