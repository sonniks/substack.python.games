# villain.py


import pygame
from loader import TILE_SIZE
from logger import conlog
from visualeffects import hue_shift_sprite
from movement import *
from collections import deque

DISABLE_WINDOW_MS = 2000      # 3 impacts must occur within this window
DISABLE_DURATION_MS = 30000   # disabled for 30 seconds


class Villain:
    def __init__(self, map_data, spawn_xy, hue_shift=0, index=0, total=1):
        self.index = index
        self.name = f"Villain{index}"
        self.MOVE_SPEED = self.compute_speed(index, total)
        self.x, self.y = spawn_xy
        self.facing_left = False
        self.seek_ladder = False
        self.seek_dx = 0
        self.timer = 0
        self.frame = 0
        # Sprites
        self._hue_shift = hue_shift
        self.sprites = self._load_villain_anim(hue_shift)
        self.disabled_sprite = self._load_disabled_sprite()
        # Combat state
        self.hit_times = deque()  # ms timestamps of recent hits
        self.disabled_until = 0   # ms; 0 means active


    def compute_speed(self, index, total):
        """
        Compute villain speed based on index and total number of villains.
        :param index:
        :param total:
        :return:
        """
        min_speed = 1.2
        max_speed = 1.8
        t = index / max(1, total - 1)
        return min_speed + t * (max_speed - min_speed)


    def _load_villain_anim(self, hue_shift):
        """
        Load the 4-frame walking animation for the villain and apply hue shift.
        :param hue_shift:
        :return:
        """
        sheet = pygame.image.load("assets/sprites/sheet.png").convert_alpha()
        base = [sheet.subsurface(pygame.Rect(i * TILE_SIZE, TILE_SIZE, TILE_SIZE, TILE_SIZE)) for i in range(4)]
        return [hue_shift_sprite(s, hue_shift) for s in base]


    def _load_disabled_sprite(self):
        """
        Load the disabled (frozen) sprite for the villain.
        :return:
        """
        sheet = pygame.image.load("assets/sprites/sheet.png").convert_alpha()
        rect = pygame.Rect(5 * TILE_SIZE, 1 * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        return sheet.subsurface(rect)


    def is_disabled(self):
        """
        Check if the villain is currently disabled (frozen).
        :return:
        """
        return self.disabled_until and pygame.time.get_ticks() < self.disabled_until


    def register_hit(self, now_ms):
        """
        Register a hit on the villain at the given timestamp.
        :param now_ms:
        :return:
        """
        self.hit_times.append(now_ms)
        # Trim old hits outside the window
        while self.hit_times and now_ms - self.hit_times[0] > DISABLE_WINDOW_MS:
            self.hit_times.popleft()
        conlog(f"[{self.name}] Hit registered at {now_ms} ms; recent={list(self.hit_times)}")
        if len(self.hit_times) >= 3 and not self.is_disabled():
            self.disabled_until = now_ms + DISABLE_DURATION_MS
            conlog(f"[{self.name}] DISABLED until {self.disabled_until} (30 seconds)")
            # Clear movement intent while disabled
            self.seek_ladder = False
            if hasattr(self, 'climb_dy'):
                self.climb_dy = 0
            if hasattr(self, 'has_started_climbing'):
                self.has_started_climbing = False


    def update(self, player, map_data):
        """
        Update the villain's state each frame.
        :param player:
        :param map_data:
        :return:
        """
        self.timer += 1
        if self.is_disabled():
            # Stay frozen but still animate a gentle blink on the disabled sprite via frame counter
            return
        maybe_snap_to_floor(self, map_data)
        if self.timer % 10 == 0:
            self.frame = (self.frame + 1) % len(self.sprites)
        cx, cy = get_tile_position(self)
        current_tile = map_data[cy][cx]
        if self.handle_floor_collision(current_tile, cx, cy):
            return
        if self.handle_stuck_detection(cx, cy, map_data):
            return
        if self.handle_seek_ladder(player, map_data, cx, cy):
            return
        if self.try_climb_if_on_ladder(player, map_data, current_tile, cx, cy):
            return
        if self.is_aligned_with_player(player):
            self.try_climb(player, map_data, cx, cy)
        self.move_toward_player(player, map_data)


    def handle_floor_collision(self, current_tile, cx, cy):
        """
        Handle the case where the villain is stuck inside a floor tile.
        :param current_tile:
        :param cx:
        :param cy:
        :return:
        """
        if current_tile == 'F':
            conlog(f"[{self.name}] Inside floor at ({cx},{cy}), nudging up and canceling downward motion")
            self.y -= 1.0
            if hasattr(self, 'climb_dy') and self.climb_dy > 0:
                self.climb_dy = 0
                self.has_started_climbing = False
            return True
        return False


    def handle_stuck_detection(self, cx, cy, map_data):
        """
        Detect if the villain is stuck in the same tile for too long and attempt to jostle free.
        :param cx:
        :param cy:
        :param map_data:
        :return:
        """
        current_pos = (cx, cy)
        if not hasattr(self, 'last_tile'):
            self.last_tile = current_pos
            self.stuck_counter = 0
            self.STUCK_LIMIT = 45
        if self.last_tile == current_pos:
            self.stuck_counter += 1
            if self.stuck_counter > self.STUCK_LIMIT:
                self.jostle_villain(current_pos)
                for dx in [-1, 1]:
                    if try_move(self, dx, 0, map_data):
                        # conlog(f"[{self.name}] Forced move {'left' if dx == -1 else 'right'} from ({self.x:.1f},{self.y:.1f})")
                        return True
        else:
            self.stuck_counter = 0
            self.last_tile = current_pos
        return False


    def jostle_villain(self, current_pos):
        """
        Jostle the villain free after being stuck too long.
        :param current_pos:
        :return:
        """
        conlog(f"[{self.name}] Stuck too long at {current_pos}, clearing flags and forcing move")
        self.seek_ladder = False
        self.climb_dy = 0
        self.has_started_climbing = False
        self.stuck_counter = 0


    def handle_seek_ladder(self, player, map_data, cx, cy):
        """
        Handle seeking a ladder when the villain is trying to reach the player vertically.
        :param player:
        :param map_data:
        :param cx:
        :param cy:
        :return:
        """
        if self.seek_ladder:
            self.facing_left = self.seek_dx > 0
            if on_ladder(self, map_data):
                if self.try_climb(player, map_data, cx, cy):
                    if valid_floor_below(self, map_data):
                        self.seek_ladder = False
                return True
            else:
                try_move(self, self.seek_dx, 0, map_data)
                return True
        return False


    def try_climb_if_on_ladder(self, player, map_data, current_tile, cx, cy):
        """
        Attempt to climb if currently on a ladder tile.
        :param player:
        :param map_data:
        :param current_tile:
        :param cx:
        :param cy:
        :return:
        """
        if current_tile in ['L', 'U', 'D', 'E', 'T']:
            if self.try_climb(player, map_data, cx, cy):
                return True
        return False


    def move_toward_player(self, player, map_data):
        """
        Move horizontally toward the player if not aligned.
        :param player:
        :param map_data:
        :return:
        """
        delta_x = player.x - self.x
        if abs(delta_x) >= 1.0:
            dx = 1 if delta_x > 0 else -1
            self.facing_left = dx > 0
            success = try_move(self, dx, 0, map_data)
            if not success:
                cx, cy = get_tile_position(self)
                if map_data[cy][cx] not in ['L', 'U', 'D', 'E']:
                    self.seek_ladder = True
                    self.seek_dx = -dx


    def try_climb(self, player, map_data, cx, cy):
        """
        Attempt to climb up or down a ladder toward the player.
        :param player:
        :param map_data:
        :param cx:
        :param cy:
        :return:
        """
        self._ensure_climb_state()
        if self._should_exit_ladder(player, map_data):
            self._exit_ladder(map_data)
            return True
        if not self._determine_climb_direction(player, map_data, cx, cy):
            return False
        return self._attempt_climb(map_data)


    def _ensure_climb_state(self):
        """
        Ensure climbing state attributes are initialized.
        :return:
        """
        if not hasattr(self, 'climb_dy'):
            self.climb_dy = 0
        if not hasattr(self, 'has_started_climbing'):
            self.has_started_climbing = False


    def _should_exit_ladder(self, player, map_data):
        """
        Determine if the villain should exit the ladder (aligned with player and at bottom).
        :param player:
        :param map_data:
        :return:
        """
        if self.climb_dy == 0 or not self.has_started_climbing:
            return False
        tiles = get_surrounding_tiles(self, map_data)
        _, pcy = get_tile_position(player)
        _, vcy = get_tile_position(self)
        tile_y_aligned = abs((self.y % TILE_SIZE) - 0) <= 2
        return pcy == vcy and tile_y_aligned and (tiles['loleft'] == 'F' or tiles['loright'] == 'F')


    def _exit_ladder(self, map_data):
        """
        Exit the ladder by moving left or right onto a floor tile.
        :param map_data:
        :return:
        """
        tiles = get_surrounding_tiles(self, map_data)
        self.climb_dy = 0
        self.has_started_climbing = False
        self.seek_ladder = False
        if tiles['loleft'] == 'F':
            try_move(self, -1, 0, map_data)
        elif tiles['loright'] == 'F':
            try_move(self, 1, 0, map_data)


    def _determine_climb_direction(self, player, map_data, cx, cy):
        """
        Determine the climb direction (up or down) based on player's vertical position.
        :param player:
        :param map_data:
        :param cx:
        :param cy:
        :return:
        """
        if self.climb_dy != 0:
            return True
        up_possible = can_climb(-1, map_data, cx, cy)
        down_possible = can_climb(1, map_data, cx, cy)
        if not up_possible and not down_possible:
            return False
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
        return True


    def _attempt_climb(self, map_data):
        """
        Attempt to move the villain vertically by climb_dy on the ladder.
        :param map_data:
        :return:
        """
        success = try_move(self, 0, self.climb_dy, map_data)
        if success:
            self.has_started_climbing = True
        else:
            self.climb_dy = 0
            self.has_started_climbing = False
        return success


    def draw(self, surface, offset_y=0):
        """
        Draw the villain onto the given surface with vertical offset.
        :param surface:
        :param offset_y:
        :return:
        """
        if self.is_disabled():
            sprite = self.disabled_sprite
        else:
            sprite = self.sprites[self.frame]
            if self.facing_left:
                sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (int(self.x), int(self.y + offset_y)))


    def is_aligned_with_player(self, player):
        """
        Check if the villain is horizontally aligned with the player (same tile column).
        :param player:
        :return:
        """
        pcx, pcy = get_tile_position(player)
        vcx, vcy = get_tile_position(self)
        return pcx == vcx


    def vertical_tile_distance(self, player):
        """
        Get the vertical tile distance from the villain to the player.
        :param player:
        :return:
        """
        pcx, pcy = get_tile_position(player)
        vcx, vcy = get_tile_position(self)
        return pcy - vcy
