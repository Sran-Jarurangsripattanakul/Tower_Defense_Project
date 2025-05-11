import pygame
import math

class Enemy:
    def __init__(self, path):
        if not path:
            raise ValueError("Enemy path is empty. Ensure your TMX map defines a proper path.")

        self.path = path
        self.current_point = 0
        self.x, self.y = self.path[0]
        self.alive = True

        # Health
        self.health = 100
        self.max_health = self.health

        # Speed + slow
        self.speed = 1.0
        self.original_speed = self.speed
        self.slow_until = 0  # timestamp when slow ends

        # Visual
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0), (10, 10), 10)

    def move(self, time_multiplier=1.0):
        now = pygame.time.get_ticks()
        # revert slow if expired
        if now > self.slow_until:
            self.speed = self.original_speed

        # if we've reached the end of the path, die
        if self.current_point + 1 >= len(self.path):
            self.alive = False
            return

        # calculate one movement “step”
        step = self.speed * time_multiplier

        # next waypoint
        tx, ty = self.path[self.current_point + 1]
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)

        if dist > 0:
            # move proportionally toward the target
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step

        # once we're within one "step" of the waypoint, snap and advance
        if dist < step:
            self.current_point += 1
            # snap exactly onto the waypoint
            self.x, self.y = float(tx), float(ty)



    def draw(self, surface):
        # Blit the enemy sprite
        surface.blit(self.image, (int(self.x) - 10, int(self.y) - 10))

        # Draw health bar
        bar_w, bar_h = 20, 4
        health_ratio = max(self.health, 0) / self.max_health
        bx = int(self.x) - bar_w // 2
        by = int(self.y) - 16  # above the sprite

        # Background (red)
        pygame.draw.rect(surface, (150, 0, 0), (bx, by, bar_w, bar_h))
        # Foreground (green)
        pygame.draw.rect(surface, (0, 255, 0), (bx, by, int(bar_w * health_ratio), bar_h))

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.alive = False

    def apply_slow(self, multiplier, duration_ms, current_time):
        self.speed = self.original_speed * multiplier
        self.slow_until = current_time + duration_ms

    def is_alive(self):
        return self.alive

class Goblin(Enemy):
    def __init__(self, path):
        super().__init__(path)
        self.health = 50
        self.max_health = 50
        self.speed = 2.0
        self.original_speed = self.speed
        pygame.draw.circle(self.image, (0, 255, 0), (10, 10), 10)

class Orc(Enemy):
    def __init__(self, path):
        super().__init__(path)
        self.health = 150
        self.max_health = 150
        self.speed = 0.8
        self.original_speed = self.speed
        pygame.draw.circle(self.image, (0, 0, 255), (10, 10), 10)

class Troll(Enemy):
    def __init__(self, path):
        super().__init__(path)
        self.health = 250
        self.max_health = 250
        self.speed = 0.5
        self.original_speed = self.speed
        pygame.draw.circle(self.image, (128, 0, 128), (10, 10), 10)

class Boss(Enemy):
    def __init__(self, path):
        super().__init__(path)
        self.health = 1000
        self.max_health = self.health
        self.speed = 0.7
        self.original_speed = self.speed
        # Make the boss visually distinct (e.g., larger blue circle)
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 0, 150), (20, 20), 20)
