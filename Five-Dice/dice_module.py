import random
import pygame
import numpy as np


DICE_SIZE = 80
PIP_RADIUS = 6
PIP_COLOR = (0, 0, 0)
HELD_COLOR = (200, 200, 255)
FREE_COLOR = (255, 255, 255)
ROLL_LIMIT = 3
ROLL_COUNT = 0
FONT = None
CLICK_SOUND = None  # Will be initialized by init_dice_audio()


def generate_click():
    """
    Generate a click sound using numpy.
    :return:
    """
    freq = 1000  # Hz
    duration_ms = 20
    sample_rate = 44100
    samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, duration_ms / 1000, samples, False)
    wave = 0.5 * np.sin(2 * np.pi * freq * t) * (1 - t / (duration_ms / 1000))  # Fade out
    sound_array = np.int16(wave * 32767)
    stereo_array = np.column_stack((sound_array, sound_array))  # 2 channels
    return pygame.sndarray.make_sound(stereo_array)


def init_dice_audio():
    """
    Initialize the dice audio.
    :return:
    """
    global CLICK_SOUND, FONT
    pygame.mixer.init()
    CLICK_SOUND = generate_click()
    CLICK_SOUND.set_volume(0.2)
    FONT = pygame.font.SysFont(None, 36)


def get_pip_positions():
    """
    Get the pip positions for the dice. (Pip locations relative to die center)
    :return:
    """
    offset = DICE_SIZE // 4
    center = DICE_SIZE // 2
    return [
        (center, center),                             # 1 pip
        (center - offset, center - offset),           # TL
        (center + offset, center + offset),           # BR
        (center + offset, center - offset),           # TR
        (center - offset, center + offset),           # BL
        (center - offset, center),                    # ML
        (center + offset, center),                    # MR
    ]

PIP_MAP = {
    1: [0],
    2: [1, 2],
    3: [0, 1, 2],
    4: [1, 2, 3, 4],
    5: [0, 1, 2, 3, 4],
    6: [1, 2, 3, 4, 5, 6]
}

class Die:
    """
    A class representing a single die.
    """
    def __init__(self, x, y):
        self.value = random.randint(1, 6)
        self.held = False
        self.rect = pygame.Rect(x, y, DICE_SIZE, DICE_SIZE)


    def toggle_hold(self):
        """
        Toggle the hold state of the die.
        :return:
        """
        self.held = not self.held


    def roll(self):
        """
        Performs the random roll.
        :return:
        """
        if not self.held:
            self.value = random.randint(1, 6)


    def draw(self, surface):
        """
        Draw the die on the surface.
        :param surface:
        :return:
        """
        color = HELD_COLOR if self.held else FREE_COLOR
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        cx, cy = self.rect.topleft
        pip_positions = get_pip_positions()
        for idx in PIP_MAP[self.value]:
            px, py = pip_positions[idx]
            pygame.draw.circle(surface, PIP_COLOR, (cx + px, cy + py), PIP_RADIUS)


    def animate_roll(self, surface):
        """
        Animate the roll of the die.
        :param surface:
        :return:
        """
        for _ in range(8):
            if not self.held:
                self.value = random.randint(1, 6)
                if CLICK_SOUND:
                    CLICK_SOUND.play()
            self.draw(surface)
            draw_roll_indicator(surface)
            pygame.display.update()
            pygame.time.delay(50)


def roll_dice(dice_list, surface):
    """
    Roll the dice.
    :param dice_list:
    :param surface:
    :return:
    """
    global ROLL_COUNT
    if ROLL_COUNT < ROLL_LIMIT:
        ROLL_COUNT += 1
        for die in dice_list:
            die.animate_roll(surface)


def reset_dice(dice_list):
    """
    Reset the dice.
    :param dice_list:
    :return:
    """
    global ROLL_COUNT
    for die in dice_list:
        die.held = False
    ROLL_COUNT = 0


def draw_roll_indicator(surface):
    """
    Draw the roll indicator.  (Number of rolls of three allowed)
    :param surface:
    :return:
    """
    if FONT:
        # Clear the previous text area
        pygame.draw.rect(surface, (220, 220, 220), (400, 20, 180, 40))  # Match your background
        text = FONT.render(f"Roll: {ROLL_COUNT} / {ROLL_LIMIT}", True, (0, 0, 0))
        surface.blit(text, (400, 20))


def can_score():
    """
    Check if scoring is possible.  (Prevents "slotting" a score before rolling)
    :return:
    """
    return ROLL_COUNT > 0