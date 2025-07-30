import pygame
import random
import math
import sys
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
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

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class Snake:
    def __init__(self, start_x, start_y, color, name):
        self.body = [(start_x, start_y)]
        self.direction = random.choice(list(Direction))
        self.color = color
        self.name = name
        self.score = 0
        self.last_direction_change = 0
        
    def move(self):
        head_x, head_y = self.body[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        # Handle wall collisions - wrap around instead of dying
        new_x = new_head[0] % GRID_WIDTH
        new_y = new_head[1] % GRID_HEIGHT
        new_head = (new_x, new_y)
        
        self.body.insert(0, new_head)
        return self.body.pop()  # Return tail for potential food check
    
    def grow(self):
        # Add back the tail that was removed in the last move
        tail = self.body[-1]
        self.body.append(tail)
        self.score += 1
    
    def check_self_collision(self):
        head = self.body[0]
        return head in self.body[1:]
    
    def check_other_snake_collision(self, other_snake):
        head = self.body[0]
        return head in other_snake.body
    
    def handle_collision(self):
        # When hitting self or other snake, just reverse direction
        opposite_directions = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        self.direction = opposite_directions[self.direction]
    
    def find_best_direction(self, food_pos, other_snake, current_time):
        # Prevent too frequent direction changes
        if current_time - self.last_direction_change < 200:  # 200ms cooldown
            return self.direction
        
        head_x, head_y = self.body[0]
        food_x, food_y = food_pos
        
        # Calculate distance to food for each possible direction
        best_direction = self.direction
        min_distance = float('inf')
        
        for direction in Direction:
            dx, dy = direction.value
            next_x = (head_x + dx) % GRID_WIDTH
            next_y = (head_y + dy) % GRID_HEIGHT
            next_pos = (next_x, next_y)
            
            # Skip if this would cause immediate collision with self (except tail)
            if next_pos in self.body[:-1]:
                continue
            
            # Skip if this would cause collision with other snake
            if next_pos in other_snake.body:
                continue
            
            # Calculate distance to food
            distance = math.sqrt((next_x - food_x)**2 + (next_y - food_y)**2)
            
            # Add penalty for direction changes to make movement smoother
            if direction != self.direction:
                distance += 0.5
            
            if distance < min_distance:
                min_distance = distance
                best_direction = direction
        
        # If no safe direction found, try to avoid collisions
        if best_direction == self.direction and min_distance == float('inf'):
            for direction in Direction:
                dx, dy = direction.value
                next_x = (head_x + dx) % GRID_WIDTH
                next_y = (head_y + dy) % GRID_HEIGHT
                next_pos = (next_x, next_y)
                
                # Just avoid immediate self collision
                if next_pos not in self.body[:-1]:
                    best_direction = direction
                    break
        
        if best_direction != self.direction:
            self.last_direction_change = current_time
            
        return best_direction

class Food:
    def __init__(self):
        self.position = self.spawn()
    
    def spawn(self):
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        return (x, y)
    
    def respawn(self, snake1, snake2):
        # Ensure food doesn't spawn on either snake
        while True:
            new_pos = self.spawn()
            if new_pos not in snake1.body and new_pos not in snake2.body:
                self.position = new_pos
                break

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Autonomous Snake Competition")
        self.clock = pygame.time.Clock()
        
        # Create two snakes
        self.snake1 = Snake(GRID_WIDTH // 4, GRID_HEIGHT // 2, RED, "Snake 1")
        self.snake2 = Snake(3 * GRID_WIDTH // 4, GRID_HEIGHT // 2, BLUE, "Snake 2")
        
        # Create food
        self.food = Food()
        self.food.respawn(self.snake1, self.snake2)
        
        # Font for score display
        self.font = pygame.font.Font(None, 36)
        
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw snakes
        for segment in self.snake1.body:
            pygame.draw.rect(self.screen, self.snake1.color, 
                           (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        
        for segment in self.snake2.body:
            pygame.draw.rect(self.screen, self.snake2.color, 
                           (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        
        # Draw food
        pygame.draw.rect(self.screen, GREEN, 
                        (self.food.position[0] * GRID_SIZE, self.food.position[1] * GRID_SIZE, 
                         GRID_SIZE, GRID_SIZE))
        
        # Draw scores
        score1_text = self.font.render(f"Red Snake: {self.snake1.score}", True, WHITE)
        score2_text = self.font.render(f"Blue Snake: {self.snake2.score}", True, WHITE)
        
        self.screen.blit(score1_text, (10, 10))
        self.screen.blit(score2_text, (10, 50))
        
        # Draw instructions
        instruction_text = self.font.render("Autonomous Snake Competition - Press ESC to quit", True, WHITE)
        self.screen.blit(instruction_text, (WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT - 30))
        
        pygame.display.flip()
    
    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Update snake directions based on AI
        self.snake1.direction = self.snake1.find_best_direction(self.food.position, self.snake2, current_time)
        self.snake2.direction = self.snake2.find_best_direction(self.food.position, self.snake1, current_time)
        
        # Move snakes
        tail1 = self.snake1.move()
        tail2 = self.snake2.move()
        
        # Check for food collision
        if self.snake1.body[0] == self.food.position:
            self.snake1.grow()
            self.food.respawn(self.snake1, self.snake2)
        elif self.snake2.body[0] == self.food.position:
            self.snake2.grow()
            self.food.respawn(self.snake1, self.snake2)
        
        # Handle collisions (but don't end game)
        if self.snake1.check_self_collision() or self.snake1.check_other_snake_collision(self.snake2):
            self.snake1.handle_collision()
        
        if self.snake2.check_self_collision() or self.snake2.check_other_snake_collision(self.snake1):
            self.snake2.handle_collision()
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            self.update()
            self.draw()
            self.clock.tick(10)  # 10 FPS for visible movement
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()