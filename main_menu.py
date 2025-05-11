import pygame
import sys
import json
import glob, os
from maps import Map
from game_manager import GameManager
from enemy import (
    Goblin, Orc, Troll, Boss,
    Slime, Werewolf, Werebear, OrcRider
)

class MainMenu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 400))
        pygame.display.set_caption("Tower Defense – Main Menu")
        self.font        = pygame.font.Font(None, 50)
        self.button_font = pygame.font.Font(None, 36)
        self.clock       = pygame.time.Clock()
        self.state       = "main_menu"
        self.running     = True
        self.game_started = False
        self.selected_level = "level1"

        # Load or initialize level progress
        self.level_progress = self._load_progress()

        # Preload background
        bg = pygame.image.load("assets/background.jpg")
        self.background = pygame.transform.scale(bg, (600, 400))

        # Button colors
        self.WHITE      = (255, 255, 255)
        self.GRAY       = (70, 70, 70)
        self.LIGHT_GRAY = (150, 150, 150)
        self.GREEN      = (34, 139, 34)
        self.RED        = (255, 0, 0)

    def _load_progress(self):
        try:
            with open("assets/maps.json", "r") as f:
                return json.load(f)["levels"]
        except FileNotFoundError:
            # default if no file
            return {
                "level1": {"file": "assets/level1.tmx", "completed": False},
                "level2": {"file": "assets/level2.tmx", "completed": False},
            }

    def save_progress(self):
        with open("assets/maps.json", "w") as f:
            json.dump({"levels": self.level_progress}, f, indent=2)

    def draw_button(self, text, x, y, w, h, color, hover_color):
        mx, my = pygame.mouse.get_pos()
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(
            self.screen,
            hover_color if rect.collidepoint(mx, my) else color,
            rect,
            border_radius=10
        )
        label = self.button_font.render(text, True, self.WHITE)
        self.screen.blit(label, label.get_rect(center=rect.center))

    def run(self):
        while self.running:
            if self.state == "main_menu":
                self._show_main_menu()
            elif self.state == "level_select":
                self._show_level_selection()
            elif self.state == "game":
                self._start_game()

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()
        sys.exit()

    def _show_main_menu(self):
        self.screen.blit(self.background, (0, 0))
        title = self.font.render("Tower Defense", True, self.WHITE)
        self.screen.blit(title, title.get_rect(center=(300, 60)))

        # Only Levels & Quit
        self.draw_button("Levels", 200, 150, 200, 60, self.GRAY, self.LIGHT_GRAY)
        self.draw_button("Quit",   200, 230, 200, 60, self.GRAY, self.LIGHT_GRAY)
        self._handle_main_menu_events()

    def _handle_main_menu_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # Levels
                if 200 <= mx <= 400 and 150 <= my <= 210:
                    self.state = "level_select"
                # Quit
                elif 200 <= mx <= 400 and 230 <= my <= 290:
                    self.running = False

    def _show_level_selection(self):
        self.screen.fill((0, 0, 0))
        title = self.font.render("Select Level", True, self.WHITE)
        self.screen.blit(title, title.get_rect(center=(300, 60)))

        for i, (name, data) in enumerate(self.level_progress.items()):
            color = self.GREEN if data.get("completed") else self.RED
            self.draw_button(
                name.capitalize(),
                200, 150 + i * 80,
                200, 60,
                color, self.LIGHT_GRAY
            )

        # Back button
        back_y = 150 + len(self.level_progress) * 80
        self.draw_button("Back", 200, back_y, 200, 60, self.GRAY, self.LIGHT_GRAY)
        self._handle_level_select_events()

    def _handle_level_select_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # Level buttons
                for i, (name, data) in enumerate(self.level_progress.items()):
                    y0 = 150 + i * 80
                    if 200 <= mx <= 400 and y0 <= my <= y0 + 60:
                        if data.get("completed"):
                            self.selected_level = name
                            self.state = "game"
                        else:
                            print(f"{name} is locked!")
                        break
                else:
                    # Back
                    back_y = 150 + len(self.level_progress) * 80
                    if 200 <= mx <= 400 and back_y <= my <= back_y + 60:
                        self.state = "main_menu"

    def _show_enemy_info_modal(self):
        w, h = self.screen.get_size()
        info_map = {
            Goblin:    ("Goblin",    "assets/enemy/skel/right",      "HP:50  Spd:2.0"),
            Orc:       ("Orc",       "assets/enemy/orc/right",       "HP:150 Spd:0.8"),
            Troll:     ("Troll",     "assets/enemy/troll/right",     "HP:250 Spd:0.5"),
            Boss:      ("Boss",      "assets/enemy/boss/right",      "HP:1000 Spd:0.7"),
            Slime:     ("Slime",     "assets/enemy/slime/right","HP:200 Spd:1.5"),
            Werewolf:  ("Werewolf",  "assets/enemy/werewolf/right","HP:300 Spd:1.8"),
            Werebear:  ("Werebear",  "assets/enemy/werebear/right","HP:500 Spd:0.6"),
            OrcRider:  ("OrcRider",  "assets/enemy/orcrider/right","HP:400 Spd:1.2"),
        }
        types = getattr(self, "_level_enemy_types", [Goblin, Orc, Troll, Boss])
        entries = []
        for cls in types:
            name, folder, stats = info_map.get(cls, (cls.__name__, "", ""))
            files = sorted(glob.glob(os.path.join(folder, "*.png")))
            icon = files[0] if files else None
            entries.append((name, icon, stats))

        cont_rect = pygame.Rect(w//2 - 60, h - 100, 120, 40)
        clock = pygame.time.Clock()
        showing = True

        while showing:
            # dark overlay
            overlay = pygame.Surface((w, h))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            # title
            title = self.font.render("Enemies You'll Face", True, self.WHITE)
            self.screen.blit(title, title.get_rect(center=(w//2, 60)))

            # icon sizing & spacing
            ICON_SIZE = 80
            SPACING   = ICON_SIZE + 20
            y = 120

            # draw each entry
            for name, icon_path, stats in entries:
                if icon_path:
                    img = pygame.image.load(icon_path).convert_alpha()
                    img = pygame.transform.scale(img, (ICON_SIZE, ICON_SIZE))
                    self.screen.blit(img, (w//2 - 200, y))

                # vertically center the text next to the icon
                text_y = y + ICON_SIZE // 2 - 10
                t_name  = self.button_font.render(name,  True, self.WHITE)
                t_stats = self.button_font.render(stats, True, self.LIGHT_GRAY)
                self.screen.blit(t_name,  (w//2 - 130, text_y))
                self.screen.blit(t_stats, (w//2 - 130, text_y + 24))

                y += SPACING

            # continue button
            pygame.draw.rect(self.screen, self.GRAY, cont_rect, border_radius=8)
            lbl = self.button_font.render("Continue", True, self.WHITE)
            self.screen.blit(lbl, lbl.get_rect(center=cont_rect.center))

            pygame.display.flip()
            clock.tick(30)

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    if cont_rect.collidepoint(pygame.mouse.get_pos()):
                        showing = False


    def _start_game(self):
        level = self.selected_level

        # ── Define minion roster & boss per level
        roster_map = {
            "level1": [Slime, Werewolf, Werebear],
            "level2": [Goblin, Orc, Troll]
        }
        boss_map = {
            "level1": OrcRider,
            "level2": Boss
        }
        base_enemy_types = roster_map.get(level, [Goblin, Orc, Troll])
        boss_class       = boss_map.get(level, Boss)
        # ─────────────────────────────────────

        # Load map
        map_path = self.level_progress[level]["file"]
        self.map = Map(self.screen, map_path, tile_size=40)

        # Resize window
        w, h = self.map.get_size()
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption("Tower Defense – Game")

        # Pass roster & boss into GameManager
        self.game_manager = GameManager(
            self.screen,
            self.map,
            self,
            base_enemy_types=base_enemy_types,
            boss_class=boss_class
        )
        self.game_started = True

        # Prepare enemy‐preview modal
        roster = self.game_manager.enemy_types.copy()
        if boss_class not in roster:
            roster.insert(0, boss_class)
        self._level_enemy_types = roster

        self._show_enemy_info_modal()

        # Game loop
        while self.game_started:
            self.screen.fill((0, 0, 0))
            self.map.draw()
            self.map.draw_path()
            self.map.draw_tower_slots()
            self.game_manager.update()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                    self.game_started = False
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    self.game_manager.handle_click(pygame.mouse.get_pos())

            pygame.display.flip()
            self.clock.tick(30)


if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
