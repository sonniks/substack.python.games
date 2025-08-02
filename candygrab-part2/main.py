# main.py

import pygame
import random
from loader import load_level_data, load_tileset, load_map
from tilemap import build_tilemap
from player import Player
from input import get_movement_input
from villain import Villain

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
UI_OFFSET = 96


def setup_screen():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Candy Grab Part 2")
    return screen, pygame.time.Clock()


def load_assets(level_path):
    level = load_level_data(level_path)
    sprites = load_tileset(level['lookup'])
    map_data = load_map(level['map'])
    return level, sprites, map_data


def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()


def handle_input(player, map_data):
    keys = pygame.key.get_pressed()
    dx, dy = get_movement_input(keys)
    player.update(dx, dy, map_data)


def render(screen, tile_surface, player, villains):
    screen.fill((0, 0, 0))
    screen.blit(tile_surface, (0, UI_OFFSET))
    player.draw(screen, offset_y=UI_OFFSET)
    for v in villains:
        v.draw(screen, offset_y=UI_OFFSET)
    pygame.display.flip()


def find_all_villain_spawns(map_data, char='V'):
    positions = []
    for y, row in enumerate(map_data):
        for x, val in enumerate(row):
            if val == char:
                positions.append((x * 32, y * 32))
    return positions


def main():
    screen, clock = setup_screen()
    level, sprites, map_data = load_assets("config/levels.json")
    tile_surface = build_tilemap(map_data, sprites)
    player = Player(map_data)

    spawns = find_all_villain_spawns(map_data, 'V')
    total = len(spawns)
    villains = []

    for i, pos in enumerate(spawns):
        hue_shift = (i * 0.2) % 1.0
        villains.append(Villain(map_data, pos, hue_shift=hue_shift, index=i, total=total))

    while True:
        handle_events()
        handle_input(player, map_data)
        for villain in villains:
            villain.update(player, map_data)
        render(screen, tile_surface, player, villains)
        clock.tick(FPS)


if __name__ == '__main__':
    main()
