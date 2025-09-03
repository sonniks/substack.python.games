# main.py


import os
import json
import pygame
from constants import *
from loader import load_level, TILE_SIZE
from tilemap import build_tilemap, sheet_width
from scoredisplay import ScoreDisplay
from player import Player
from display import render_frame, update_villains, update_beams, show_level_complete, show_title_card
from scanner import scan_world
from combat import handle_firing, check_and_trigger_player_death
from input import get_movement_input
from game_init import setup_screen, HUDState, spawn_villains, SCREEN_WIDTH, FPS


def handle_events():
    """
    Handle pygame events, returning whether the fire button (space) was pressed.
    :return:
    """
    fire_pressed = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            fire_pressed = True
    return fire_pressed


def run_game_loop(screen, clock, all_levels, candy_sound, music_volume):
    """
    Main game loop: handle input, update game state, render frame, manage levels.
    :param screen:
    :param clock:
    :param all_levels:
    :param candy_sound:
    :param music_volume:
    :return:
    """
    current_level_index = 0
    loop_count = 0
    level, map_data, tile_lookup = load_level(all_levels, current_level_index, music_volume)
    tile_surface = build_tilemap(map_data, tile_lookup)
    player = Player(map_data)
    score_display = ScoreDisplay(SCREEN_WIDTH)
    hud = HUDState()
    hud.level_number = level["id"]
    villains = spawn_villains(map_data)
    beams = []
    while True:
        fire_pressed = handle_events()
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
        dx, dy = get_movement_input(keys)
        player.update(dx, dy, map_data, now_ms=now)
        update_villains(villains, player, map_data)
        if fire_pressed:
            handle_firing(player, map_data, villains, beams, now, hud)
        update_beams(beams, now)
        check_and_trigger_player_death(player, villains, map_data, now)
        scan_world(map_data, player, villains, tile_lookup, hud, candy_sound=candy_sound)
        if not any(ch in row for row in map_data for ch in {'@', '!', '#', '$'}):
            show_level_complete(screen, hud.level_number, hud.lives, music_volume)
            current_level_index += 1
            if current_level_index >= len(all_levels):
                current_level_index = 0
                loop_count += 1
            speed_multiplier = 1.0 + 0.15 * loop_count
            level, map_data, tile_lookup = load_level(all_levels, current_level_index, music_volume)
            tile_surface = build_tilemap(map_data, tile_lookup)
            player = Player(map_data)
            villains = spawn_villains(map_data, speed_multiplier=speed_multiplier)
            beams.clear()
            hud.level_number = level["id"] + loop_count * len(all_levels)
        tile_surface = build_tilemap(map_data, tile_lookup)
        render_frame(screen, tile_surface, player, villains, score_display, hud, beams)
        clock.tick(FPS)


def main():
    """
    Main entry point: initialize pygame, load sounds, levels, and start the game loop.
    :return:
    """
    pygame.mixer.init()
    music_volume = float(os.getenv("MUSIC_VOLUME", "0.25"))
    candy_sound = pygame.mixer.Sound("assets/sounds/grab-candy.wav")
    candy_sound.set_volume(0.5)
    with open("config/levels.json") as f:
        all_levels = json.load(f)["levels"]
    screen, clock = setup_screen()
    show_title_card(screen)
    run_game_loop(screen, clock, all_levels, candy_sound, music_volume)


if __name__ == '__main__':
    main()
