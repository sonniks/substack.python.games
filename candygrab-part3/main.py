# main.py

import pygame
from input import get_movement_input
from scanner import scan_world
from game_init import init_game, FPS
from display import update_villains, update_beams, render_frame
from combat import handle_firing, check_and_trigger_player_death
from tilemap import build_tilemap


def handle_events():
    """
    Handle Pygame events, specifically looking for quit events and spacebar presses.
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


def main():
    """
    Main game loop: initialize game, handle input, update game state, and render frames.
    :return:
    """
    screen, clock, map_data, tile_lookup, tile_surface, player, score_display, hud, villains, beams = init_game()
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
        scan_world(map_data, player, villains, tile_lookup, hud)
        tile_surface = build_tilemap(map_data, tile_lookup)
        # scan_world(map_data, player, villains)
        render_frame(screen, tile_surface, player, villains, score_display, hud, beams)
        clock.tick(FPS)


if __name__ == '__main__':
    main()
