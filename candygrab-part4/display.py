# display.py

import pygame
from scoredisplay import FONT_PATH

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


def show_level_complete(screen, level_number, lives_remaining, MUSIC_VOLUME):
    """
    Fade in a message and wait for key press after level is complete.
    """
    import time
    pygame.mixer.music.stop()
    try:
        pygame.mixer.music.load("assets/music/c-viou.xm")
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Failed to load level complete music: {e}")

    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    font = pygame.font.Font(FONT_PATH, 36)
    clock = pygame.time.Clock()

    fade_steps = 30
    background = screen.copy()  # capture the completed game frame

    for i in range(fade_steps):
        alpha = int(0.7 * 255 * i / fade_steps)
        screen.blit(background, (0, 0))  # re-blit captured game frame
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    text1 = font.render(f"Level {level_number} Clear", True, (255, 255, 255))
    text2 = font.render(f"Extra Lives Remaining: {lives_remaining}", True, (255, 255, 255))
    text3 = font.render("Press any key for next level...", True, (255, 255, 255))

    screen.blit(text1, text1.get_rect(center=(400, 250)))
    screen.blit(text2, text2.get_rect(center=(400, 300)))
    screen.blit(text3, text3.get_rect(center=(400, 370)))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                waiting = False
        clock.tick(30)

    for i in range(fade_steps):
        alpha = int(255 * i / fade_steps)
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(60)