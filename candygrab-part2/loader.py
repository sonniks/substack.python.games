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
        return {row['char']: (int(row['x']), int(row['y'])) for row in reader}


def load_map(txt_path):
    """
    Load a map from a text file.
    :param txt_path:
    :return:
    """
    with open(txt_path) as f:
        return [list(line.rstrip('\n')) for line in f]
