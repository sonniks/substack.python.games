# spritesheet.py

import pygame

TILE_SIZE = 32

def load_spritesheet(path):
    sheet = pygame.image.load(path).convert_alpha()
    sheet_width, sheet_height = sheet.get_size()
    cols, rows = sheet_width // TILE_SIZE, sheet_height // TILE_SIZE
    return [
        sheet.subsurface(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        for y in range(rows)
        for x in range(cols)
    ]