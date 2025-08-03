# player.py

import pygame
from loader import TILE_SIZE
from movement import (
    get_tile_position,
    in_bounds,
    get_target_tile,
    try_move,
    log_surrounding_tiles,
    maybe_snap_to_floor
)
from logger import conlog

class Player:
    def __init__(self, map_data):
        self.sprites = self.load_player_sprites()
        self.MOVE_SPEED = 2
        self.frame = 0
        self.timer = 0
        self.x, self.y = self.find_spawn(map_data)
        self.facing_left = False
        self.name = "Player"


    def load_player_sprites(self):
        """
        Load player sprites from the spritesheet.
        :return:
        """
        sheet = pygame.image.load("assets/sprites/sheet.png").convert_alpha()
        return [sheet.subsurface(pygame.Rect(i * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)) for i in range(4)]


    def find_spawn(self, map_data):
        """
        Find the spawn position of the player in the map data.
        :param map_data:
        :return:
        """
        for y, row in enumerate(map_data):
            for x, char in enumerate(row):
                if char == 'P':
                    return x * TILE_SIZE, y * TILE_SIZE
        return 0, 0


    def update(self, dx, dy, map_data):
        """
        Update the player's position based on input and map data.
        :param dx:
        :param dy:
        :param map_data:
        :return:
        """
        self.timer += 1
        maybe_snap_to_floor(self, map_data)
        if self.timer % 10 == 0:
            self.frame = (self.frame + 1) % len(self.sprites)
        cx, cy = get_tile_position(self)
        # conlog(f"Player position: ({self.x:.1f}, {self.y:.1f}) in tile ({cx},{cy})")
        # conlog(f"Player position: ({self.x:.1f}, {self.y:.1f}) in tile ({cx},{cy})")
        if dx < 0:
            self.facing_left = True
        elif dx > 0:
            self.facing_left = False
        new_x, new_y, tx, ty, cx, cy = get_target_tile(self, dx, dy)
        # conlog(f"Target tile: moving to ({tx}, {ty}) from ({cx}, {cy})")
        # log_surrounding_tiles(self, map_data)
        try_move(self, dx, dy, map_data)


    def draw(self, surface, offset_y=0):
        """
        Draw the player sprite on the given surface at the player's position.
        :param surface:
        :param offset_y:
        :return:
        """
        sprite = self.sprites[self.frame]
        if self.facing_left:
            sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (self.x, self.y + offset_y))
