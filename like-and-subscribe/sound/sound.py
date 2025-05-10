# sound.py

import numpy as np
import pygame


SAMPLE_RATE = 44100
VOLUME = 0.1  # Low volume to avoid being annoying

sounds = {}


def generate_tone(frequency, duration):
    """
    Generate a sine wave tone for the given frequency and duration.
    :param frequency:
    :param duration:
    :return:
    """
    samples = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    waveform = np.sin(2 * np.pi * frequency * samples)
    waveform = (waveform * 32767).astype(np.int16)
    stereo_wave = np.column_stack([waveform, waveform])
    return pygame.mixer.Sound(buffer=stereo_wave.tobytes())


def init_sounds():
    """
    Initialize the sounds used in the game.
    :return:
    """
    pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2)
    global sounds
    sounds = {
        "news_in": generate_tone(800, 0.1),   # soft chirp
        "news_out": generate_tone(400, 0.1),  # soft low tone
    }
    for s in sounds.values():
        s.set_volume(VOLUME)


def play(name):
    """
    Play the sound associated with the given name.
    :param name:
    :return:
    """
    if name in sounds:
        sounds[name].play()
