# render/fonts.py
import pygame


_font_cache = {}


def get_font(size):
    """
    Retrieve a font of the specified size from the cache, or load it if not already cached.
    :param size:
    :return:
    """
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font("assets/fonts/Hyperspace.otf", size)
    return _font_cache[size]


def draw_text(screen, text, size, x, y, color=(0, 255, 0)):
    """
    Draw text on the screen at the specified position with the given size and color.
    :param screen:
    :param text:
    :param size:
    :param x:
    :param y:
    :param color:
    :return:
    """
    font = get_font(size)
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))
