import pygame
import math

class Enemy:
    def __init__(self, path, speed=2):
        if not path:
            raise ValueError("Enemy path is empty. Ensure your TMX map defines a proper path.")

        self.path = path
        self.speed = speed
        self.current_point = 0
        self.x, self.y = self.path[0]
        self.alive = True
        self.health = 100
        
        # Create a placeholder image (red circle)
        self.image = pygame.Surface((20, 20))  # Create a 20x20 surface
        pygame.draw.circle(self.image, (255, 0, 0), (10, 10), 10)  # Draw a red circle in the center
        self.image.set_colorkey((0, 0, 0))  # Set transparent color if needed

    def move(self):
        if self.current_point + 1 >= len(self.path):
            self.alive = False  # Reached the end
            return

        target_x, target_y = self.path[self.current_point + 1]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        if dist == 0:
            self.current_point += 1
            return

        dx /= dist
        dy /= dist

        self.x += dx * self.speed
        self.y += dy * self.speed

        # Snap to the next point if close enough
        if math.hypot(target_x - self.x, target_y - self.y) < self.speed:
            self.current_point += 1

    def draw(self, surface):
        surface.blit(self.image, (int(self.x) - 10, int(self.y) - 10))  # Draw the red circle at the current position

    def take_damage(self, amount):
        """Reduces health when the enemy is hit."""
        self.health -= amount
        if self.health <= 0:
            self.alive = False  # Enemy dies when health reaches 0
