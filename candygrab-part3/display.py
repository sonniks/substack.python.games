# display.py

import pygame

UI_OFFSET = 96


def update_villains(villains, player, map_data):
    """
    Update all villains with respect to the player's position and the map data.
    :param villains:
    :param player:
    :param map_data:
    :return:
    """
    for v in villains:
        v.update(player, map_data)


def update_beams(beams, now_ms):
    """
    Update all beams and remove any that are dead.
    :param beams:
    :param now_ms:
    :return:
    """
    for b in beams:
        b.update(now_ms)
    beams[:] = [b for b in beams if not b.is_dead()]


def render_frame(screen, tile_surface, player, villains, score_display, hud, beams, ui_offset=UI_OFFSET):
    """
    Render the entire game frame: background, HUD, player, villains, and beams.
    :param screen:
    :param tile_surface:
    :param player:
    :param villains:
    :param score_display:
    :param hud:
    :param beams:
    :param ui_offset:
    :return:
    """
    screen.fill((0, 0, 0))
    score_display.draw(screen, hud.level_number, hud.score, hud.lives)
    screen.blit(tile_surface, (0, ui_offset))
    player.draw(screen, offset_y=ui_offset)
    for v in villains:
        v.draw(screen, offset_y=ui_offset)
    for b in beams:
        b.draw(screen, offset_y=ui_offset)
    pygame.display.flip()
