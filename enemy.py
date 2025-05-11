import pygame
import math
import glob
import os

class Enemy:
    def __init__(self, path):
        if not path:
            raise ValueError("Enemy path is empty. Ensure your TMX map defines a proper path.")
        # Path & movement
        self.path = path
        self.current_point = 0
        self.x, self.y = path[0]
        self.alive = True

        # Health
        self.health = 100
        self.max_health = 100

        # Speed + slow
        self.speed = 1.0
        self.original_speed = self.speed
        self.slow_until = 0

        # which way we're facing
        self.frames_right = []
        self.frames_left  = []
        self.frames       = self.frames_right

        # Animation timing
        self.frame_index    = 0
        self.frame_interval = 100
        self.last_frame_time = pygame.time.get_ticks()

        # fallback circle
        self.image = pygame.Surface((20,20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255,0,0), (10,10), 10)

    def update_animation(self, now):
        if not self.frames:
            return
        if now - self.last_frame_time >= self.frame_interval:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.last_frame_time = now

    def move(self, time_multiplier=1.0):
        now = pygame.time.get_ticks()
        self.update_animation(now)

        # revert any slow
        if now > self.slow_until:
            self.speed = self.original_speed

        # end of path?
        if self.current_point + 1 >= len(self.path):
            self.alive = False
            return

        # step & direction
        step = self.speed * time_multiplier
        tx, ty = self.path[self.current_point + 1]
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx /= dist
            dy /= dist

        # choose frames based on x‐direction
        if dx < 0:
            self.frames = self.frames_left
        else:
            self.frames = self.frames_right

        # move
        self.x += dx * step
        self.y += dy * step

        # snap if close
        if dist <= step:
            self.current_point += 1
            self.x, self.y = float(tx), float(ty)

    def draw(self, surface):
        if self.frames:
            frame = self.frames[self.frame_index]
            w, h = frame.get_size()
            surface.blit(frame, (int(self.x)-w//2, int(self.y)-h//2))
        else:
            surface.blit(self.image, (int(self.x)-10, int(self.y)-10))

        # health bar
        bar_w, bar_h = 20, 4
        health_ratio = max(self.health,0)/self.max_health
        bx = int(self.x)-bar_w//2
        by = int(self.y)-(h//2)-6
        pygame.draw.rect(surface, (150,0,0), (bx,by,bar_w,bar_h))
        pygame.draw.rect(surface, (0,255,0), (bx,by,int(bar_w*health_ratio),bar_h))

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.alive = False

    def apply_slow(self, multiplier, duration_ms, current_time):
        self.speed = self.original_speed * multiplier
        self.slow_until = current_time + duration_ms

    def is_alive(self):
        return self.alive

def load_frames(folder, size):
    """Helper: load all PNGs from folder, scale to size×size."""
    files = sorted(glob.glob(os.path.join(folder, "*.png")))
    frames = []
    for fn in files:
        img = pygame.image.load(fn).convert_alpha()
        frames.append(pygame.transform.scale(img, (size, size)))
    return frames

def load_bidirectional_frames(base_folder, size):
    """Load right and left. If left folder empty, flip right."""
    right = load_frames(os.path.join(base_folder, "right"), size)
    left  = load_frames(os.path.join(base_folder, "left"), size)
    if not left:
        # auto‐flip right into left
        left = [pygame.transform.flip(f, True, False) for f in right]
    return right, left

# ─── Subclasses ──────────────────────────────────────────────

class Goblin(Enemy):
    def __init__(self, path):
        super().__init__(path)
        folder = os.path.join("assets","enemy","skel")
        r, l = load_bidirectional_frames(folder, 150)
        self.frames_right = r
        self.frames_left  = l
        self.frames       = self.frames_right
        self.health       = 50;  self.max_health = 50
        self.speed        = 2.0; self.original_speed = self.speed

class Orc(Enemy):
    def __init__(self, path):
        super().__init__(path)
        folder = os.path.join("assets","enemy","orc")
        r, l = load_bidirectional_frames(folder, 150)
        self.frames_right = r
        self.frames_left  = l
        self.frames       = self.frames_right
        self.health       = 150; self.max_health = 150
        self.speed        = 0.8; self.original_speed = self.speed

class Troll(Enemy):
    def __init__(self, path):
        super().__init__(path)
        folder = os.path.join("assets","enemy","troll")
        r, l = load_bidirectional_frames(folder, 150)
        self.frames_right = r
        self.frames_left  = l
        self.frames       = self.frames_right
        self.health       = 250; self.max_health = 250
        self.speed        = 0.5; self.original_speed = self.speed

class Boss(Enemy):
    def __init__(self, path):
        super().__init__(path)
        folder = os.path.join("assets","enemy","boss")
        r, l = load_bidirectional_frames(folder, 150)
        self.frames_right = r
        self.frames_left  = l
        self.frames       = self.frames_right
        self.health       = 1000; self.max_health = 1000
        self.speed        = 0.7;   self.original_speed = self.speed

class Slime(Enemy):
    def __init__(self, path):
        super().__init__(path)
        folder = os.path.join("assets","enemy","slime")
        r, l = load_bidirectional_frames(folder, 150)
        self.frames_right = r
        self.frames_left  = l
        self.frames       = self.frames_right
        self.health       = 200; self.max_health = 200
        self.speed        = 1.5; self.original_speed = self.speed

class Werewolf(Enemy):
    def __init__(self, path):
        super().__init__(path)
        folder = os.path.join("assets","enemy","werewolf")
        r, l = load_bidirectional_frames(folder, 150)
        self.frames_right = r
        self.frames_left  = l
        self.frames       = self.frames_right
        self.health       = 300; self.max_health = 300
        self.speed        = 1.8; self.original_speed = self.speed

class Werebear(Enemy):
    def __init__(self, path):
        super().__init__(path)
        folder = os.path.join("assets","enemy","werebear")
        r, l = load_bidirectional_frames(folder, 150)
        self.frames_right = r
        self.frames_left  = l
        self.frames       = self.frames_right
        self.health       = 500; self.max_health = 500
        self.speed        = 0.6; self.original_speed = self.speed

class OrcRider(Enemy):
    def __init__(self, path):
        super().__init__(path)
        folder = os.path.join("assets","enemy","orcrider")
        r, l = load_bidirectional_frames(folder, 150)
        self.frames_right = r
        self.frames_left  = l
        self.frames       = self.frames_right
        self.health       = 400; self.max_health = 400
        self.speed        = 1.2; self.original_speed = self.speed
