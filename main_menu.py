import pygame
import json
from maps import Map
from game_manager import GameManager
from tower import Tower

class MainMenu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 400))
        pygame.display.set_caption("Tower Defense - Main Menu")
        self.font = pygame.font.Font(None, 50)
        self.button_font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        self.state = "main_menu"
        self.game_start_time = None

        # Background
        self.background = pygame.image.load("assets/background.jpg")
        self.background = pygame.transform.scale(self.background, (600, 400))

        # Colors
        self.WHITE = (255, 255, 255)
        self.GRAY = (70, 70, 70)
        self.LIGHT_GRAY = (150, 150, 150)
        self.GREEN = (34, 139, 34)
        self.RED = (255, 0, 0)

        self.running = True
        self.game_started = False
        self.map = None
        self.back_button_rect = pygame.Rect(0, 0, 0, 0)

        self.level_progress = self.load_progress()

    def load_progress(self):
        try:
            with open("assets/maps.json", "r") as f:
                data = json.load(f)
                return data["levels"]
        except FileNotFoundError:
            return {
                "level1": {"completed": False},
                "level2": {"completed": False},
                "level3": {"completed": False},
            }

    def save_progress(self):
        with open("assets/maps.json", "w") as f:
            json.dump({"levels": self.level_progress}, f)

    def draw_button(self, text, x, y, w, h, color, hover_color, text_color):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        button_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, hover_color if button_rect.collidepoint(mouse_x, mouse_y) else color, button_rect, border_radius=10)
        label = self.button_font.render(text, True, text_color)
        text_rect = label.get_rect(center=(x + w // 2, y + h // 2))
        self.screen.blit(label, text_rect)

    def run(self):
        while self.running:
            if self.state == "main_menu":
                self.show_main_menu()
            elif self.state == "level_select":
                self.show_level_selection()
            elif self.state == "game":
                self.start_game()

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()

    def show_main_menu(self):
        self.screen.blit(self.background, (0, 0))
        title_text = self.font.render("Tower Defense Game", True, self.WHITE)
        self.screen.blit(title_text, title_text.get_rect(center=(300, 60)))
        self.draw_button("Start Game", 200, 150, 200, 60, self.GRAY, self.LIGHT_GRAY, self.WHITE)
        self.draw_button("Level", 200, 230, 200, 60, self.GRAY, self.LIGHT_GRAY, self.WHITE)
        self.draw_button("Quit", 200, 310, 200, 60, self.GRAY, self.LIGHT_GRAY, self.WHITE)
        self.handle_events()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if not self.game_started:
                    if 200 <= mx <= 400 and 150 <= my <= 210:
                        print("Start Game clicked!")
                        self.state = "game"
                    elif 200 <= mx <= 400 and 230 <= my <= 290:
                        print("Level clicked!")
                        self.state = "level_select"
                    elif 200 <= mx <= 400 and 310 <= my <= 370:
                        self.running = False

    def start_game(self, level_name="level1"):
        print(f"Starting Game with {level_name}...")

        # Setup map and screen size
        level_data = self.level_progress[level_name]
        map_path = level_data["file"]
        self.map = Map(self.screen, map_path, tile_size=40)
        map_width, map_height = self.map.get_size()  # Get map size after initializing it properly
        screen_size = (map_width, map_height)  # Adjust screen size to only fit the map
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("Tower Defense - Game")

        self.game_manager = GameManager(self.screen, self.map)
        self.game_manager.towers.append(Tower(450, 200))  # Example tower placement
        self.game_started = True
        self.game_start_time = pygame.time.get_ticks()

        while self.game_started:
            self.screen.fill((0, 0, 0))
            self.map.draw()
            self.map.draw_path()
            self.game_manager.update()

            # Draw the back button at the top right
            self.back_button_rect = pygame.Rect(self.screen.get_width() - 110, 10, 100, 40)
            self.draw_button("Back", *self.back_button_rect, self.GRAY, self.LIGHT_GRAY, self.WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.game_started = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.back_button_rect.collidepoint(pygame.mouse.get_pos()):
                        # Destroy current game window and reset screen
                        self.game_started = False
                        self.state = "main_menu"
                        self.screen = pygame.display.set_mode((600, 400))  # Reset to main menu size
                        pygame.display.set_caption("Tower Defense - Main Menu")

            pygame.display.flip()
            self.clock.tick(30)


    def draw_sidebar(self):
        sidebar_x = self.map.get_size()[0]
        sidebar_rect = pygame.Rect(sidebar_x, 0, 200, self.map.get_size()[1])
        pygame.draw.rect(self.screen, (40, 40, 40), sidebar_rect)

        money = 100
        time_elapsed = (pygame.time.get_ticks() - self.game_start_time) // 1000 if self.game_start_time else 0
        wave = 1

        money_text = self.button_font.render(f"Money: ${money}", True, self.WHITE)
        time_text = self.button_font.render(f"Time: {time_elapsed}s", True, self.WHITE)
        wave_text = self.button_font.render(f"Wave: {wave}", True, self.WHITE)

        self.back_button_rect = pygame.Rect(sidebar_x + 10, 180, 180, 50)
        self.draw_button("Back", *self.back_button_rect, self.GRAY, self.LIGHT_GRAY, self.WHITE)

        self.screen.blit(money_text, (sidebar_x + 10, 30))
        self.screen.blit(time_text, (sidebar_x + 10, 80))
        self.screen.blit(wave_text, (sidebar_x + 10, 130))

    def show_level_selection(self):
        self.screen.fill((0, 0, 0))
        title_text = self.font.render("Select Level", True, self.WHITE)
        self.screen.blit(title_text, title_text.get_rect(center=(300, 60)))

        for i, (level_name, level_data) in enumerate(self.level_progress.items()):
            color = self.GREEN if level_data["completed"] else self.RED
            self.draw_button(level_name.capitalize(), 200, 150 + i * 80, 200, 60, color, self.LIGHT_GRAY, self.WHITE)

        self.draw_button("Back", 200, 150 + len(self.level_progress) * 80, 200, 60, self.GRAY, self.LIGHT_GRAY, self.WHITE)
        self.handle_level_selection()

    def handle_level_selection(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.game_started = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for i, (level_name, level_data) in enumerate(self.level_progress.items()):
                    if 200 <= mx <= 400 and 150 + i * 80 <= my <= 210 + i * 80:
                        if level_data["completed"]:
                            self.start_game(level_name)
                        else:
                            print(f"{level_name.capitalize()} is locked!")
                        return
                if 200 <= mx <= 400 and 150 + len(self.level_progress) * 80 <= my <= 210 + len(self.level_progress) * 80:
                    self.state = "main_menu"

if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
