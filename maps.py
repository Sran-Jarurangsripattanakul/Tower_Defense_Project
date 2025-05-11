import pygame
import pytmx
from pytmx.util_pygame import load_pygame
import heapq

class Map:
    def __init__(self, screen, map_path, tile_size=40):
        self.screen = screen
        self.tile_size = tile_size
        self.tmx_data = load_pygame(map_path)

        # Map in tiles
        self.width  = self.tmx_data.width
        self.height = self.tmx_data.height

        # Load visuals
        self.tiles = self._load_tiles()

        # Build a boolean grid of walkable (path) vs blocked
        self._build_grid()

        # Find the two endpoints of the path layer
        self.start_tile, self.goal_tile = self._find_path_endpoints()

        # Compute the pixel-perfect path once
        self.path = self._compute_pixel_path()

        # Tower points unchanged
        self.tower_points = self._load_tower_points()

        # Path debug draw settings
        self.path_color      = (255, 0, 0)
        self.path_thickness  = 3
        self.path_point_rad  = 5

    def _load_tiles(self):
        out = []
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        out.append((
                            pygame.transform.scale(tile, (self.tile_size, self.tile_size)),
                            x*self.tile_size, y*self.tile_size
                        ))
        return out

    def _build_grid(self):
        # True = walkable (path), False = blocked
        path_layer = self.tmx_data.get_layer_by_name("path")
        self.grid = []
        for y in range(path_layer.height):
            row = []
            for x in range(path_layer.width):
                row.append(path_layer.data[y][x] != 0)
            self.grid.append(row)

    def _find_path_endpoints(self):
        # collect all path tiles
        pts = [(r, c)
               for r in range(self.height)
               for c in range(self.width)
               if self.grid[r][c]]

        # function to count how many path-neighbors a tile has
        def neighbors(r,c):
            for dr,dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < self.height and 0 <= nc < self.width and self.grid[nr][nc]:
                    yield (nr,nc)

        # endpoints have exactly one neighbor
        ends = [pt for pt in pts if len(list(neighbors(*pt))) == 1]
        if len(ends) >= 2:
            return ends[0], ends[-1]
        else:
            # fallback: first and last in scan order
            return pts[0], pts[-1]

    def _astar(self, start, goal):
        """Returns list of (r,c) from start to goal or empty if none."""
        def h(a,b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
        open_set = [(h(start,goal), 0, start, None)]
        came_from = {}
        cost_so_far = {start: 0}

        while open_set:
            _, g, current, parent = heapq.heappop(open_set)
            if current in came_from:
                continue
            came_from[current] = parent
            if current == goal:
                break

            r, c = current
            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nbr = (r+dr, c+dc)
                if (0 <= nbr[0] < self.height and
                    0 <= nbr[1] < self.width  and
                    self.grid[nbr[0]][nbr[1]]):
                    new_cost = g + 1
                    if nbr not in cost_so_far or new_cost < cost_so_far[nbr]:
                        cost_so_far[nbr] = new_cost
                        f = new_cost + h(nbr, goal)
                        heapq.heappush(open_set, (f, new_cost, nbr, current))

        # reconstruct
        if goal not in came_from:
            return []
        path = []
        node = goal
        while node:
            path.append(node)
            node = came_from[node]
        return path[::-1]

    def _tile_to_pixel(self, r, c):
        return (c*self.tile_size + self.tile_size//2,
                r*self.tile_size + self.tile_size//2)

    def _compute_pixel_path(self):
        tile_path = self._astar(self.start_tile, self.goal_tile)
        return [self._tile_to_pixel(r, c) for r, c in tile_path]

    # Public API
    def draw(self):
        for img, x, y in self.tiles:
            self.screen.blit(img, (x,y))

    def draw_path(self):
        if len(self.path) > 1:
            pygame.draw.lines(self.screen, self.path_color, False,
                              self.path, self.path_thickness)
        for pt in self.path:
            pygame.draw.circle(self.screen, self.path_color,
                               pt, self.path_point_rad)

    def get_path(self):
        # return a fresh copy each time if you like:
        return self.path[:]

    def get_size(self):
        return (self.width*self.tile_size,
                self.height*self.tile_size)

    def _load_tower_points(self):
        out = []
        try:
            layer = self.tmx_data.get_layer_by_name("tower_layer")
            for y in range(layer.height):
                for x in range(layer.width):
                    if layer.data[y][x] != 0:
                        out.append(self._tile_to_pixel(y, x))
        except Exception as e:
            print(f"[Tower Point Error] {e}")
        return out

    def get_tower_points(self):
        return self.tower_points

    def draw_tower_slots(self):
        for px, py in self.tower_points:
            pygame.draw.circle(self.screen, (0, 255, 0), (px, py), 12)
            pygame.draw.circle(self.screen, (255, 255, 255), (px, py), 12, 2)
