# fire.py

import pygame
from loader import TILE_SIZE
from spritesheet import TILE_SIZE as _CHECK_TILE  # sanity check same size
from movement import get_tile_position
from scanner import NON_ELIGIBLE  # {'L','D','U','E'}

BEAM_DURATION_MS = 300  # ~0.3s
SPRITESHEET_PATH = "assets/sprites/sheet.png"
# Projectile sprite is sheet coordinate (0,2)
PROJ_SX, PROJ_SY = 0, 2


class FireBeam:
    """
    Represents a short-lived projectile beam fired by the player.
    """
    def __init__(self, player, now_ms):
        self.spawn_ms = now_ms
        self.tiles = self._compute_tiles(player)
        self.sprite = self._load_projectile_sprite()
        self._alpha = 255

    def _compute_tiles(self, player):
        """
        Compute the list of tile coordinates covered by the beam based on player position and facing.
        :param player:
        :return:
        """
        pcx, pcy = get_tile_position(player)
        step = -1 if player.facing_left else 1
        # tiles from 1..3 in facing direction
        return [(pcx + step * i, pcy) for i in range(1, 4)]

    def _load_projectile_sprite(self):
        """
        Load and return the projectile sprite from the spritesheet.
        :return:
        """
        sheet = pygame.image.load(SPRITESHEET_PATH).convert_alpha()
        rect = pygame.Rect(PROJ_SX * TILE_SIZE, PROJ_SY * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        return sheet.subsurface(rect)

    def apply_damage_once(self, villains, map_data, player, now_ms):
        """
        Apply damage to villains in the beam's path. Each villain can only be hit once per beam.
        :param villains:
        :param map_data:
        :param player:
        :param now_ms:
        :return:
        """
        from scanner import _safe_cell  # avoid circular import at module import time
        newly_disabled = 0
        pcx, pcy = get_tile_position(player)
        pcell = _safe_cell(map_data, pcx, pcy)
        if pcell in NON_ELIGIBLE:
            return 0
        covered = set(self.tiles)
        for v in villains:
            vcx, vcy = get_tile_position(v)
            if (vcx, vcy) not in covered:
                continue
            vcell = _safe_cell(map_data, vcx, vcy)
            if vcell in NON_ELIGIBLE:
                continue
            was_disabled = v.is_disabled() if hasattr(v, "is_disabled") else False
            v.register_hit(now_ms)
            is_disabled = v.is_disabled() if hasattr(v, "is_disabled") else False
            if is_disabled and not was_disabled:
                newly_disabled += 1
        return newly_disabled


    def update(self, now_ms):
        """
        Update the beam's state based on elapsed time since spawn.
        :param now_ms:
        :return:
        """
        elapsed = now_ms - self.spawn_ms
        if elapsed >= BEAM_DURATION_MS:
            self._alpha = 0
        else:
            # linear fade 255 -> 0
            self._alpha = int(255 * (1.0 - (elapsed / BEAM_DURATION_MS)))


    def is_dead(self):
        """
        Check if the beam's lifetime has ended.
        :return:
        """
        return self._alpha <= 0


    def draw(self, surface, offset_y=0):
        """
        Draw the beam onto the given surface with vertical offset.
        :param surface:
        :param offset_y:
        :return:
        """
        if self._alpha <= 0:
            return
        img = self.sprite.copy()
        img.set_alpha(self._alpha)
        for cx, cy in self.tiles:
            px = cx * TILE_SIZE
            py = cy * TILE_SIZE + offset_y
            surface.blit(img, (px, py))
