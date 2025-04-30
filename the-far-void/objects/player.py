# objects/player.py
import pygame


player_pos = [400, 550]
player_speed = 5


def update_player():
    """
    Update the player's position based on keyboard input.
    :return:
    """
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_pos[0] -= player_speed
    if keys[pygame.K_RIGHT]:
        player_pos[0] += player_speed
    if keys[pygame.K_UP]:
        player_pos[1] -= player_speed
    if keys[pygame.K_DOWN]:
        player_pos[1] += player_speed
    # Boundaries
    player_pos[0] = max(0, min(800, player_pos[0]))
    player_pos[1] = max(0, min(600, player_pos[1]))


def draw_player(screen):
    """
    Draw the player on the screen as a triangle.
    :param screen:
    :return:
    """
    points = [
        (player_pos[0], player_pos[1] - 10),
        (player_pos[0] - 8, player_pos[1] + 8),
        (player_pos[0] + 8, player_pos[1] + 8)
    ]
    pygame.draw.polygon(screen, (0, 255, 0), points, 1)
