import pygame, sys, csv, os
from enemy import Goblin, Orc, Troll, Boss
from tower import ArcherTower, CannonTower, MagicTower, IceTower
from projectile import Projectile

class GameManager:
    def __init__(self, screen, map_obj, menu):
        pygame.font.init()
        self.screen = screen
        self.map    = map_obj
        self.menu   = menu
        self.font   = pygame.font.Font(None, 36)

        # Game state
        self.enemies     = []
        self.projectiles = []
        self.towers      = []
        self.enemy_types = [Goblin, Orc, Troll]

        self.player_money = 100
        self.health       = 10

        # Wave control
        self.wave            = 0
        self.wave_in_progress = False
        self.victory          = False
        self.paused           = False
        self.game_over        = False

        # Spawning
        self.spawn_timer     = 0
        self.spawn_interval  = 800
        self.enemies_to_spawn = 0
        self.spawned_count    = 0
        self.is_boss_wave     = False

        # Manual start
        self.manual_wave_trigger = False

        # Speed toggle
        self.time_multiplier = 1

        # Tower slots
        self.available_slots = map_obj.get_tower_points()
        self.occupied_slots  = {}
        self.selected_slot   = None
        self.selected_tower  = None
        self.showing_tower_menu = False
        self.tower_icons     = {}
        self.tower_icon_rects = []

        # UI buttons
        w, h = self.screen.get_size()
        self.wave_button_rect  = pygame.Rect(w-150,  80, 130, 40)
        self.speed_button_rect = pygame.Rect(w-150, 130, 130, 40)
        self.menu_button_rect  = pygame.Rect(w- 50,  10,  40, 40)

        self.load_tower_icons()

        # Prepare CSV
        self.stats_path = "game_stats.csv"
        if not os.path.exists(self.stats_path):
            with open(self.stats_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Wave",
                    "Enemies Defeated",
                    "Towers Placed",
                    "Placement Effectiveness",
                    "Damage Dealt",
                    "Wave Time (ms)",
                    "Currency Spent"
                ])

        self._reset_wave_stats()

    def _reset_wave_stats(self):
        self.enemies_defeated = 0
        self.towers_placed    = 0
        self.total_damage     = 0
        self.currency_spent   = 0
        self._wave_start_time = pygame.time.get_ticks()

    def load_tower_icons(self):
        icons = {
            "archer": "assets/icon/archer_icon.png",
            "cannon": "assets/icon/cannon_icon.png",
            "magic":  "assets/icon/magic_icon.png",
            "ice":    "assets/icon/ice_icon.png",
        }
        for k, path in icons.items():
            img = pygame.image.load(path)
            self.tower_icons[k] = pygame.transform.scale(img, (40,40))

    def start_new_wave(self):
        self.spawned_count = 0
        self._reset_wave_stats()
        if self.wave in (5,10,15):
            self.is_boss_wave = True
            self.enemy_types  = [Boss, Goblin, Orc, Troll]
            self.enemies_to_spawn = 1 + (5 + self.wave*2)
        else:
            self.is_boss_wave = False
            self.enemy_types  = [Goblin, Orc, Troll]
            self.enemies_to_spawn = 5 + self.wave*2
        self.wave_in_progress  = True
        self.manual_wave_trigger = False

    def update(self):
        now = pygame.time.get_ticks()

        if self.paused:
            self._draw_pause_overlay(); return
        if self.victory:
            self._draw_victory(); return
        if self.game_over:
            self._draw_game_over(); return

        # start wave
        if not self.wave_in_progress and self.manual_wave_trigger:
            self.wave += 1
            if self.wave > 15:
                lvl = self.menu.selected_level
                self.menu.level_progress[lvl]["completed"] = True
                self.menu.save_progress()
                self.victory = True
            else:
                self.start_new_wave()

        # spawning
        if self.wave_in_progress and self.spawned_count < self.enemies_to_spawn:
            if now - self.spawn_timer >= self.spawn_interval // self.time_multiplier:
                cls = Boss if self.is_boss_wave and self.spawned_count==0 else \
                      self.enemy_types[self.spawned_count % len(self.enemy_types)]
                self.enemies.append(cls(self.map.path))
                self.spawned_count += 1
                self.spawn_timer = now

        # update enemies
        for e in self.enemies[:]:
            e.move(self.time_multiplier); e.draw(self.screen)
            if not e.alive:
                self.enemies.remove(e)
                self.enemies_defeated += 1
                self.player_money   += 10
            elif e.current_point >= len(e.path)-1:
                self.health -= 1
                self.enemies.remove(e)
                if self.health <= 0:
                    self.game_over = True
                    break

        # update projectiles
        for p in self.projectiles[:]:
            p.update(); p.draw(self.screen)
            if not p.alive:
                self.total_damage += getattr(p, "damage", 0)
                self.projectiles.remove(p)

        # update towers
        for t in self.towers:
            t.shoot(self.enemies, now, self.projectiles, self.time_multiplier)
            t.draw(self.screen)

        # UI
        self._draw_ui()
        self.draw_tower_selection()

        # wave cleared?
        if (self.wave_in_progress
            and self.spawned_count == self.enemies_to_spawn
            and not self.enemies):

            wave_time = now - self._wave_start_time
            path = self.stats_path

            # trim to 49 rows if needed
            with open(path, "r") as f:
                lines = f.readlines()
            header, data = lines[0], lines[1:]
            if len(data) >= 50:
                data = data[1:]
            with open(path, "w") as f:
                f.writelines([header] + data)

            # append
            with open(path, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    self.wave,
                    self.enemies_defeated,
                    self.towers_placed,
                    round(self.enemies_defeated / max(1, self.towers_placed), 2),
                    self.total_damage,
                    wave_time,
                    self.currency_spent
                ])

            self.wave_in_progress = False

    def handle_click(self, pos):
        if self.wave_button_rect.collidepoint(pos) and not self.wave_in_progress:
            self.manual_wave_trigger = True; return
        if self.speed_button_rect.collidepoint(pos):
            self.time_multiplier = 2 if self.time_multiplier==1 else 1; return
        if self.menu_button_rect.collidepoint(pos):
            self.paused = True; return

        # Sell first
        if self.selected_tower and hasattr(self, "sell_button_rect") \
           and self.sell_button_rect.collidepoint(pos):
            self._sell_tower(); return

        # Upgrade
        if self.selected_tower and self.upgrade_button_rect.collidepoint(pos):
            cost = self.selected_tower.upgrade_cost
            if self.player_money >= cost:
                self.currency_spent += cost
                self.player_money  -= cost
                self.selected_tower.upgrade()
            return

        # tower placement menu...
        if self.showing_tower_menu:
            for rect, kind in self.tower_icon_rects:
                if rect.collidepoint(pos):
                    self._place_tower(kind); return
            self.selected_slot = None; self.showing_tower_menu = False; return

        # select/deselect slots & towers
        for slot, tw in self.occupied_slots.items():
            dx, dy = pos[0]-slot[0], pos[1]-slot[1]
            if dx*dx+dy*dy <= 20*20:
                self.selected_tower = tw; return
        for slot in self.available_slots:
            if slot not in self.occupied_slots:
                dx, dy = pos[0]-slot[0], pos[1]-slot[1]
                if dx*dx+dy*dy <= 15*15:
                    self.selected_slot = slot; self.showing_tower_menu = True; return
        self.selected_tower = None

    def _place_tower(self, kind):
        cost_map = {"archer":30,"cannon":50,"magic":40,"ice":20}
        cost = cost_map[kind]
        if self.player_money >= cost:
            self.currency_spent += cost
            self.towers_placed  += 1
            cls = {"archer":ArcherTower,"cannon":CannonTower,
                   "magic":MagicTower,"ice":IceTower}[kind]
            tw = cls(*self.selected_slot)
            self.towers.append(tw)
            self.occupied_slots[self.selected_slot] = tw
            self.player_money -= cost
        self.selected_slot = None
        self.showing_tower_menu = False

    def _sell_tower(self):
        tw = self.selected_tower
        refund = tw.get_sell_value()
        self.player_money += refund
        for slot, tower in list(self.occupied_slots.items()):
            if tower is tw:
                del self.occupied_slots[slot]
                break
        self.towers.remove(tw)
        self.selected_tower = None

    # … (keep your existing _draw_ui, _draw_pause_overlay,
    #      _draw_victory, _draw_game_over methods) …

    def draw_tower_selection(self):
        if self.selected_slot and self.showing_tower_menu:
            # … tower icons …
            return

        if self.selected_tower:
            x, y = self.selected_tower.x, self.selected_tower.y
            px, py = x+50, y-60
            # Upgrade
            self.upgrade_button_rect = pygame.Rect(px, py, 100, 30)
            pygame.draw.rect(self.screen, (90,90,90),
                             self.upgrade_button_rect, border_radius=6)
            lbl = self.font.render("Upgrade", True, (255,255,255))
            self.screen.blit(lbl, lbl.get_rect(center=self.upgrade_button_rect.center))

            # Sell
            sell_y = py + 40
            self.sell_button_rect = pygame.Rect(px, sell_y, 100, 30)
            pygame.draw.rect(self.screen, (150,50,50),
                             self.sell_button_rect, border_radius=6)
            sell_lbl = self.font.render("Sell", True, (255,255,255))
            self.screen.blit(sell_lbl,
                             sell_lbl.get_rect(center=self.sell_button_rect.center))

            # … and then draw the tower stats below …

