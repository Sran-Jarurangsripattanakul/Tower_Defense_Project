import pygame

class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.range = 100
        self.damage = 10
        self.fire_rate = 60  # frames between shots
        self.last_shot_time = 0

        self.image = pygame.image.load("assets/tower.png")  # Make sure this exists
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # Optional: draw range circle
        # pygame.draw.circle(screen, (0, 255, 0), (self.x, self.y), self.range, 1)

    def can_shoot(self, current_time):
        return current_time - self.last_shot_time >= self.fire_rate

    def shoot(self, enemies, current_time):
        for enemy in enemies:
            if self.in_range(enemy):
                if self.can_shoot(current_time):
                    enemy.take_damage(self.damage)
                    self.last_shot_time = current_time
                    break

    def in_range(self, enemy):
        dx = self.x - enemy.x
        dy = self.y - enemy.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        return distance <= self.range
