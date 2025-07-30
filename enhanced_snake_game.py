import pygame
import random
import math
import sys
import time
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Optional sound support
try:
    from sound_manager import SoundManager
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False
    print("Note: Running without sound effects (sound_manager not available)")

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
LIME = (50, 205, 50)
PINK = (255, 192, 203)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class PowerUpType(Enum):
    SPEED_BOOST = "speed"
    GROWTH_BOOST = "growth"
    INVINCIBILITY = "invincible"
    DOUBLE_POINTS = "double"
    SLOW_OPPONENT = "slow"

@dataclass
class PowerUp:
    position: Tuple[int, int]
    type: PowerUpType
    color: Tuple[int, int, int]
    duration: int  # frames the power-up lasts on screen
    effect_duration: int  # frames the effect lasts when collected

class SnakePersonality(Enum):
    AGGRESSIVE = "aggressive"  # Takes more risks, goes for power-ups
    DEFENSIVE = "defensive"    # Plays it safe, avoids risky moves
    BALANCED = "balanced"      # Mix of aggressive and defensive

class Snake:
    def __init__(self, start_x, start_y, color, name, personality=SnakePersonality.BALANCED):
        self.body = [(start_x, start_y)]
        self.direction = random.choice(list(Direction))
        self.color = color
        self.name = name
        self.personality = personality
        self.score = 0
        self.last_direction_change = 0
        self.speed_multiplier = 1.0
        self.invincible_frames = 0
        self.double_points_frames = 0
        self.slow_frames = 0
        self.trail = []  # Visual trail effect
        self.max_trail_length = 5
        
    def move(self):
        # Apply speed effects
        if self.slow_frames > 0:
            self.slow_frames -= 1
            if pygame.time.get_ticks() % 2 == 0:  # Move every other frame when slowed
                return self.body[-1] if self.body else (0, 0)
        
        head_x, head_y = self.body[0]
        dx, dy = self.direction.value
        
        # Apply speed boost
        if self.speed_multiplier > 1.0:
            # Speed boost allows skipping grid positions
            dx *= int(self.speed_multiplier)
            dy *= int(self.speed_multiplier)
        
        new_head = (head_x + dx, head_y + dy)
        
        # Handle wall collisions - wrap around
        new_x = new_head[0] % GRID_WIDTH
        new_y = new_head[1] % GRID_HEIGHT
        new_head = (new_x, new_y)
        
        # Add to trail for visual effect
        if len(self.trail) >= self.max_trail_length:
            self.trail.pop(0)
        self.trail.append(self.body[0])
        
        self.body.insert(0, new_head)
        return self.body.pop()
    
    def grow(self, amount=1):
        tail = self.body[-1]
        for _ in range(amount):
            self.body.append(tail)
            points = 1
            if self.double_points_frames > 0:
                points *= 2
            self.score += points
    
    def apply_power_up(self, power_up: PowerUp):
        if power_up.type == PowerUpType.SPEED_BOOST:
            self.speed_multiplier = 2.0
            pygame.time.set_timer(pygame.USEREVENT + 1, power_up.effect_duration * 100)
        elif power_up.type == PowerUpType.GROWTH_BOOST:
            self.grow(3)  # Immediate growth boost
        elif power_up.type == PowerUpType.INVINCIBILITY:
            self.invincible_frames = power_up.effect_duration
        elif power_up.type == PowerUpType.DOUBLE_POINTS:
            self.double_points_frames = power_up.effect_duration
        elif power_up.type == PowerUpType.SLOW_OPPONENT:
            # This will be applied to the opponent snake
            pass
    
    def check_self_collision(self):
        if self.invincible_frames > 0:
            self.invincible_frames -= 1
            return False
        head = self.body[0]
        return head in self.body[1:]
    
    def check_other_snake_collision(self, other_snake):
        if self.invincible_frames > 0:
            return False
        head = self.body[0]
        return head in other_snake.body
    
    def handle_collision(self):
        # When hitting self or other snake, reverse direction
        opposite_directions = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        self.direction = opposite_directions[self.direction]
    
    def find_best_direction(self, food_positions: List[Tuple[int, int]], 
                           power_ups: List[PowerUp], other_snake, current_time):
        # Prevent too frequent direction changes
        if current_time - self.last_direction_change < 150:
            return self.direction
        
        head_x, head_y = self.body[0]
        
        # Find closest food
        closest_food = min(food_positions, 
                          key=lambda f: math.sqrt((head_x - f[0])**2 + (head_y - f[1])**2))
        
        # Consider power-ups based on personality
        target = closest_food
        if power_ups and self.personality != SnakePersonality.DEFENSIVE:
            closest_powerup = min(power_ups, 
                                key=lambda p: math.sqrt((head_x - p.position[0])**2 + (head_y - p.position[1])**2))
            
            # Aggressive snakes prioritize power-ups more
            if self.personality == SnakePersonality.AGGRESSIVE:
                powerup_distance = math.sqrt((head_x - closest_powerup.position[0])**2 + (head_y - closest_powerup.position[1])**2)
                food_distance = math.sqrt((head_x - closest_food[0])**2 + (head_y - closest_food[1])**2)
                
                if powerup_distance < food_distance * 1.5:  # Prefer power-up if reasonably close
                    target = closest_powerup.position
        
        target_x, target_y = target
        
        # Calculate best direction
        best_direction = self.direction
        min_distance = float('inf')
        
        for direction in Direction:
            dx, dy = direction.value
            next_x = (head_x + dx) % GRID_WIDTH
            next_y = (head_y + dy) % GRID_HEIGHT
            next_pos = (next_x, next_y)
            
            # Skip if collision with self (except tail)
            if next_pos in self.body[:-1]:
                continue
            
            # Defensive snakes avoid other snake more
            if next_pos in other_snake.body:
                if self.personality == SnakePersonality.DEFENSIVE:
                    continue  # Never risk collision
                elif self.personality == SnakePersonality.BALANCED and len(other_snake.body) > len(self.body):
                    continue  # Avoid if opponent is larger
            
            # Calculate distance to target
            distance = math.sqrt((next_x - target_x)**2 + (next_y - target_y)**2)
            
            # Add penalty for direction changes
            if direction != self.direction:
                distance += 0.3
            
            if distance < min_distance:
                min_distance = distance
                best_direction = direction
        
        # If no safe direction, find any available direction
        if best_direction == self.direction and min_distance == float('inf'):
            for direction in Direction:
                dx, dy = direction.value
                next_x = (head_x + dx) % GRID_WIDTH
                next_y = (head_y + dy) % GRID_HEIGHT
                next_pos = (next_x, next_y)
                
                if next_pos not in self.body[:-1]:
                    best_direction = direction
                    break
        
        if best_direction != self.direction:
            self.last_direction_change = current_time
        
        return best_direction

