# input.py


import pygame


def get_movement_input(keys):
    """
    Get movement input from the current key states.
    :param keys:
    :return:
    """
    dx, dy = 0, 0
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        dy = -1
    elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
        dy = 1
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        dx = -1
    elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        dx = 1
    # print(f"dx={dx}, dy={dy}")
    return dx, dy
