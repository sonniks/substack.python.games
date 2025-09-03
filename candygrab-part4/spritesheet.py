# spritesheet.py


import pygame
from constants import TILE_SIZE


def load_spritesheet(path):
    """
    Load a spritesheet and return a list of subsurfaces for each tile.
    :param path:
    :return:
    """
    sheet = pygame.image.load(path).convert_alpha()
    sheet_width, sheet_height = sheet.get_size()
    cols, rows = sheet_width // TILE_SIZE, sheet_height // TILE_SIZE
    return [
        sheet.subsurface(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        for y in range(rows)
        for x in range(cols)
    ]