# villain.py

import pygame
from loader import TILE_SIZE
from logger import conlog
from visualeffects import hue_shift_sprite
from movement import *

class Villain:
    def __init__(self, map_data, spawn_xy, hue_shift=0, index=0, total=1):
        self.index = index
        self.name = f"Villain{index}"
        self.MOVE_SPEED = self.compute_speed(index, total)
        self.sprites = self.load_villain_sprites(hue_shift)
        self.frame = 0
        self.timer = 0
        self.x, self.y = spawn_xy
        self.facing_left = False
        self.seek_ladder = False
        self.seek_dx = 0


    def compute_speed(self, index, total):
        min_speed = 1.2
        max_speed = 1.8
        t = index / max(1, total - 1)
        return min_speed + t * (max_speed - min_speed)


    def load_villain_sprites(self, hue_shift):
        sheet = pygame.image.load("assets/sprites/sheet.png").convert_alpha()
        base_sprites = [
            sheet.subsurface(pygame.Rect(i * TILE_SIZE, TILE_SIZE, TILE_SIZE, TILE_SIZE))
            for i in range(4)
        ]
        return [hue_shift_sprite(sprite, hue_shift) for sprite in base_sprites]

    def find_spawn(self, map_data):
        for y, row in enumerate(map_data):
            for x, char in enumerate(row):
                if char == 'V':
                    return x * TILE_SIZE, y * TILE_SIZE
        return 0, 0

    def update(self, player, map_data):
        self.timer += 1
        maybe_snap_to_floor(self, map_data)
        if self.timer % 10 == 0:
            self.frame = (self.frame + 1) % len(self.sprites)
        cx, cy = get_tile_position(self)
        current_tile = map_data[cy][cx]
        if current_tile == 'F':
            conlog(f"[{self.name}] Inside floor at ({cx},{cy}), nudging up and canceling downward motion")
            self.y -= 1.0  # small upward nudge
            if hasattr(self, 'climb_dy') and self.climb_dy > 0:
                self.climb_dy = 0
                self.has_started_climbing = False
            return  # skip this frame
        if self.seek_ladder:
            #conlog("seek ladder mode active")
            self.facing_left = self.seek_dx > 0
            if on_ladder(self, map_data):
                if self.try_climb(player, map_data, cx, cy):
                    if valid_floor_below(self, map_data):
                        self.seek_ladder = False
                return
            else:
                try_move(self, self.seek_dx, 0, map_data)
                return
        if current_tile in ['L', 'U', 'D', 'E', 'T']:
            #conlog("standing on ladder")
            if self.try_climb(player, map_data, cx, cy):
                return
        if self.is_aligned_with_player(player):
            self.try_climb(player, map_data, cx, cy)
        delta_x = player.x - self.x
        if abs(delta_x) >= 1.0:
            dx = 1 if delta_x > 0 else -1
            self.facing_left = dx > 0
            # log_surrounding_tiles(self, map_data)
            success = try_move(self, dx, 0, map_data)
            if not success:
                cx, cy = get_tile_position(self)
                if map_data[cy][cx] not in ['L', 'U', 'D', 'E']:
                    self.seek_ladder = True
                    self.seek_dx = -dx

    def try_climb(self, player, map_data, cx, cy):
        conlog("try climb invoked")
        if not hasattr(self, 'climb_dy'):
            self.climb_dy = 0
        if not hasattr(self, 'has_started_climbing'):
            self.has_started_climbing = False
        if self.climb_dy != 0 and self.has_started_climbing:
            tiles = get_surrounding_tiles(self, map_data)
            _, pcy = get_tile_position(player)
            _, vcy = get_tile_position(self)
            tile_y_aligned = abs((self.y % TILE_SIZE) - 0) <= 2  # snap to top edge
            if pcy == vcy and tile_y_aligned and (tiles['loleft'] == 'F' or tiles['loright'] == 'F'):
                # conlog(f"[{self.name}] Exiting ladder: aligned and floor detected at row {vcy}")
                self.climb_dy = 0
                self.has_started_climbing = False
                self.seek_ladder = False
                if tiles['loleft'] == 'F':
                    #conlog(f"[{self.name}] Stepping left off ladder")
                    try_move(self, -1, 0, map_data)
                elif tiles['loright'] == 'F':
                    #conlog(f"[{self.name}] Stepping right off ladder")
                    try_move(self, 1, 0, map_data)
                return True
        up_possible = can_climb(-1, map_data, cx, cy)
        down_possible = can_climb(1, map_data, cx, cy)
        if not up_possible and not down_possible:
            return False
        if self.climb_dy == 0:
            dy = self.vertical_tile_distance(player)
            if dy > 0 and down_possible:
                self.climb_dy = 1
            elif dy < 0 and up_possible:
                self.climb_dy = -1
            elif up_possible:
                self.climb_dy = -1
            elif down_possible:
                self.climb_dy = 1
            else:
                return False
        dy = self.climb_dy
        success = try_move(self, 0, dy, map_data)
        if success:
            self.has_started_climbing = True
        else:
            self.climb_dy = 0
            self.has_started_climbing = False
        return success


    def draw(self, surface, offset_y=0):
        sprite = self.sprites[self.frame]
        if self.facing_left:
            sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (int(self.x), int(self.y + offset_y)))

    def is_aligned_with_player(self, player):
        pcx, pcy = get_tile_position(player)
        vcx, vcy = get_tile_position(self)
        return pcx == vcx

    def vertical_tile_distance(self, player):
        pcx, pcy = get_tile_position(player)
        vcx, vcy = get_tile_position(self)
        return pcy - vcy
