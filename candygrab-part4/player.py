# player.py

import pygame
from logger import conlog
from constants import DEATH_ANIM_MS, DEATH_COOLDOWN_MS, TILE_SIZE
from movement import (
    get_tile_position,
    get_target_tile,
    try_move,
    log_surrounding_tiles,
    maybe_snap_to_floor
)


class Player:
    def __init__(self, map_data):
        self.sprites = self.load_player_sprites()
        self.MOVE_SPEED = 2
        self.frame = 0
        self.timer = 0
        self.x, self.y = self.find_spawn(map_data)
        self.facing_left = False
        self.name = "Player"
        # death state
        self.death_start_ms = None
        self.invulnerable_until_ms = 0
        self.spin_angle = 0.0


    def load_player_sprites(self):
        """
        Load player sprites from the spritesheet.
        :return:
        """
        sheet = pygame.image.load("assets/sprites/sheet.png").convert_alpha()
        return [sheet.subsurface(pygame.Rect(i * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)) for i in range(4)]


    def find_spawn(self, map_data):
        """
        Find the player's spawn position in the map data (marked by 'P').
        :param map_data:
        :return:
        """
        for y, row in enumerate(map_data):
            for x, char in enumerate(row):
                if char == 'P':
                    return x * TILE_SIZE, y * TILE_SIZE
        return 0, 0


    def start_death(self, now_ms):
        """
        Initiate the death animation if not already dying.
        :param now_ms:
        :return:
        """
        if self.is_dying():
            return
        self.death_start_ms = now_ms
        self.spin_angle = 0.0


    def is_dying(self):
        """
        Check if the player is currently in the death animation state.
        :return:
        """
        return self.death_start_ms is not None


    def is_invulnerable(self, now_ms):
        """
        Check if the player is currently invulnerable (after death).
        :param now_ms:
        :return:
        """
        return now_ms < self.invulnerable_until_ms


    def _update_death(self, now_ms):
        """
        Update the death animation state.
        :param now_ms:
        :return:
        """
        if not self.is_dying():
            return
        elapsed = now_ms - self.death_start_ms
        # spin at 360 deg/sec for ~3s, clockwise
        self.spin_angle = (elapsed * 360.0) / 1000.0
        if elapsed >= DEATH_ANIM_MS:
            self.death_start_ms = None
            self.spin_angle = 0.0
            self.invulnerable_until_ms = now_ms + DEATH_COOLDOWN_MS


    def update(self, dx, dy, map_data, now_ms=None):
        """
        Update the player's state based on input and map data.
        :param dx:
        :param dy:
        :param map_data:
        :param now_ms:
        :return:
        """
        self.timer += 1
        maybe_snap_to_floor(self, map_data)
        if self.timer % 10 == 0:
            self.frame = (self.frame + 1) % len(self.sprites)
        # Death animation overrides control
        if self.is_dying():
            self._update_death(now_ms or 0)
            return
        # Normal control
        if dx < 0:
            self.facing_left = True
        elif dx > 0:
            self.facing_left = False
        _nx, _ny, _tx, _ty, _cx, _cy = get_target_tile(self, dx, dy)
        # log_surrounding_tiles(self, map_data)
        conlog("Player trying move")
        try_move(self, dx, dy, map_data)


    def draw(self, surface, offset_y=0):
        """
        Draw the player onto the given surface with vertical offset.
        :param surface:
        :param offset_y:
        :return:
        """
        base = self.sprites[self.frame]
        sprite = pygame.transform.flip(base, True, False) if self.facing_left else base
        if self.is_dying():
            # rotate around center while spinning
            rotated = pygame.transform.rotate(sprite, -self.spin_angle)  # negative for clockwise
            rect = rotated.get_rect(center=(self.x + TILE_SIZE // 2, self.y + offset_y + TILE_SIZE // 2))
            surface.blit(rotated, rect.topleft)
        else:
            surface.blit(sprite, (self.x, self.y + offset_y))
