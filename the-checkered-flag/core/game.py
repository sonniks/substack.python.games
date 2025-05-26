# core/game.py


import pygame
from core.track import Track
from core.car import PlayerCar, AICar


class Game:
    def __init__(self, track: Track, player: PlayerCar, ai_cars: list):
        self.track = track
        self.player = player
        self.ai_cars = ai_cars
        self.font = pygame.font.SysFont("Arial", 24)

    def update(self, mouse_pos, mouse_buttons):
        """
        Update the game state based on player input and AI logic.
        :param mouse_pos:
        :param mouse_buttons:
        :return:
        """
        self.player.update(mouse_pos, mouse_buttons, self.track)
        for ai in self.ai_cars:
            ai.update(self.track)

    def draw(self, surface):
        """
        Draw the game elements on the given surface.
        :param surface:
        :return:
        """
        self.track.draw(surface)
        for ai in self.ai_cars:
            ai.draw(surface)
        self.player.draw(surface)
        self._draw_hud(surface)

    def _draw_hud(self, surface):
        """
        Draw the heads-up display (HUD) with player and AI stats.
        :param surface:
        :return:
        """
        white = (255, 255, 255)
        black = (0, 0, 0)
        player_lap = f"Player Lap: {min(self.player.lap_count + 1, self.track.laps_required)} / {self.track.laps_required}"
        cp_text = f"Checkpoints: {len(self.player.checkpoints_hit)} / {len(self.track.waypoints)}"
        fastest_ai = max(self.ai_cars, key=lambda ai: ai.lap_count)
        ai_lap = f"Fastest AI Lap: {min(fastest_ai.lap_count + 1, self.track.laps_required)} / {self.track.laps_required}"
        texts = [player_lap, cp_text, ai_lap]
        x = 10
        y = 485  # just below the 480px track
        for text in texts:
            shadow = self.font.render(text, True, black)
            label = self.font.render(text, True, white)
            surface.blit(shadow, (x + 1, y + 1))
            surface.blit(label, (x, y))
            x += label.get_width() + 40  # spacing between entries

    def check_race_complete(self):
        """
        Check to see if the race (specific track) is complete.
        :return:
        """
        if self.player.lap_count >= self.track.laps_required:
            # print("Player wins!")
            return True
        for idx, ai in enumerate(self.ai_cars):
            if ai.lap_count >= self.track.laps_required:
                # print(f"AI Car {idx + 1} wins!")
                return True
        return False

