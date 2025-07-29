# main.py

import pygame
from loader import load_level_data, load_tileset, load_map
from tilemap import build_tilemap
from player import Player
from input import get_movement_input


SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
UI_OFFSET = 96


def init_game():
    """
    Initialize the game environment.
    :return:
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Burger-Dig Hybrid")
    return screen


def load_assets(level_path):
    """
    Load level data, sprites, and map from the specified path.
    :param level_path:
    :return:
    """
    level = load_level_data(level_path)
    sprites = load_tileset(level['lookup'])
    map_data = load_map(level['map'])
    return level, sprites, map_data


def setup_screen():
    """
    Set up the game screen and pygame clock.
    :return:
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Burger-Dig Hybrid")
    return screen, pygame.time.Clock()


def handle_events():
    """
    Handle events such as quitting the game.
    :return:
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()


def handle_input(player, map_data):
    """
    Handle player (keyboard) input for movement.
    :param player:
    :param map_data:
    :return:
    """
    keys = pygame.key.get_pressed()
    dx, dy = get_movement_input(keys)
    player.update(dx, dy, map_data)


def render(screen, tile_surface, player):
    """
    Render the game screen with the tilemap and player.
    :param screen:
    :param tile_surface:
    :param player:
    :return:
    """
    screen.fill((0, 0, 0))
    screen.blit(tile_surface, (0, UI_OFFSET))
    player.draw(screen, offset_y=UI_OFFSET)
    pygame.display.flip()


def main():
    """
    Main function to run the game.
    :return:
    """
    screen, clock = setup_screen()
    level, sprites, map_data = load_assets("config/levels.json")
    tile_surface = build_tilemap(map_data, sprites)
    player = Player(map_data)
    render(screen, tile_surface, player)

    while True:
        handle_events()
        handle_input(player, map_data)
        render(screen, tile_surface, player)
        clock.tick(FPS)


if __name__ == '__main__':
    main()
