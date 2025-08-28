# loader.py

import json
import csv
import pygame
from spritesheet import load_spritesheet

TILE_SIZE = 32


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


# def load_map(txt_path):
#     """
#     Load map data from a text file.
#     :param txt_path:
#     :return:
#     """
#     with open(txt_path) as f:
#         return [list(line.rstrip('\n')) for line in f]


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
