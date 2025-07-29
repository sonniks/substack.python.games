# tilemap.py

import pygame
from loader import TILE_SIZE
from spritesheet import load_spritesheet


SPRITESHEET_PATH = "assets/sprites/sheet.png"


def build_tilemap(map_data, tile_lookup):
    """
    Build a tilemap surface from the given map data and tile lookup.
    :param map_data:
    :param tile_lookup:
    :return:
    """
    tiles = load_spritesheet(SPRITESHEET_PATH)
    surface = pygame.Surface(
        (len(map_data[0]) * TILE_SIZE, len(map_data) * TILE_SIZE + 96),
        pygame.SRCALPHA
    )
    for y, row in enumerate(map_data):
        for x, char in enumerate(row):
            if char == 'P':
                continue  # Do not draw spawn marker
            if char not in tile_lookup:
                continue
            sx, sy = tile_lookup[char]
            tile_index = sy * (sheet_width() // TILE_SIZE) + sx
            surface.blit(tiles[tile_index], (x * TILE_SIZE, y * TILE_SIZE))
    return surface

def sheet_width():
    """
    Get the width of the spritesheet.
    :return:
    """
    image = pygame.image.load(SPRITESHEET_PATH)
    return image.get_width()
