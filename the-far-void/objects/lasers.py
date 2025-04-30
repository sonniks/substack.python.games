# objects/lasers.py
import pygame
from audio.sfx import play_tone


lasers = []
speed = -8
color = (0, 255, 0)
cooldown = 200  # milliseconds
_last_fired = 0


def update_lasers():
    """
    Update the position of all lasers and remove those that are off-screen.
    :return:
    """
    for laser in lasers:
        laser[1] += speed
    lasers[:] = [l for l in lasers if l[1] > -20]


def draw_lasers(screen):
    """
    Draw all lasers on the screen.
    :param screen:
    :return:
    """
    for x, y in lasers:
        pygame.draw.line(screen, color, (x, y), (x, y + 10), 2)


def fire_laser(x, y):
    """
    Fire a laser from the specified position if the cooldown period has passed.
    :param x:
    :param y:
    :return:
    """
    global _last_fired
    now = pygame.time.get_ticks()
    if now - _last_fired >= cooldown:
        lasers.append([x, y])
        _last_fired = now
        play_tone(440, 0.04, volume=0.3, wave_type='saw')
