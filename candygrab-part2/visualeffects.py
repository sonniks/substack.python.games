# visualeffects.py

import pygame

def hue_shift_sprite(surface, shift):
    import colorsys
    import pygame.surfarray

    surface = surface.convert_alpha()
    width, height = surface.get_size()

    # Extract both RGB and Alpha
    rgb_array = pygame.surfarray.array3d(surface).astype(float)
    alpha_array = pygame.surfarray.array_alpha(surface)

    # Prepare output array
    new_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    for x in range(width):
        for y in range(height):
            r, g, b = rgb_array[x, y] / 255.0
            a = alpha_array[x, y]
            if a == 0:
                continue  # fully transparent pixel; skip color shift
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            h = (h + shift) % 1.0
            r2, g2, b2 = colorsys.hsv_to_rgb(h, s, v)
            rgb = (int(r2 * 255), int(g2 * 255), int(b2 * 255), a)
            new_surface.set_at((x, y), rgb)

    return new_surface

