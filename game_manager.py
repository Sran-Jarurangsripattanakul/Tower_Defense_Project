import pygame, sys, csv, os
from enemy import Goblin, Orc, Troll, Boss
from tower import ArcherTower, CannonTower, MagicTower, IceTower
from projectile import Projectile

class GameManager:
    def __init__(self, screen, map_obj, menu,
                 base_enemy_types=None,
                 boss_class=None):
        pygame.font.init()
        self.screen = screen
        self.map    = map_obj
        self.menu   = menu
        # Use Arial so we can render “≡”
        self.font   = pygame.font.SysFont("Arial", 36)

        # Enemy roster
        self.base_enemy_types = base_enemy_types or [Goblin, Orc, Troll]
        self.boss_class       = boss_class or Boss
        self.enemy_types      = list(self.base_enemy_types)

        # Game state
        self.enemies     = []
        self.projectiles = []
        self.towers      = []

        self.player_money = 100
        self.health       = 10

        # Wave control
        self.wave             = 14
        self.wave_in_progress = False
        self.victory          = False
        self.paused           = False
        self.game_over        = False

        # Spawning
        self.spawn_timer      = 0
        self.spawn_interval   = 800
        self.enemies_to_spawn = 0
        self.spawned_count    = 0
        self.is_boss_wave     = False

        # Manual start trigger
        self.manual_wave_trigger = False

        # Speed toggle
        self.time_multiplier = 1

        # Tower slots
        self.available_slots    = map_obj.get_tower_points()
        self.occupied_slots     = {}
        self.selected_slot      = None
        self.selected_tower     = None
        self.showing_tower_menu = False
        self.tower_icons        = {}
        self.tower_icon_rects   = []

        # UI buttons
        w, h = self.screen.get_size()
        self.wave_button_rect  = pygame.Rect(w-150,  80, 130, 40)
        self.speed_button_rect = pygame.Rect(w-150, 130, 130, 40)
        self.menu_button_rect  = pygame.Rect(w- 50,  10,  40, 40)

        # Victory/session stats
        self.session_wave_stats = []
        self._summary_shown     = False

        # Show/hide start button
        self.show_wave_button = True

        self.load_tower_icons()

        # CSV for stats
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
        self.tower_costs = {
            "archer": 30,
            "cannon": 50,
            "magic":  40,
            "ice":    20,
        }
        for kind, path in icons.items():
            img = pygame.image.load(path)
            self.tower_icons[kind] = pygame.transform.scale(img, (40, 40))

    def start_new_wave(self):
        self.spawned_count = 0
        self._reset_wave_stats()
        self.show_wave_button = False

        # Boss waves?
        if self.wave in (5, 10, 15):
            self.is_boss_wave     = True
            self.enemy_types      = [self.boss_class] + list(self.base_enemy_types)
            self.enemies_to_spawn = 1 + (5 + self.wave * 2)
        else:
            self.is_boss_wave     = False
            self.enemy_types      = list(self.base_enemy_types)
            self.enemies_to_spawn = 5 + self.wave * 2

        self.wave_in_progress   = True
        self.manual_wave_trigger = False

    def update(self):
        now = pygame.time.get_ticks()

        if self.paused:
            self._draw_pause_overlay()
            return
        if self.victory:
            self._draw_victory()
            return
        if self.game_over:
            self._draw_game_over()
            return

        # Handle manual start
        if not self.wave_in_progress and self.manual_wave_trigger:
            self.wave += 1
            if self.wave > 15:
                lvl = self.menu.selected_level
                # mark current level complete
                self.menu.level_progress[lvl]["completed"] = True
                # unlock next level
                next_level = f"level{int(lvl[-1]) + 1}"
                if next_level in self.menu.level_progress:
                    self.menu.level_progress[next_level]["completed"] = True
                self.menu.save_progress()
                self.victory = True
            else:
                self.start_new_wave()

        # Spawn enemies
        if self.wave_in_progress and self.spawned_count < self.enemies_to_spawn:
            if now - self.spawn_timer >= self.spawn_interval // self.time_multiplier:
                cls = (self.boss_class if self.is_boss_wave and self.spawned_count == 0
                       else self.enemy_types[self.spawned_count % len(self.enemy_types)])
                self.enemies.append(cls(self.map.path))
                self.spawned_count += 1
                self.spawn_timer = now

        # Update enemies
        for e in self.enemies[:]:
            e.move(self.time_multiplier)
            e.draw(self.screen)
            if not e.alive:
                self.enemies.remove(e)
                self.enemies_defeated += 1
                self.player_money   += 10
            elif e.current_point >= len(e.path) - 1:
                self.health -= 1
                self.enemies.remove(e)
                if self.health <= 0:
                    self.game_over = True
                    break

        # Update projectiles
        for p in self.projectiles[:]:
            p.update()
            p.draw(self.screen)
            if not p.alive:
                self.total_damage += getattr(p, "damage", 0)
                self.projectiles.remove(p)

        # Update towers
        for t in self.towers:
            t.shoot(self.enemies, now, self.projectiles, self.time_multiplier)
            t.draw(self.screen)

        # UI & selection
        self._draw_ui()
        self.draw_tower_selection()

        # Wave cleared?
        if (self.wave_in_progress
            and self.spawned_count == self.enemies_to_spawn
            and not self.enemies):
            wave_time = now - self._wave_start_time
            self.session_wave_stats.append({
                "wave": self.wave,
                "enemies": self.enemies_defeated,
                "damage": self.total_damage,
                "time_ms": wave_time,
                "currency_spent": self.currency_spent
            })

            # Trim & append CSV
            with open(self.stats_path, "r") as f:
                lines = f.readlines()
            header, data = lines[0], lines[1:]
            if len(data) >= 50:
                data = data[1:]
            with open(self.stats_path, "w") as f:
                f.writelines([header] + data)
            with open(self.stats_path, "a", newline="") as f:
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

            self._reset_wave_stats()
            self.wave_in_progress = False
            self.show_wave_button = True

    def handle_click(self, pos):
        if self.wave_button_rect.collidepoint(pos) and not self.wave_in_progress:
            self.manual_wave_trigger = True
            return
        if self.speed_button_rect.collidepoint(pos):
            self.time_multiplier = 2 if self.time_multiplier == 1 else 1
            return
        if self.menu_button_rect.collidepoint(pos):
            self.paused = True
            return

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
            self._sell_tower(); 
            return

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

    # ——— UI Helpers ———

    def _draw_ui(self):
        # HUD
        self.screen.blit(self.font.render(f"Money: {self.player_money}", True, (255, 255, 0)), (10, 10))
        self.screen.blit(self.font.render(f"Wave: {self.wave}", True, (255, 255, 255)), (10, 40))
        self.screen.blit(self.font.render(f"HP: {self.health}", True, (255, 100, 100)), (10, 70))

        # Start Wave / Finish button
        if self.show_wave_button:
            button_text = "Finish" if self.wave == 15 else "Start Wave"
            pygame.draw.rect(self.screen, (70, 70, 70), self.wave_button_rect, border_radius=8)
            lbl = self.font.render(button_text, True, (255, 255, 255))
            self.screen.blit(lbl, lbl.get_rect(center=self.wave_button_rect.center))

        # Speed button
        pygame.draw.rect(self.screen, (50, 50, 50), self.speed_button_rect, border_radius=8)
        sl = self.font.render(f"Speed x{self.time_multiplier}", True, (255, 255, 255))
        self.screen.blit(sl, self.speed_button_rect.move(10, 5))

        # Pause/Menu button
        pygame.draw.rect(self.screen, (200, 200, 200), self.menu_button_rect)
        mi = self.font.render("≡", True, (50, 50, 50))
        self.screen.blit(mi, mi.get_rect(center=self.menu_button_rect.center))



    def draw_tower_selection(self):
        # Placement icons
        if self.selected_slot and self.showing_tower_menu:
            x, y = self.selected_slot
            offs, sp = 50, 60
            self.tower_icon_rects = []

            for i, kind in enumerate(["archer", "cannon", "magic", "ice"]):
                # Draw icon
                ico = self.tower_icons[kind]
                rect = ico.get_rect(topleft=(x + offs, y - 60 + i * sp))
                self.screen.blit(ico, rect)
                self.tower_icon_rects.append((rect, kind))

                # Draw cost
                cost = self.tower_costs[kind]
                cost_text = self.font.render(f"${cost}", True, (255, 255, 255))
                self.screen.blit(cost_text, (x + offs + 50, y - 55 + i * sp))

        # Upgrade panel
        
        if self.selected_tower:
            x, y = self.selected_tower.x, self.selected_tower.y
            px, py = x + 50, y - 60

            # If not maxed, draw Upgrade button
            if self.selected_tower.level < 5:
                self.upgrade_button_rect = pygame.Rect(px, py, 100, 30)
                pygame.draw.rect(self.screen, (90,90,90), self.upgrade_button_rect, border_radius=6)
                u_lbl = self.font.render("Upgrade", True, (255,255,255))
                self.screen.blit(u_lbl, u_lbl.get_rect(center=self.upgrade_button_rect.center))
            else:
                # draw a disabled “MAX” badge instead
                max_rect = pygame.Rect(px, py, 100, 30)
                pygame.draw.rect(self.screen, (50,50,50), max_rect, border_radius=6)
                m_lbl = self.font.render("MAX", True, (200,200,200))
                self.screen.blit(m_lbl, m_lbl.get_rect(center=max_rect.center))

            # — Sell button (below upgrade) —
            sell_y = py + 40
            self.sell_button_rect = pygame.Rect(px, sell_y, 100, 30)
            pygame.draw.rect(self.screen, (150,50,50), self.sell_button_rect, border_radius=6)
            s_lbl = self.font.render("Sell", True, (255,255,255))
            self.screen.blit(s_lbl, s_lbl.get_rect(center=self.sell_button_rect.center))

            # — Stats panel (below sell) —
            sf = pygame.font.Font(None, 20)
            stats = [
                f"Lv: {self.selected_tower.level}",
                f"Dmg: {self.selected_tower.damage}",
                f"Rng: {self.selected_tower.range}",
                f"Rate: {self.selected_tower.fire_rate}",
                f"Next ${self.selected_tower.upgrade_cost}",
                f"Sell ${self.selected_tower.get_sell_value()}"
            ]
            for i, txt in enumerate(stats):
                line = sf.render(txt, True, (200,200,200))
                self.screen.blit(line, (px, sell_y + 40 + i*18))

    def _place_tower(self, kind):
        cost_map = {"archer":30, "cannon":50, "magic":40, "ice":20}
        cost = cost_map[kind]
        if self.player_money >= cost:
            # 1) Track spending and placement
            self.currency_spent  += cost
            self.towers_placed   += 1

            # 2) Deduct money and place tower
            cls = {
                "archer": ArcherTower,
                "cannon": CannonTower,
                "magic": MagicTower,
                "ice": IceTower
            }[kind]
            tw = cls(*self.selected_slot)
            self.towers.append(tw)
            self.occupied_slots[self.selected_slot] = tw
            self.player_money -= cost

        self.selected_slot = None
        self.showing_tower_menu = False


    def _draw_pause_overlay(self):
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h)); overlay.set_alpha(180); overlay.fill((0,0,0))
        self.screen.blit(overlay, (0,0))

        btn_w, btn_h = 200, 50
        cx, cy = w//2, h//2
        btns = [
            (pygame.Rect(cx-btn_w//2, cy-80, btn_w, btn_h), "Resume"),
            (pygame.Rect(cx-btn_w//2, cy,    btn_w, btn_h), "Restart"),
            (pygame.Rect(cx-btn_w//2, cy+80, btn_w, btn_h), "Main Menu"),
        ]
        for rect, label in btns:
            pygame.draw.rect(self.screen, (70,70,70), rect, border_radius=8)
            t = self.font.render(label, True, (255,255,255))
            self.screen.blit(t, t.get_rect(center=rect.center))

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if btns[0][0].collidepoint((mx,my)):
                    self.paused = False
                elif btns[1][0].collidepoint((mx,my)):
                    # restart level
                    self.__init__(self.screen, self.map, self.menu)
                elif btns[2][0].collidepoint((mx,my)):
                    from main_menu import MainMenu
                    pygame.display.set_mode((600,400))
                    MainMenu().run()

    def _draw_victory(self):
        w, h = self.screen.get_size()

        # Compute and cache the session summary (only once)
        if not self._summary_shown:
            stats = self.session_wave_stats
            W = len(stats)
            total_enemies = sum(s["enemies"] for s in stats)
            total_damage  = sum(s["damage"]   for s in stats)
            total_spent   = sum(s["currency_spent"] for s in stats)
            avg_time      = (sum(s["time_ms"] for s in stats) // W) if W else 0

            self._session_summary = {
                "Waves":         W,
                "Enemies":       total_enemies,
                "Damage":        total_damage,
                "Spent":         total_spent,
                "Avg Time (ms)": avg_time
            }
            self._summary_shown = True

        # Draw overlay
        overlay = pygame.Surface((w, h))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        self.screen.blit(overlay, (0,0))

        # Victory text
        txt = self.font.render("VICTORY!", True, (0,255,0))
        self.screen.blit(txt, txt.get_rect(center=(w//2, h//2 - 80)))

        # Session summary
        sf = pygame.font.Font(None, 24)
        sx, sy = w//2 - 150, h//2 - 40
        for i, (key, val) in enumerate(self._session_summary.items()):
            line = sf.render(f"{key}: {val}", True, (255,255,255))
            self.screen.blit(line, (sx, sy + i*30))

        # Main Menu button
        btn = pygame.Rect(w//2 - 60, h//2 + 100, 120, 40)
        pygame.draw.rect(self.screen, (50,50,50), btn, border_radius=8)
        lb = self.font.render("Main Menu", True, (255,255,255))
        self.screen.blit(lb, lb.get_rect(center=btn.center))

        # Handle click
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN and btn.collidepoint(pygame.mouse.get_pos()):
                # 1) Reset summary tracking
                self._summary_shown = False
                self.session_wave_stats.clear()
                # 2) Destroy the current game window
                pygame.display.quit()
                # 3) Re-initialize video & open main menu
                pygame.display.init()
                self.menu.screen = pygame.display.set_mode((600, 400))
                pygame.display.set_caption("Tower Defense – Main Menu")
                # 4) Switch MainMenu state
                self.menu.state = "main_menu"
                self.menu.game_started = False

    def _draw_game_over(self):
        w, h = self.screen.get_size()

        # Compute and cache the session summary (only once)
        if not self._summary_shown:
            stats = self.session_wave_stats
            W = len(stats)
            total_enemies = sum(s["enemies"] for s in stats)
            total_damage  = sum(s["damage"]   for s in stats)
            total_spent   = sum(s["currency_spent"] for s in stats)
            avg_time      = (sum(s["time_ms"] for s in stats) // W) if W else 0

            self._session_summary = {
                "Waves":         W,
                "Enemies":       total_enemies,
                "Damage":        total_damage,
                "Spent":         total_spent,
                "Avg Time (ms)": avg_time
            }
            self._summary_shown = True

        # Draw overlay
        overlay = pygame.Surface((w, h))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        self.screen.blit(overlay, (0,0))

        # Game Over text
        txt = self.font.render("GAME OVER", True, (255,0,0))
        self.screen.blit(txt, txt.get_rect(center=(w//2, h//2 - 80)))

        # Session summary
        sf = pygame.font.Font(None, 24)
        sx, sy = w//2 - 150, h//2 - 40
        for i, (key, val) in enumerate(self._session_summary.items()):
            line = sf.render(f"{key}: {val}", True, (255,255,255))
            self.screen.blit(line, (sx, sy + i*30))

        # Main Menu button
        btn = pygame.Rect(w//2 - 60, h//2 + 100, 120, 40)
        pygame.draw.rect(self.screen, (50,50,50), btn, border_radius=8)
        lb = self.font.render("Main Menu", True, (255,255,255))
        self.screen.blit(lb, lb.get_rect(center=btn.center))

        # Handle click
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN and btn.collidepoint(pygame.mouse.get_pos()):
                # 1) Reset summary tracking
                self._summary_shown = False
                self.session_wave_stats.clear()
                # 2) Destroy the current game window
                pygame.display.quit()
                # 3) Re-init video & open main menu
                pygame.display.init()
                self.menu.screen = pygame.display.set_mode((600, 400))
                pygame.display.set_caption("Tower Defense – Main Menu")
                # 4) Switch MainMenu state
                self.menu.state = "main_menu"
                self.menu.game_started = False

