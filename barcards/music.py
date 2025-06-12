# music.py

import pygame
import os


MUSIC_PATH = "assets/sounds/piano-groove.mod"
_music_loaded = False


def init_music():
    """
    Initializes the music player and loads the music file.
    :return:
    """
    global _music_loaded
    try:
        pygame.mixer.init()
        if os.path.exists(MUSIC_PATH):
            pygame.mixer.music.load(MUSIC_PATH)
            pygame.mixer.music.play(-1)  # loop indefinitely
            _music_loaded = True
    except Exception:
        _music_loaded = False


def set_volume(delta):
    """
    Adjusts the music volume by a delta value.
    :param delta:
    :return:
    """
    if _music_loaded:
        current = pygame.mixer.music.get_volume()
        new_volume = max(0, min(1, current + delta))
        pygame.mixer.music.set_volume(new_volume)


def get_volume():
    """
    Returns the current music volume.
    :return:
    """
    return pygame.mixer.music.get_volume() if _music_loaded else 0


def is_music_active():
    """
    Checks if the music is currently loaded and playing.
    :return:
    """
    return _music_loaded
