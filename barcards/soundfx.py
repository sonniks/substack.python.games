# soundfx.py

import pygame
import os


pygame.mixer.init()
_sound_cache = {}
sound_volume = 0.5  # Default starting volume (range: 0.0 to 1.0)


def _load_sound(path):
    """
    Loads a sound file from the given path, caching it for future use.
    :param path:
    :return:
    """
    if path not in _sound_cache:
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(sound_volume)
            _sound_cache[path] = sound
        except pygame.error as e:
            print(f"Error loading sound: {e}")
            return None
    return _sound_cache[path]


def play_card_sound():
    """
    Plays the card dealing sound effect.
    :return:
    """
    path = os.path.join("assets", "sounds", "carddeal.wav")
    sound = _load_sound(path)
    if sound:
        sound.play()


def set_volume(delta):
    """
    Adjusts the global sound volume by a delta value.
    :param delta:
    :return:
    """
    global sound_volume
    sound_volume = max(0.0, min(1.0, sound_volume + delta))
    for snd in _sound_cache.values():
        snd.set_volume(sound_volume)


def get_volume():
    """
    Returns the current global sound volume.
    :return:
    """
    return sound_volume
