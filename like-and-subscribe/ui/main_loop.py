# ui/main_loop.py

import pygame
from core.engine import GameState
from data.game_data import PLATFORMS, CONTENT_TYPES, DEFAULT_GAME_LENGTHS
from ui import screen_draw
from ui.screen_draw import draw_text, load_icons, draw_header, draw_news, draw_platforms, draw_content_options, draw_end_screen
from sound.sound import init_sounds


pygame.init()
screen_draw.setup_fonts()
init_sounds()

SCREEN_WIDTH, SCREEN_HEIGHT = 480, 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Like and Subscribe")

FONT = pygame.font.SysFont("Arial", 24)
BIG_FONT = pygame.font.SysFont("Arial", 30)

BLACK = (0, 0, 0)


def start_menu():
    """
    Display the start menu and handle user input for game length selection.
    :return:
    """
    while True:
        screen.fill(BLACK)
        draw_text(screen, "Welcome to Like and Subscribe!", (60, 120), BIG_FONT)
        draw_text(screen, "Choose your career length:", (60, 200), FONT)
        draw_text(screen, "1. Quick Grind (14 days)", (80, 260), FONT)
        draw_text(screen, "2. Standard Career (30 days)", (80, 300), FONT)
        draw_text(screen, "3. Influencer Marathon (60 days)", (80, 340), FONT)
        draw_text(screen, "Q. Quit", (80, 400), FONT)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                key = event.key
                if key == pygame.K_1:
                    return DEFAULT_GAME_LENGTHS["Quick Grind"]
                elif key == pygame.K_2:
                    return DEFAULT_GAME_LENGTHS["Standard Career"]
                elif key == pygame.K_3:
                    return DEFAULT_GAME_LENGTHS["Influencer Marathon"]
                elif key == pygame.K_ESCAPE or key == pygame.K_q:
                    return None


def end_screen_loop(state):
    """
    Display the end screen and handle user input for restarting or quitting.
    :param state:
    :return:
    """
    while True:
        draw_end_screen(screen, state)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    return False


def main():
    """
    Main game loop. Handles the game state, user input, and rendering.
    :return:
    """
    while True:
        game_days = start_menu()
        if game_days is None:
            return
        clock = pygame.time.Clock()
        state = GameState(game_days)
        state.start_day()
        icons = load_icons()
        selected_platform = None
        selected_content = None # Not used?
        result_message = ""
        result_delta = 0
        post_timer = 0
        POST_DELAY_FRAMES = 210
        running = True
        while running:
            screen.fill(BLACK)
            draw_header(screen, state, result_message, result_delta)
            draw_news(screen, state, icons)
            if post_timer == 0:
                draw_platforms(screen, icons, selected_platform)
                draw_content_options(screen, selected_platform)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN and post_timer == 0:
                    key = event.key
                    if key == pygame.K_ESCAPE or key == pygame.K_q:
                        return
                    elif key in range(pygame.K_1, pygame.K_1 + len(PLATFORMS)):
                        index = key - pygame.K_1
                        selected_platform = list(PLATFORMS.keys())[index]
                        state.set_platform(selected_platform)
                        selected_content = None
                        result_message = ""
                        result_delta = 0
                    elif selected_platform and key in range(pygame.K_a, pygame.K_a + len(CONTENT_TYPES)):
                        index = key - pygame.K_a
                        if index < len(CONTENT_TYPES):
                            selected_content = list(CONTENT_TYPES.keys())[index]
                            before = state.followers
                            result_message = state.post_content(selected_content)
                            after = state.followers
                            result_delta = after - before
                            post_timer = POST_DELAY_FRAMES
            if post_timer > 0:
                post_timer -= 1
                if post_timer == 0:
                    if state.day < state.total_days:
                        state.next_day()
                        selected_platform = None
                        selected_content = None
                        result_message = ""
                        result_delta = 0
                    else:
                        if end_screen_loop(state):
                            break  # restart the game
                        else:
                            return
            clock.tick(30)


if __name__ == "__main__":
    main()
