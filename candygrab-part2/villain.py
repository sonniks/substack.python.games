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
        """
        Compute the villain's speed based on its index and total number of villains.
        :param index:
        :param total:
        :return:
        """
        min_speed = 1.2
        max_speed = 1.8
        t = index / max(1, total - 1)
        return min_speed + t * (max_speed - min_speed)


    def load_villain_sprites(self, hue_shift):
        """
        Load the villain sprites from the spritesheet and apply a hue shift.
        :param hue_shift:
        :return:
        """
        sheet = pygame.image.load("assets/sprites/sheet.png").convert_alpha()
        base_sprites = [
            sheet.subsurface(pygame.Rect(i * TILE_SIZE, TILE_SIZE, TILE_SIZE, TILE_SIZE))
            for i in range(4)
        ]
        return [hue_shift_sprite(sprite, hue_shift) for sprite in base_sprites]


    def find_spawn(self, map_data):
        """
        Find the spawn position of the villain in the map data.
        :param map_data:
        :return:
        """
        for y, row in enumerate(map_data):
            for x, char in enumerate(row):
                if char == 'V':
                    return x * TILE_SIZE, y * TILE_SIZE
        return 0, 0

    # villain.py (refactored update)
    def update(self, player, map_data):
        """
        Update the villain's position and state based on the player and map data.
        :param player:
        :param map_data:
        :return:
        """
        self.timer += 1
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
        Handle collision with the floor tile.
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
        Detect if the villain is stuck in the same tile for too long.
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
                        conlog(
                            f"[{self.name}] Forced move {'left' if dx == -1 else 'right'} from ({self.x:.1f},{self.y:.1f})")
                        return True
        else:
            self.stuck_counter = 0
            self.last_tile = current_pos
        return False


    def jostle_villain(self, current_pos):
        """
        Handle the case where the villain is stuck in the same tile for too long.
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
        Handle the logic for seeking a ladder when the villain is not aligned with the player.
        :param player:
        :param map_data:
        :param cx:
        :param cy:
        :return:
        """
        if self.seek_ladder:
            conlog(f"{self.name} is seek ladder at ({cx},{cy}) direction {self.seek_dx}")
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
        Check if the villain is on a ladder or vine and attempt to climb.
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
        Move the villain towards the player if they are not aligned vertically.
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
        Attempt to climb the ladder or vine based on the player's position and map data.
        :param player:
        :param map_data:
        :param cx:
        :param cy:
        :return:
        """
        conlog("try climb invoked")
        self._ensure_climb_state()
        if self._should_exit_ladder(player, map_data):
            self._exit_ladder(map_data)
            return True
        if not self._determine_climb_direction(player, map_data, cx, cy):
            return False
        return self._attempt_climb(map_data)


    def _ensure_climb_state(self):
        """
        Ensure the villain has the necessary attributes for climbing.
        :return:
        """
        if not hasattr(self, 'climb_dy'):
            self.climb_dy = 0
        if not hasattr(self, 'has_started_climbing'):
            self.has_started_climbing = False


    def _should_exit_ladder(self, player, map_data):
        """
        Check if the villain should exit the ladder based on the player's position and surrounding tiles.
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
        Exit the ladder by moving left or right based on the surrounding tiles.
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
        Determine the direction to climb based on the player's position and the map data.
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
        Attempt to climb the ladder or vine based on the determined direction.
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
        Draw the villain sprite on the given surface at the current position.
        :param surface:
        :param offset_y:
        :return:
        """
        sprite = self.sprites[self.frame]
        if self.facing_left:
            sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (int(self.x), int(self.y + offset_y)))


    def is_aligned_with_player(self, player):
        """
        Check if the villain is aligned vertically with the player.
        :param player:
        :return:
        """
        pcx, pcy = get_tile_position(player)
        vcx, vcy = get_tile_position(self)
        return pcx == vcx


    def vertical_tile_distance(self, player):
        """
        Calculate the vertical distance in tiles between the villain and the player.
        :param player:
        :return:
        """
        pcx, pcy = get_tile_position(player)
        vcx, vcy = get_tile_position(self)
        return pcy - vcy
