# render/draw.py
import pygame
import random
from objects.player import draw_player
from objects.lasers import draw_lasers
from objects.enemy import draw_enemies, get_score, get_lives, get_stage
from render.fonts import draw_text


stars = []


def init_starfield(num_stars=100):
    """
    Initialize the starfield with a specified number of stars.
    :param num_stars:
    :return:
    """
    global stars
    stars = [[random.randint(0, 800), random.randint(0, 600)] for _ in range(num_stars)]


def draw_frame(screen):
    """
    Draw the main game frame including player, lasers, enemies, and HUD elements.
    :param screen:
    :return:
    """
    screen.fill((0, 0, 0))
    draw_player(screen)
    draw_lasers(screen)
    draw_enemies(screen)
    draw_starfield(screen)
    draw_text(screen, "THE FAR VOID", 24, 20, 20)
    draw_text(screen, f"STAGE: {get_stage()}", 20, 20, 50)
    draw_text(screen, f"SCORE: {get_score()}", 24, 600, 20)
    draw_text(screen, f"SHIELDS: {get_lives()}", 24, 600, 50)
    apply_crt_effect(screen)



def draw_game_over(screen):
    """
    Draw the game over screen with an overlay and instructions.
    :param screen:
    :return:
    """
    overlay = pygame.Surface(screen.get_size())
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    draw_text(screen, "GAME OVER", 48, 250, 220, (255, 0, 0))
    draw_text(screen, f"STAGE: {get_stage()}", 24, 320, 300)
    draw_text(screen, f"SCORE: {get_score()}", 24, 320, 340)
    draw_text(screen, "Press ENTER to Restart or Q to Quit", 24, 180, 400, (255, 255, 255))
    apply_crt_effect(screen)


def draw_starfield(screen):
    """
    Draw the starfield by rendering each star and updating their positions.
    :param screen:
    :return:
    """
    global stars
    for star in stars:
        pygame.draw.circle(screen, (80, 80, 80), star, 1)
        star[1] += 1
        if star[1] > 600:
            star[0] = random.randint(0, 800)
            star[1] = 0


def apply_crt_effect(screen):
    """
    Apply a CRT effect to the screen by drawing horizontal lines and a flickering overlay.
    :param screen:
    :return:
    """
    width, height = screen.get_size()
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(0, height, 4):
        pygame.draw.line(overlay, (0, 0, 0, 30), (0, y), (width, y))
    flicker_intensity = random.randint(0, 1)
    flicker_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    flicker_overlay.fill((0, 255, 0, flicker_intensity))
    overlay.blit(flicker_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    screen.blit(overlay, (0, 0))
