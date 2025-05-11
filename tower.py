import pygame

class Tower:
    def __init__(self, x, y, base_cost=50):
        self.x = x
        self.y = y

        # Combat stats
        self.range = 100
        self.damage = 10
        self.fire_rate = 60  # frames between shots
        self.last_shot_time = 0

        # Upgrade tracking
        self.level = 1
        self.upgrade_cost = base_cost

        # Financials
        self.purchase_cost  = base_cost
        self.total_invested = base_cost

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def can_shoot(self, current_time, time_multiplier):
        return (current_time - self.last_shot_time) >= (self.fire_rate / time_multiplier)

    def in_range(self, enemy):
        dx, dy = self.x - enemy.x, self.y - enemy.y
        return (dx*dx + dy*dy)**0.5 <= self.range

    def shoot(self, enemies, current_time, projectiles, time_multiplier=1.0):
        if not self.can_shoot(current_time, time_multiplier):
            return
        candidates = [e for e in enemies if e.alive and self.in_range(e)]
        if not candidates:
            return
        # target the enemy closest to the base
        candidates.sort(key=lambda e: e.current_point, reverse=True)
        self.attack(candidates[0], current_time, projectiles)

    def attack(self, enemy, current_time, projectiles):
        from projectile import Projectile
        proj = Projectile(self.x, self.y, enemy, self.damage)
        projectiles.append(proj)
        self.last_shot_time = current_time

    def upgrade(self):
        # only allow up to level 5
        if self.level >= 5:
            return

        self.level += 1
        self.damage    = int(self.damage * 1.3)
        self.range     = int(self.range  * 1.1)
        self.fire_rate = max(10, int(self.fire_rate * 0.9))

        old_cost = self.upgrade_cost
        # after level-up the new upgrade cost
        self.upgrade_cost = int(old_cost * 1.5)
        self.total_invested += self.upgrade_cost

    def get_sell_value(self):
        """50% refund of everything invested."""
        return int(self.total_invested * 0.5)


class ArcherTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, base_cost=30)
        self.damage   = 15
        self.fire_rate = 40
        img = pygame.image.load("assets/tower/archer_tower.png")
        self.image = pygame.transform.scale(img, (50, 50))
        self.rect  = self.image.get_rect(center=(x, y))


class CannonTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, base_cost=50)
        self.damage   = 30
        self.fire_rate = 90
        self.range    = 120
        img = pygame.image.load("assets/tower/tower.png")
        self.image = pygame.transform.scale(img, (50, 50))
        self.rect  = self.image.get_rect(center=(x, y))


class MagicTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, base_cost=40)
        self.damage   = 20
        self.fire_rate = 60
        img = pygame.image.load("assets/tower/magic_tower.png")
        self.image = pygame.transform.scale(img, (50, 50))
        self.rect  = self.image.get_rect(center=(x, y))


class IceTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, base_cost=20)
        self.damage        = 0     # no direct damage
        self.fire_rate     = 50
        self.slow_effect   = 0.5   # 50% speed
        self.slow_duration = 3000  # ms
        img = pygame.image.load("assets/tower/ice_tower.png")
        self.image = pygame.transform.scale(img, (50, 50))
        self.rect  = self.image.get_rect(center=(x, y))

    def shoot(self, enemies, current_time, projectiles, time_multiplier=1.0):
        if current_time - self.last_shot_time < (self.fire_rate / time_multiplier):
            return
        for e in enemies:
            if self.in_range(e):
                from projectile import Projectile
                proj = Projectile(
                    self.x, self.y, e,
                    damage=self.damage,
                    speed=7,
                    slow_effect=self.slow_effect,
                    slow_duration=self.slow_duration
                )
                proj.image.fill((0, 191, 255))
                projectiles.append(proj)
                self.last_shot_time = current_time
                break
