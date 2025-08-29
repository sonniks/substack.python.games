# main.py

import os
import json
import pygame
from loader import load_map, load_tileset, TILE_SIZE
from spritesheet import load_spritesheet
from visualeffects import hue_shift_sprite
from tilemap import build_tilemap, sheet_width
from scoredisplay import ScoreDisplay
from game_init import setup_screen, HUDState, spawn_villains
from player import Player
from display import render_frame, update_villains, update_beams
from scanner import scan_world
from combat import handle_firing, check_and_trigger_player_death
from input import get_movement_input
from game_init import setup_screen, HUDState, spawn_villains, SCREEN_WIDTH, SCREEN_HEIGHT, FPS





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
    from visualeffects import hue_shift_sprite
    from spritesheet import load_spritesheet
    from tilemap import sheet_width
    import os

    pygame.mixer.init()
    MUSIC_VOLUME = float(os.getenv("MUSIC_VOLUME", "0.25"))

    with open("config/levels.json") as f:
        all_levels = json.load(f)["levels"]

    current_level_index = 0

    def load_level(index):
        level = all_levels[index]
        map_data = load_map(level["map"])
        tile_lookup = load_tileset(level["lookup"])
        hue_shift = level.get("floor_hue_shift", 0.0)

        # Pre-hue-shift floor tiles
        if hue_shift:
            tilesheet = load_spritesheet("assets/sprites/sheet.png")
            sheet_cols = sheet_width() // TILE_SIZE
            for ch in {'F', 'T', 'L', 'E', 'U'}:
                entry = tile_lookup.get(ch)
                if entry and 'coords' in entry:
                    sx, sy = entry['coords']
                    tile_index = sy * sheet_cols + sx
                    original_tile = tilesheet[tile_index]
                    shifted_tile = hue_shift_sprite(original_tile, hue_shift)
                    tile_lookup[ch]['surface'] = shifted_tile

        # Load and play music
        music_file = level.get("music")
        if music_file:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(MUSIC_VOLUME)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Could not play music '{music_file}': {e}")

        return level, map_data, tile_lookup

    screen, clock = setup_screen()
    level, map_data, tile_lookup = load_level(current_level_index)
    tile_surface = build_tilemap(map_data, tile_lookup)
    player = Player(map_data)
    score_display = ScoreDisplay(SCREEN_WIDTH)
    hud = HUDState()
    hud.level_number = level["id"]
    villains = spawn_villains(map_data)
    beams = []

    loop_count = 0
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

        # Check for level completion (no candy)
        if not any(ch in row for row in map_data for ch in {'@', '!', '#', '$'}):
            print("[Main] Level complete!")
            # TODO: Add fadeout or transition effect here

            current_level_index += 1
            if current_level_index >= len(all_levels):
                current_level_index = 0
                loop_count += 1  # completed a full round

            speed_multiplier = 1.0 + 0.25 * loop_count  # 1.0 → 1.25 → 1.5 etc.

            level, map_data, tile_lookup = load_level(current_level_index)
            tile_surface = build_tilemap(map_data, tile_lookup)
            player = Player(map_data)
            villains = spawn_villains(map_data, speed_multiplier=speed_multiplier)
            beams.clear()
            hud.level_number = level["id"] + loop_count * len(all_levels)

        tile_surface = build_tilemap(map_data, tile_lookup)
        render_frame(screen, tile_surface, player, villains, score_display, hud, beams)
        clock.tick(FPS)




if __name__ == '__main__':
    main()
