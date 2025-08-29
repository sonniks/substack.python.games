# visualeffects.py


import pygame
import colorsys
import numpy as np
import pygame.surfarray


def hue_shift_sprite(surface, shift):
    if shift == 0:
        return surface.copy()  # cheap copy with no processing

    surface = surface.convert_alpha()
    rgb_array = pygame.surfarray.array3d(surface).astype(np.float32) / 255.0
    alpha_array = pygame.surfarray.array_alpha(surface)

    r, g, b = rgb_array[..., 0], rgb_array[..., 1], rgb_array[..., 2]

    # Flatten for vectorized HSV conversion
    flat_rgb = np.stack((r.flatten(), g.flatten(), b.flatten()), axis=1)
    hsv = np.array([colorsys.rgb_to_hsv(*px) for px in flat_rgb])
    hsv[:, 0] = (hsv[:, 0] + shift) % 1.0
    new_rgb = np.array([colorsys.hsv_to_rgb(*px) for px in hsv])

    # Reshape and scale back to 0-255
    rgb_shifted = new_rgb.reshape(rgb_array.shape) * 255.0
    rgb_shifted = rgb_shifted.astype(np.uint8)

    result = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    pygame.surfarray.blit_array(result, rgb_shifted)
    result_lock = pygame.surfarray.pixels_alpha(result)
    result_lock[:, :] = alpha_array
    del result_lock

    return result