class Food:
    def __init__(self):
        self.positions = []
        self.max_food = 3  # Multiple food items
        self.spawn_multiple()
    
    def spawn_single(self):
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        return (x, y)
    
    def spawn_multiple(self):
        self.positions = []
        for _ in range(random.randint(2, self.max_food)):
            self.positions.append(self.spawn_single())
    
    def respawn_eaten(self, eaten_pos, snake1, snake2):
        if eaten_pos in self.positions:
            self.positions.remove(eaten_pos)
        
        # Add new food if below minimum
        while len(self.positions) < 2:
            new_pos = self.spawn_single()
            if (new_pos not in snake1.body and new_pos not in snake2.body and 
                new_pos not in self.positions):
                self.positions.append(new_pos)

class PowerUpManager:
    def __init__(self):
        self.power_ups = []
        self.spawn_timer = 0
        self.spawn_interval = 300  # frames between power-up spawns
        
    def update(self, snake1, snake2):
        self.spawn_timer += 1
        
        # Remove expired power-ups
        self.power_ups = [p for p in self.power_ups if p.duration > 0]
        
        # Update durations
        for power_up in self.power_ups:
            power_up.duration -= 1
        
        # Spawn new power-ups
        if self.spawn_timer >= self.spawn_interval and len(self.power_ups) < 2:
            self.spawn_power_up(snake1, snake2)
            self.spawn_timer = 0
    
    def spawn_power_up(self, snake1, snake2):
        # Find empty position
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            pos = (x, y)
            
            if (pos not in snake1.body and pos not in snake2.body and
                not any(p.position == pos for p in self.power_ups)):
                break
        
        # Random power-up type
        power_type = random.choice(list(PowerUpType))
        colors = {
            PowerUpType.SPEED_BOOST: YELLOW,
            PowerUpType.GROWTH_BOOST: PURPLE,
            PowerUpType.INVINCIBILITY: CYAN,
            PowerUpType.DOUBLE_POINTS: GOLD,
            PowerUpType.SLOW_OPPONENT: MAGENTA
        }
        
        power_up = PowerUp(
            position=pos,
            type=power_type,
            color=colors[power_type],
            duration=600,  # 60 seconds at 10 FPS
            effect_duration=100  # 10 seconds effect
        )
        
        self.power_ups.append(power_up)
    
    def check_collection(self, snake, other_snake, sound_manager=None):
        collected = []
        for power_up in self.power_ups:
            if snake.body[0] == power_up.position:
                collected.append(power_up)
                snake.apply_power_up(power_up)
                
                # Play sound effect based on power-up type
                if sound_manager:
                    if power_up.type == PowerUpType.SPEED_BOOST:
                        sound_manager.play('speed')
                    elif power_up.type == PowerUpType.GROWTH_BOOST:
                        sound_manager.play('growth')
                    elif power_up.type == PowerUpType.INVINCIBILITY:
                        sound_manager.play('invincible')
                    elif power_up.type == PowerUpType.DOUBLE_POINTS:
                        sound_manager.play('double')
                    elif power_up.type == PowerUpType.SLOW_OPPONENT:
                        sound_manager.play('slow')
                    else:
                        sound_manager.play('powerup')
                
                # Special case: slow opponent
                if power_up.type == PowerUpType.SLOW_OPPONENT:
                    other_snake.slow_frames = power_up.effect_duration
        
        # Remove collected power-ups
        for power_up in collected:
            self.power_ups.remove(power_up)

