import pygame
import pytmx
from pytmx.util_pygame import load_pygame

class Map:
    def __init__(self, screen, map_path, tile_size=40):
        self.screen = screen
        self.tile_size = tile_size
        self.tmx_data = load_pygame(map_path)

        # Map size in pixels
        self.width = self.tmx_data.width * self.tile_size
        self.height = self.tmx_data.height * self.tile_size

        self.tiles = self._load_tiles()
        self.path = self._load_tile_path()

        self.path_color = (255, 0, 0)
        self.path_thickness = 3
        self.path_point_radius = 5

    def _load_tiles(self):
        tiles = []
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        scaled_tile = pygame.transform.scale(tile, (self.tile_size, self.tile_size))
                        tiles.append((scaled_tile, x * self.tile_size, y * self.tile_size))
        return tiles

    def _load_tile_path(self):
        path_tiles = []
        path_layer = self.tmx_data.get_layer_by_name("path")

        for y in range(path_layer.height):
            for x in range(path_layer.width):
                gid = path_layer.data[y][x]
                if gid != 0:
                    # Center of the tile
                    screen_x = x * self.tile_size + self.tile_size // 2
                    screen_y = y * self.tile_size + self.tile_size // 2
                    path_tiles.append((screen_x, screen_y))

        return path_tiles


    def draw(self):
        for tile, x, y in self.tiles:
            self.screen.blit(tile, (x, y))

    def draw_path(self):
        if len(self.path) > 1:
            pygame.draw.lines(self.screen, self.path_color, False, self.path, self.path_thickness)
        for point in self.path:
            pygame.draw.circle(self.screen, self.path_color, point, self.path_point_radius)

    def get_path(self):
        return self.path.copy()

    def get_size(self):
        return (self.width, self.height)
