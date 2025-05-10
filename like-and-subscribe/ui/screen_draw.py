# ui/screen_draw.py

import pygame
import os
from data.game_data import PLATFORMS, CONTENT_TYPES


FONT = None
BIG_FONT = None
NEWS_FONT = None
CONTENT_FONT = None

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (160, 160, 160)
DARK_GRAY = (40, 40, 40)
BLUE = (80, 160, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

ICON_SIZE = (32, 32)


def setup_fonts():
    """
    Initialize the fonts used in the game. This function sets up the
    :return:
    """
    global FONT, BIG_FONT, NEWS_FONT, CONTENT_FONT
    FONT = pygame.font.SysFont("Arial", 24)
    BIG_FONT = pygame.font.SysFont("Arial", 30)
    NEWS_FONT = pygame.font.SysFont("Arial", 20)
    CONTENT_FONT = pygame.font.SysFont("Arial", 20)


def draw_text(surface, text, pos, font=None, color=WHITE, max_lines=10):
    """
    Draw text on the given surface at the specified position.
    :param surface:
    :param text:
    :param pos:
    :param font:
    :param color:
    :param max_lines:
    :return:
    """
    if font is None:
        raise RuntimeError("Font not initialized. Call setup_fonts() before using draw_text.")
    lines = text.splitlines()[:max_lines]
    y = pos[1]
    for line in lines:
        rendered = font.render(line, True, color)
        surface.blit(rendered, (pos[0], y))
        y += rendered.get_height() + 4


def load_icons():
    """
    Load icons for the platforms and news.
    :return:
    """
    icons = {}
    asset_dir = "assets"
    for platform in PLATFORMS.keys():
        fname = f"{platform.lower()}.png"
        path = os.path.join(asset_dir, fname)
        if os.path.exists(path):
            icon = pygame.image.load(path).convert_alpha()
            icon = pygame.transform.scale(icon, ICON_SIZE)
            icons[platform] = icon
        else:
            fallback = os.path.join(asset_dir, "default.png")
            if os.path.exists(fallback):
                icon = pygame.image.load(fallback).convert_alpha()
                icon = pygame.transform.scale(icon, ICON_SIZE)
                icons[platform] = icon
            else:
                icons[platform] = None
    news_path = os.path.join(asset_dir, "news.png")
    if os.path.exists(news_path):
        icon = pygame.image.load(news_path).convert_alpha()
        icon = pygame.transform.scale(icon, ICON_SIZE)
        icons["news"] = icon
    else:
        icons["news"] = None
    return icons


def draw_header(screen, state, result_message, result_delta):
    """
    Draw the header section of the game screen, including the day, energy,
    :param screen:
    :param state:
    :param result_message:
    :param result_delta:
    :return:
    """
    draw_text(screen, f"Day {state.day}/{state.total_days}   Energy: {state.energy}/4", (20, 20), FONT)
    follower_color = GREEN if result_delta > 0 else RED if result_delta < 0 else WHITE
    draw_text(screen, f"Followers: {state.followers}", (20, 50), FONT, follower_color)
    draw_text(screen, f"Revenue: ${state.ad_revenue:.2f}", (250, 50), FONT)
    if result_message:
        pygame.draw.rect(screen, DARK_GRAY, (20, 90, 440, 70))
        draw_text(screen, result_message, (30, 100), FONT, WHITE, max_lines=2)


def draw_news(screen, state, icons):
    """
    Draw the news section of the game screen.
    :param screen:
    :param state:
    :param icons:
    :return:
    """
    draw_text(screen, "News:", (20, 180), BIG_FONT)
    y_offset = 220
    max_items = 2
    for i, n in enumerate(state.news[:max_items]):
        remaining = n["duration"] - (state.day - n["start_day"])
        remaining = max(1, remaining)
        text = f"{n['headline']} ({remaining}d left)"
        if icons.get("news"):
            screen.blit(icons["news"], (40, y_offset))
            draw_text(screen, text, (80, y_offset), NEWS_FONT, GRAY)
        else:
            draw_text(screen, text, (40, y_offset), NEWS_FONT, GRAY)
        y_offset += 30
    if not state.news:
        draw_text(screen, "No trending news", (40, y_offset), NEWS_FONT, GRAY)


def draw_platforms(screen, icons, selected_platform):
    """
    Draw the platform selection screen.
    :param screen:
    :param icons:
    :param selected_platform:
    :return:
    """
    draw_text(screen, "Pick a Platform:", (20, 320), BIG_FONT)
    for idx, name in enumerate(PLATFORMS.keys()):
        y_pos = 360 + idx * 36
        icon = icons.get(name)
        if icon:
            screen.blit(icon, (10, y_pos))
        else:
            pygame.draw.rect(screen, GRAY, (10, y_pos, 32, 32))
        color = BLUE if name == selected_platform else WHITE
        draw_text(screen, f"{idx + 1}. {name}", (50, y_pos + 6), FONT, color)


def draw_content_options(screen, selected_platform):
    """
    Draw the content options for the selected platform.
    :param screen:
    :param selected_platform:
    :return:
    """
    if selected_platform:
        draw_text(screen, "Pick Content:", (20, 620), BIG_FONT)
        content_keys = list(CONTENT_TYPES.keys())
        col_x = [40, 260]
        row_start = 660
        for idx, ctype in enumerate(content_keys):
            col = idx % 2
            row = idx // 2
            x = col_x[col]
            y = row_start + row * 26
            label = f"{chr(65 + idx)}. {ctype}  (E: {CONTENT_TYPES[ctype]['energy']})"
            draw_text(screen, label, (x, y), CONTENT_FONT, WHITE)


def draw_end_screen(screen, state):
    """
    Draw the end screen when the game is over.
    :param screen:
    :param state:
    :return:
    """
    screen.fill(BLACK)
    draw_text(screen, "Game Over", (140, 200), BIG_FONT, RED)
    draw_text(screen, f"Total Followers: {state.followers}", (100, 260), FONT)
    draw_text(screen, f"Total Revenue: ${state.ad_revenue:.2f}", (100, 300), FONT)
    draw_text(screen, "Press ENTER to Restart or Q to Quit", (40, 360), FONT, WHITE)
    pygame.display.flip()
