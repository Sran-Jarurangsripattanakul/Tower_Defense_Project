import pygame

class Projectile:
    def __init__(self, x, y, target, damage, speed=5,
                 slow_effect=None, slow_duration=0):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = speed
        self.slow_effect = slow_effect
        self.slow_duration = slow_duration
        self.alive = True

        # Visual bullet
        self.image = pygame.Surface((8, 8))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        # If target died, kill projectile
        if not self.target.is_alive():
            self.alive = False
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = (dx*dx + dy*dy) ** 0.5
        if dist <= self.speed:
            self.hit()
            return

        dx /= dist; dy /= dist
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.rect.center = (self.x, self.y)

    def hit(self):
        # Damage
        self.target.take_damage(self.damage)
        # Apply slow if any
        if self.slow_effect is not None:
            now = pygame.time.get_ticks()
            self.target.apply_slow(self.slow_effect, self.slow_duration, now)
        self.alive = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)
