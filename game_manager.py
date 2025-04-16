import pygame
import math
from enemy import Enemy
from tower import Tower

class GameManager:
    def __init__(self, screen, map_obj):
        self.screen = screen
        self.map = map_obj
        self.enemies = []
        self.spawn_timer = 0
        self.spawn_interval = 1000  # ms
        self.start_time = pygame.time.get_ticks()
        self.player_money = 100
        self.wave = 1
        self.font = pygame.font.Font(None, 36)
        self.towers = []
        

    def update(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.spawn_timer >= self.spawn_interval:
            self.enemies.append(Enemy(self.map.path))
            self.spawn_timer = current_time

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.move()
            enemy.draw(self.screen)
            if not enemy.alive:
                self.enemies.remove(enemy)

        # Update towers
        for tower in self.towers:
            tower.shoot(self.enemies, current_time)
            tower.draw(self.screen)