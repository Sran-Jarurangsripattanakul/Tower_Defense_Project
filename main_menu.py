# main_menu.py

import pygame
import json
from maps import Map
from game_manager import GameManager

class MainMenu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 400))
        pygame.display.set_caption("Tower Defense – Main Menu")
        self.font = pygame.font.Font(None, 50)
        self.button_font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        self.state = "main_menu"
        self.running = True
        self.game_started = False
        self.selected_level = "level1"    # default

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
            return {
                "level1": {"file": "assets/level1.tmx", "completed": False},
                "level2": {"file": "assets/level2.tmx", "completed": False},
                "level3": {"file": "assets/level3.tmx", "completed": False},
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

    def _show_main_menu(self):
        self.screen.blit(self.background, (0, 0))
        title = self.font.render("Tower Defense", True, self.WHITE)
        self.screen.blit(title, title.get_rect(center=(300, 60)))

        self.draw_button("Start Game", 200, 150, 200, 60, self.GRAY, self.LIGHT_GRAY)
        self.draw_button("Levels",     200, 230, 200, 60, self.GRAY, self.LIGHT_GRAY)
        self.draw_button("Quit",       200, 310, 200, 60, self.GRAY, self.LIGHT_GRAY)
        self._handle_main_menu_events()

    def _handle_main_menu_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # Start Game
                if 200 <= mx <= 400 and 150 <= my <= 210:
                    self.state = "game"
                # Levels
                elif 200 <= mx <= 400 and 230 <= my <= 290:
                    self.state = "level_select"
                # Quit
                elif 200 <= mx <= 400 and 310 <= my <= 370:
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

        self.draw_button(
            "Back",
            200, 150 + len(self.level_progress) * 80,
            200, 60,
            self.GRAY, self.LIGHT_GRAY
        )
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
                    # Back button
                    yb = 150 + len(self.level_progress) * 80
                    if 200 <= mx <= 400 and yb <= my <= yb + 60:
                        self.state = "main_menu"

    def _start_game(self):
        # Which level file to load
        level = getattr(self, "selected_level", "level1")
        map_path = self.level_progress[level]["file"]
        self.map = Map(self.screen, map_path, tile_size=40)

        w, h = self.map.get_size()
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption("Tower Defense – Game")

        # Pass self into GameManager for save_progress callback
        self.game_manager = GameManager(self.screen, self.map, self)
        self.game_started = True

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
