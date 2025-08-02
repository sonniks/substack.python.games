# tilemap.py

import pygame
from loader import TILE_SIZE
from spritesheet import load_spritesheet


SPRITESHEET_PATH = "assets/sprites/sheet.png"
SHOW_TILE_COORDS = True


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
    font = pygame.font.SysFont("consolas", 10, bold=True) if SHOW_TILE_COORDS else None
    for y, row in enumerate(map_data):
        for x, char in enumerate(row):
            if char in ('P', 'V'):
                continue  # Do not draw spawn marker
            if char not in tile_lookup:
                continue
            sx, sy = tile_lookup[char]
            tile_index = sy * (sheet_width() // TILE_SIZE) + sx
            surface.blit(tiles[tile_index], (x * TILE_SIZE, y * TILE_SIZE))
            if SHOW_TILE_COORDS and font:
                label = font.render(f"{x},{y}", True, (255, 255, 0))
                surface.blit(label, (x * TILE_SIZE + 2, y * TILE_SIZE + 2))
    return surface

def sheet_width():
    """
    Get the width of the spritesheet.
    :return:
    """
    image = pygame.image.load(SPRITESHEET_PATH)
    return image.get_width()

def find_all_villain_spawns(map_data, char):
    positions = []
    for y, row in enumerate(map_data):
        for x, val in enumerate(row):
            if val == char:
                positions.append((x * 32, y * 32))
    return positions
