# game_init.py


import pygame
from dataclasses import dataclass
from loader import *
from tilemap import build_tilemap
from player import Player
from scoredisplay import ScoreDisplay
from villain import Villain
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS





@dataclass
class HUDState:
    score: int = 0
    lives: int = 3
    level_number: int = 1


def setup_screen():
    """
    Initialize pygame and set up the main screen and clock.
    :return:
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Candy Grab Part 3")
    return screen, pygame.time.Clock()


def load_assets(level_path):
    """
    Load level data, tileset, and map data from the specified level configuration.
    :param level_path:
    :return:
    """
    level = load_level_data(level_path)
    tile_lookup = load_tileset(level['lookup'])  # now includes {'coords': (x,y), 'score': int}
    map_data = load_map(level['map'])
    return level, tile_lookup, map_data


def find_all_villain_spawns(map_data, char='V'):
    """
    Find all positions of the specified character in the map data and return their pixel coordinates.
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


def spawn_villains(map_data, speed_multiplier=1.0):
    """
    Spawn villains at all designated spawn points in the map data.
    :param map_data:
    :return:
    """
    spawns = find_all_villain_spawns(map_data, 'V')
    total = len(spawns)
    villains = []
    for i, pos in enumerate(spawns):
        hue_shift = (i * 0.2) % 1.0
        villains.append(
            Villain(map_data, pos, hue_shift=hue_shift, index=i, total=total, speed_multiplier=speed_multiplier))
    return villains


def init_game():
    """
    Initialize the game: set up screen, load assets, create player, HUD, villains, and beams list.
    :return:
    """
    screen, clock = setup_screen()
    level = load_level_data("config/levels.json")
    map_data = load_map(level["map"])
    tile_lookup = load_tileset(level["lookup"])
    hue_shift = level.get("floor_hue_shift", 0.0)
    tile_surface = build_tilemap(map_data, tile_lookup)
    player = Player(map_data)
    score_display = ScoreDisplay(SCREEN_WIDTH)
    hud = HUDState()
    villains = spawn_villains(map_data)
    beams = []
    # Return tile_lookup so main can pass it into scan_world()
    return screen, clock, map_data, tile_lookup, tile_surface, player, score_display, hud, villains, beams