class GameStats:
    def __init__(self):
        self.start_time = time.time()
        self.snake1_stats = {"food_eaten": 0, "power_ups_collected": 0, "collisions": 0}
        self.snake2_stats = {"food_eaten": 0, "power_ups_collected": 0, "collisions": 0}
        self.total_food_spawned = 0
        self.total_power_ups_spawned = 0

class EnhancedGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Enhanced Autonomous Snake Competition")
        self.clock = pygame.time.Clock()
        
        # Create snakes with different personalities
        self.snake1 = Snake(GRID_WIDTH // 4, GRID_HEIGHT // 2, RED, "Aggressive Red", SnakePersonality.AGGRESSIVE)
        self.snake2 = Snake(3 * GRID_WIDTH // 4, GRID_HEIGHT // 2, BLUE, "Defensive Blue", SnakePersonality.DEFENSIVE)
        
        # Game systems
        self.food = Food()
        self.power_up_manager = PowerUpManager()
        self.stats = GameStats()
        
        # Sound system (optional)
        self.sound_manager = None
        if SOUND_AVAILABLE:
            try:
                self.sound_manager = SoundManager()
                print("🔊 Sound effects enabled!")
            except Exception as e:
                print(f"Warning: Could not initialize sound: {e}")
        
        # Visual effects
        self.particles = []
        
        # Fonts
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)
        
    def create_particle_effect(self, pos, color, count=5):
        """Create particle effect for visual feedback"""
        for _ in range(count):
            particle = {
                'pos': [pos[0] * GRID_SIZE + GRID_SIZE//2, pos[1] * GRID_SIZE + GRID_SIZE//2],
                'vel': [random.uniform(-2, 2), random.uniform(-2, 2)],
                'life': 30,
                'color': color
            }
            self.particles.append(particle)
    
    def update_particles(self):
        """Update and remove expired particles"""
        for particle in self.particles[:]:
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw_snake_with_effects(self, snake):
        """Draw snake with trail and status effects"""
        # Draw trail
        for i, trail_pos in enumerate(snake.trail):
            alpha = int(255 * (i + 1) / len(snake.trail) * 0.3)
            trail_color = (*snake.color, alpha)
            trail_surface = pygame.Surface((GRID_SIZE, GRID_SIZE))
            trail_surface.set_alpha(alpha)
            trail_surface.fill(snake.color)
            self.screen.blit(trail_surface, (trail_pos[0] * GRID_SIZE, trail_pos[1] * GRID_SIZE))
        
        # Draw snake body
        for i, segment in enumerate(snake.body):
            color = snake.color
            
            # Modify color based on status effects
            if snake.invincible_frames > 0:
                # Flashing effect for invincibility
                if pygame.time.get_ticks() % 200 < 100:
                    color = CYAN
            elif snake.double_points_frames > 0:
                color = GOLD
            elif snake.slow_frames > 0:
                color = tuple(c // 2 for c in snake.color)  # Darker when slowed
            
            # Head is slightly larger
            size = GRID_SIZE if i > 0 else GRID_SIZE + 2
            offset = 0 if i > 0 else -1
            
            pygame.draw.rect(self.screen, color, 
                           (segment[0] * GRID_SIZE + offset, segment[1] * GRID_SIZE + offset, size, size))
            
            # Draw eyes on head
            if i == 0:
                eye_size = 3
                pygame.draw.circle(self.screen, WHITE, 
                                 (segment[0] * GRID_SIZE + 6, segment[1] * GRID_SIZE + 6), eye_size)
                pygame.draw.circle(self.screen, WHITE, 
                                 (segment[0] * GRID_SIZE + 14, segment[1] * GRID_SIZE + 6), eye_size)
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw grid lines (subtle)
        grid_color = (20, 20, 20)
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, grid_color, (0, y), (WINDOW_WIDTH, y))
        
        # Draw food with glow effect
        for food_pos in self.food.positions:
            # Glow effect
            glow_surface = pygame.Surface((GRID_SIZE + 6, GRID_SIZE + 6))
            glow_surface.set_alpha(100)
            glow_surface.fill(LIME)
            self.screen.blit(glow_surface, (food_pos[0] * GRID_SIZE - 3, food_pos[1] * GRID_SIZE - 3))
            
            # Main food
            pygame.draw.rect(self.screen, GREEN, 
                           (food_pos[0] * GRID_SIZE, food_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            
            # Food sparkle
            if pygame.time.get_ticks() % 1000 < 500:
                pygame.draw.circle(self.screen, WHITE, 
                                 (food_pos[0] * GRID_SIZE + GRID_SIZE//2, 
                                  food_pos[1] * GRID_SIZE + GRID_SIZE//2), 2)
        
        # Draw power-ups with pulsing effect
        for power_up in self.power_up_manager.power_ups:
            pulse = math.sin(pygame.time.get_ticks() * 0.01) * 3 + 3
            size = GRID_SIZE + int(pulse)
            offset = -int(pulse // 2)
            
            pygame.draw.rect(self.screen, power_up.color, 
                           (power_up.position[0] * GRID_SIZE + offset, 
                            power_up.position[1] * GRID_SIZE + offset, size, size))
            
            # Power-up symbol
            center_x = power_up.position[0] * GRID_SIZE + GRID_SIZE // 2
            center_y = power_up.position[1] * GRID_SIZE + GRID_SIZE // 2
            
            if power_up.type == PowerUpType.SPEED_BOOST:
                pygame.draw.polygon(self.screen, BLACK, 
                                  [(center_x - 5, center_y), (center_x + 5, center_y - 3), (center_x + 5, center_y + 3)])
            elif power_up.type == PowerUpType.GROWTH_BOOST:
                pygame.draw.circle(self.screen, BLACK, (center_x, center_y), 6)
            # Add more symbols for other power-ups...
        
        # Draw snakes with effects
        self.draw_snake_with_effects(self.snake1)
        self.draw_snake_with_effects(self.snake2)
        
        # Draw particles
        for particle in self.particles:
            pygame.draw.circle(self.screen, particle['color'], 
                             [int(particle['pos'][0]), int(particle['pos'][1])], 2)
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """Draw user interface with scores and stats"""
        # Score display
        score1_text = self.font.render(f"🔴 {self.snake1.name}: {self.snake1.score}", True, WHITE)
        score2_text = self.font.render(f"🔵 {self.snake2.name}: {self.snake2.score}", True, WHITE)
        
        self.screen.blit(score1_text, (10, 10))
        self.screen.blit(score2_text, (10, 40))
        
        # Status effects
        y_offset = 70
        if self.snake1.invincible_frames > 0:
            status_text = self.small_font.render("Red: INVINCIBLE", True, CYAN)
            self.screen.blit(status_text, (10, y_offset))
            y_offset += 20
        
        if self.snake1.double_points_frames > 0:
            status_text = self.small_font.render("Red: DOUBLE POINTS", True, GOLD)
            self.screen.blit(status_text, (10, y_offset))
            y_offset += 20
        
        if self.snake2.slow_frames > 0:
            status_text = self.small_font.render("Blue: SLOWED", True, MAGENTA)
            self.screen.blit(status_text, (10, y_offset))
            y_offset += 20
        
        # Game time
        elapsed = time.time() - self.stats.start_time
        time_text = self.small_font.render(f"Time: {elapsed:.0f}s", True, WHITE)
        self.screen.blit(time_text, (WINDOW_WIDTH - 120, 10))
        
        # Power-up indicators
        powerup_text = self.small_font.render(f"Power-ups: {len(self.power_up_manager.power_ups)}", True, WHITE)
        self.screen.blit(powerup_text, (WINDOW_WIDTH - 120, 30))
        
        # Food count
        food_text = self.small_font.render(f"Food: {len(self.food.positions)}", True, WHITE)
        self.screen.blit(food_text, (WINDOW_WIDTH - 120, 50))
        
        # Instructions
        instruction_text = self.small_font.render("ESC: Quit | SPACE: Pause | R: Reset", True, WHITE)
        self.screen.blit(instruction_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 25))
    
    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Update power-ups
        self.power_up_manager.update(self.snake1, self.snake2)
        
        # Update particles
        self.update_particles()
        
        # AI decision making
        self.snake1.direction = self.snake1.find_best_direction(
            self.food.positions, self.power_up_manager.power_ups, self.snake2, current_time)
        self.snake2.direction = self.snake2.find_best_direction(
            self.food.positions, self.power_up_manager.power_ups, self.snake1, current_time)
        
        # Move snakes
        self.snake1.move()
        self.snake2.move()
        
        # Check food collection
        for food_pos in self.food.positions[:]:
            if self.snake1.body[0] == food_pos:
                self.snake1.grow()
                self.food.respawn_eaten(food_pos, self.snake1, self.snake2)
                self.create_particle_effect(food_pos, GREEN)
                self.stats.snake1_stats["food_eaten"] += 1
                if self.sound_manager:
                    self.sound_manager.play('eat')
            elif self.snake2.body[0] == food_pos:
                self.snake2.grow()
                self.food.respawn_eaten(food_pos, self.snake1, self.snake2)
                self.create_particle_effect(food_pos, GREEN)
                self.stats.snake2_stats["food_eaten"] += 1
                if self.sound_manager:
                    self.sound_manager.play('eat')
        
        # Check power-up collection
        self.power_up_manager.check_collection(self.snake1, self.snake2, self.sound_manager)
        self.power_up_manager.check_collection(self.snake2, self.snake1, self.sound_manager)
        
        # Handle collisions
        if self.snake1.check_self_collision() or self.snake1.check_other_snake_collision(self.snake2):
            self.snake1.handle_collision()
            self.create_particle_effect(self.snake1.body[0], RED)
            self.stats.snake1_stats["collisions"] += 1
            if self.sound_manager:
                self.sound_manager.play('collision')
        
        if self.snake2.check_self_collision() or self.snake2.check_other_snake_collision(self.snake1):
            self.snake2.handle_collision()
            self.create_particle_effect(self.snake2.body[0], BLUE)
            self.stats.snake2_stats["collisions"] += 1
            if self.sound_manager:
                self.sound_manager.play('collision')
    
    def run(self):
        running = True
        paused = False
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_r:
                        # Reset game
                        self.__init__()
                elif event.type == pygame.USEREVENT + 1:
                    # Speed boost timer expired
                    self.snake1.speed_multiplier = 1.0
                    self.snake2.speed_multiplier = 1.0
            
            if not paused:
                self.update()
            
            self.draw()
            self.clock.tick(12)  # Slightly faster for more action
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = EnhancedGame()
    game.run()