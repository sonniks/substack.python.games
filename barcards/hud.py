# hud.py

import pygame

WHITE = (255, 255, 255)
FONT_PATH = "assets/fonts/8-bit-pusab.ttf"
FONT_SIZE = 12

class HUD:
    """
    Heads-Up Display (HUD) for displaying bankroll and current wager in a game.
    """
    def __init__(self, bankroll):
        self.bankroll = bankroll
        self.current_wager = 0
        self.font = pygame.font.Font(FONT_PATH, FONT_SIZE)


    def draw(self, surface):
        """
        Draws the HUD on the given surface, displaying bankroll and current wager.
        :param surface:
        :return:
        """
        # Clear HUD area first
        pygame.draw.rect(surface, (0, 0, 200), (0, 0, 1200, 40))  # match background blue
        text = f"Bankroll: ${self.bankroll}"
        if self.current_wager:
            text += f"   Current Wager: ${self.current_wager}"
        hud_surface = self.font.render(text, True, WHITE)
        surface.blit(hud_surface, (20, 10))


    def set_bankroll(self, amount):
        """
        Sets the bankroll to a specified amount.
        :param amount:
        :return:
        """
        self.bankroll = amount


    def get_bankroll(self):
        """
        Returns the current bankroll.
        :return:
        """
        return self.bankroll


    def set_wager(self, amount):
        """
        Sets the current wager to a specified amount.
        :param amount:
        :return:
        """
        self.current_wager = amount


    def clear_wager(self):
        """
        Clears the current wager, setting it to zero.
        :return:
        """
        self.current_wager = 0
