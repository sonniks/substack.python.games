#surface.py
import pygame


# Define dimensions
FIELD_WIDTH = 600
FIELD_HEIGHT = 800
CENTER_LINE = FIELD_HEIGHT // 2
GOAL_WIDTH = 200
GOAL_HEIGHT = 10
TITLE_HEIGHT = 80


def init_window():
    """
    Initializes the Pygame window for the Air Hockey game.
    :return:
    """
    pygame.init()
    screen = pygame.display.set_mode((FIELD_WIDTH, FIELD_HEIGHT))
    pygame.display.set_caption("Air Hockey")
    return screen


def draw_surface(screen):
    """
    Draws the game surface including the center line, goals, and title banner.
    :param screen:
    :return:
    """
    screen.fill((255, 255, 255))  # White background
    # Draw "center ice"
    pygame.draw.line(screen, (0, 0, 0), (0, CENTER_LINE), (FIELD_WIDTH, CENTER_LINE), 2)
    # Draw goals
    pygame.draw.rect(screen, (255, 0, 0), ((FIELD_WIDTH - GOAL_WIDTH) // 2, 0, GOAL_WIDTH, GOAL_HEIGHT))
    pygame.draw.rect(screen, (0, 0, 255), ((FIELD_WIDTH - GOAL_WIDTH) // 2, FIELD_HEIGHT - GOAL_HEIGHT,
                                           GOAL_WIDTH, GOAL_HEIGHT))
    # Draw AIR HOCKEY banner (placeholder)
    font = pygame.font.SysFont("Arial", 48, bold=True)
    text_surface = font.render("AIR HOCKEY", True, (100, 100, 100))
    screen.blit(text_surface, ((FIELD_WIDTH - text_surface.get_width()) // 2, TITLE_HEIGHT // 4))
