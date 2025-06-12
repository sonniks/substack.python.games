# tests/test_svg_parser.py

import pygame
import random
import sys
from svg_parser import load_deck


def main(screen: pygame.Surface):
    """
    Main function to run the SVG parser test.
    :param screen:
    :return:
    """
    deck = load_deck("assets/images/Full-Deck-Of-Ornate-Playing-Cards.svg")
    card = random.choice(deck)
    screen.fill((0, 100, 0))  # dark green background
    card_x = (screen.get_width() - card.image.get_width()) // 2
    card_y = (screen.get_height() - card.image.get_height()) // 2
    screen.blit(card.image, (card_x, card_y))
    font = pygame.font.Font("assets/fonts/8-bit-pusab.ttf", 36)
    label = f"{card.rank} of {card.suit} (value={card.value})"
    text_surface = font.render(label, True, (255, 255, 255))
    text_x = (screen.get_width() - text_surface.get_width()) // 2
    screen.blit(text_surface, (text_x, card_y + card.image.get_height() + 20))
    pygame.display.flip()
    pygame.time.wait(2000)  # pause for 2 seconds
