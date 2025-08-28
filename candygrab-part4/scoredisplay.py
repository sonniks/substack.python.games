# scoredisplay.py


import pygame
from loader import TILE_SIZE

UI_HEIGHT = 96
# FONT_PATH = "assets/fonts/8-bit-pusab.ttf"
FONT_PATH = "assets/fonts/Eight-Bit Madness.ttf"
SPRITESHEET_PATH = "assets/sprites/sheet.png"
PADDING = 12
ICON_SPACING = 8
TEXT_COLOR = (255, 255, 255)
BAR_BG = (0, 0, 0)


class ScoreDisplay:
    def __init__(self, screen_width, ui_height=UI_HEIGHT, font_size=36):  # smaller font
        self.screen_width = screen_width
        self.ui_height = ui_height
        self.font = pygame.font.Font(FONT_PATH, font_size)
        self.life_icon = self._load_icon()

    def _load_icon(self):
        """
        Load the life icon from the spritesheet (first tile).
        :return:
        """
        sheet = pygame.image.load(SPRITESHEET_PATH).convert_alpha()
        rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        return sheet.subsurface(rect)


    def draw(self, surface, level_number, score, lives):
        """
        Draw the score display bar.
        :param surface:
        :param level_number:
        :param score:
        :param lives:
        :return:
        """
        pygame.draw.rect(surface, BAR_BG, pygame.Rect(0, 0, self.screen_width, self.ui_height))
        icons_to_show = max(0, lives - 1)
        x = PADDING
        y = (self.ui_height - TILE_SIZE) // 2
        for _ in range(icons_to_show):
            surface.blit(self.life_icon, (x, y))
            x += TILE_SIZE + ICON_SPACING
        level_text = f"LEVEL {level_number}"  # title case
        level_surf = self.font.render(level_text, True, TEXT_COLOR)
        level_x = (self.screen_width - level_surf.get_width()) // 2
        level_y = (self.ui_height - level_surf.get_height()) // 2
        surface.blit(level_surf, (level_x, level_y))
        score_text = f"{score:,}"
        score_surf = self.font.render(score_text, True, TEXT_COLOR)
        score_x = self.screen_width - PADDING - score_surf.get_width()
        score_y = (self.ui_height - score_surf.get_height()) // 2
        surface.blit(score_surf, (score_x, score_y))
