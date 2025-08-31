# loader.py


import json
import csv
import pygame
from spritesheet import load_spritesheet
from visualeffects import hue_shift_sprite
from tilemap import sheet_width
from constants import *


def load_level_data(json_path):
    """
    Load level data from a JSON file.
    :param json_path:
    :return:
    """
    with open(json_path) as f:
        data = json.load(f)
    return data['levels'][0]


def load_tileset(csv_path):
    """
    Load a tileset from a CSV file.
    :param csv_path:
    :return:
    """
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        tiles = {}
        for row in reader:
            x, y = int(row['x']), int(row['y'])
            score = int(row['score']) if 'score' in row and row['score'] else 0
            tiles[row['char']] = {'coords': (x, y), 'score': score}
        return tiles


def load_map(path: str) -> list[list[str]]:
    """
    Load a text-based level map and ensure each row is exactly 25 characters wide.
    Short rows are padded with spaces. Long rows are trimmed.
    :param path: Path to the level text file
    :return: 2D list of map characters
    """
    with open(path, 'r') as f:
        lines = f.readlines()
    padded_map = []
    for line in lines:
        row = list(line.rstrip('\n'))
        row += [' '] * (25 - len(row))
        padded_map.append(row[:25])  # truncate if over
    return padded_map


def load_level(all_levels, index, music_volume):
    """
    Load level data, map, tileset, and handle music playback.
    :param all_levels:
    :param index:
    :param music_volume:
    :return:
    """
    level = all_levels[index]
    map_data = load_map(level["map"])
    tile_lookup = load_tileset(level["lookup"])
    hue_shift = level.get("floor_hue_shift", 0.0)
    if hue_shift:
        tilesheet = load_spritesheet("assets/sprites/sheet.png")
        sheet_cols = sheet_width() // TILE_SIZE
        for ch in {'F', 'T', 'L', 'E', 'U'}:
            entry = tile_lookup.get(ch)
            if entry and 'coords' in entry:
                sx, sy = entry['coords']
                tile_index = sy * sheet_cols + sx
                original_tile = tilesheet[tile_index]
                tile_lookup[ch]['surface'] = hue_shift_sprite(original_tile, hue_shift)
    music_file = level.get("music")
    if music_file:
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(music_volume)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Could not play music '{music_file}': {e}")
    return level, map_data, tile_lookup
