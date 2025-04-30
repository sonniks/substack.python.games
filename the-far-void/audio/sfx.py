# audio/sfx.py
import pygame
import numpy as np


SOUND_ENABLED = True


pygame.mixer.init(frequency=44100, size=-16, channels=1)
_sample_rate = 44100


def generate_tone(frequency, duration, volume=0.5, wave_type='sine'):
    """
    Generate a sound wave of the specified frequency, duration, volume, and wave type.
    :param frequency:
    :param duration:
    :param volume:
    :param wave_type:
    :return:
    """
    t = np.linspace(0, duration, int(_sample_rate * duration), False)
    if wave_type == 'square':
        wave = np.sign(np.sin(2 * np.pi * frequency * t))
    elif wave_type == 'saw':
        wave = 2 * (t * frequency - np.floor(0.5 + t * frequency))
    else:
        wave = np.sin(2 * np.pi * frequency * t)
    mono = (volume * wave * 32767).astype(np.int16)
    stereo = np.column_stack((mono, mono))
    sound = pygame.sndarray.make_sound(stereo)
    return sound


def play_tone(frequency=440, duration=0.2, volume=0.5, wave_type='sine'):
    """
    Play a sound of the specified frequency, duration, volume, and wave type.
    :param frequency:
    :param duration:
    :param volume:
    :param wave_type:
    :return:
    """
    if not SOUND_ENABLED:
        return
    tone = generate_tone(frequency, duration, volume, wave_type)
    tone.play()
