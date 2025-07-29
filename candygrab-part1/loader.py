# loader.py

import json
import csv
import pygame
from spritesheet import load_spritesheet

TILE_SIZE = 32

def load_level_data(json_path):
    with open(json_path) as f:
        data = json.load(f)
    return data['levels'][0]

def load_tileset(csv_path):
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        return {row['char']: (int(row['x']), int(row['y'])) for row in reader}

def load_map(txt_path):
    with open(txt_path) as f:
        return [list(line.rstrip('\n')) for line in f]
