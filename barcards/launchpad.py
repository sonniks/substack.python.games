# launchpad.py

import pygame
import sys
import os
from games import blackjack, poker
#from games import blackjack
import tests.test_svg_parser as svg_test
import soundfx
from hud import HUD
from svg_parser import load_deck
from music import init_music, set_volume, get_volume, is_music_active
from soundfx import play_card_sound


pygame.init()

WIDTH, HEIGHT = 1200, 900
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bar Cards Launchpad")
load_deck("assets/images/Full-Deck-Of-Ornate-Playing-Cards.svg")
BLUE = (0, 0, 200)
WHITE = (255, 255, 255)
FONT_PATH = "assets/fonts/8-bit-pusab.ttf"
FONT_SIZE = 12
font = pygame.font.Font(FONT_PATH, FONT_SIZE)
hud = HUD(bankroll=1000)


def draw_menu():
    """
    Draws the main menu options on the screen.
    :return:
    """
    options = [
        "Press B to play Blackjack",
        "Press J to play Jacks or Better",
        "Press Q to Quit",
        "Press up or down to adjust music volume",
        "Press left or right to adjust sound effects volume"
    ]
    for i, line in enumerate(options):
        text_surface = font.render(line, True, WHITE)
        SCREEN.blit(text_surface, (100, 150 + i * 70))

def main():
    """
    Main loop for the launchpad application.
    :return:
    """
    clock = pygame.time.Clock()
    init_music()
    background_path = os.path.join("assets", "images", "splashbackground.png")
    background = pygame.image.load(background_path).convert()
    while True:
        SCREEN.blit(background, (0, 0))  # <-- Background first
        hud.draw(SCREEN)
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                key = event.key
                if key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif key == pygame.K_b:
                    blackjack.mainloop(SCREEN, hud)
                elif key == pygame.K_j:
                    poker.mainloop(SCREEN, hud)
                elif key == pygame.K_s:
                    svg_test.main(SCREEN)
                elif key == pygame.K_UP:
                    set_volume(0.1)
                elif key == pygame.K_DOWN:
                    set_volume(-0.1)
                elif key == pygame.K_LEFT:
                    soundfx.set_volume(-0.1)
                    play_card_sound()
                elif key == pygame.K_RIGHT:
                    soundfx.set_volume(0.1)
                    play_card_sound()
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
