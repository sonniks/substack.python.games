# tilemap.py


import pygame
from constants import TILE_SIZE
from spritesheet import load_spritesheet
from movement import get_tile_position
from scanner import _safe_cell
from constants import SPRITESHEET_PATH, SHOW_TILE_COORDS


def build_tilemap(map_data, tile_lookup):
    """
    Build a tilemap surface from map data and a tile lookup dictionary.
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
    cols_in_sheet = sheet_width() // TILE_SIZE


    def _coords_for(ch):
        """
        Get the (sx, sy) coordinates in the spritesheet for the given character.
        :param ch:
        :return:
        """
        entry = tile_lookup.get(ch)
        if entry is None:
            return None
        coords = entry.get('coords') if isinstance(entry, dict) else entry
        if coords is None or len(coords) < 2:
            return None
        return int(coords[0]), int(coords[1])

    for y, row in enumerate(map_data):
        for x, ch in enumerate(row):
            if ch in ('P', 'V'):
                continue
            pos = _coords_for(ch)
            if pos is None:
                continue
            sx, sy = pos
            tile_index = sy * cols_in_sheet + sx
            tile = tile_lookup[ch].get('surface') or tiles[tile_index]
            surface.blit(tile, (x * TILE_SIZE, y * TILE_SIZE))
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
    """
    Find all spawn positions for a given character in the map data.
    :param map_data:
    :param char:
    :return:
    """
    positions = []
    for y, row in enumerate(map_data):
        for x, val in enumerate(row):
            if val == char:
                positions.append((x * 32, y * 32))
    return positions


def player_cell(map_data, entity):
    """
    Get the map cell character at the entity's current tile position.
    :param map_data:
    :param entity:
    :return:
    """
    cx, cy = get_tile_position(entity)
    return _safe_cell(map_data, cx, cy)