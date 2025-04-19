#scoring.py
import pygame
import surface

GOAL_WIDTH = surface.GOAL_WIDTH
GOAL_HEIGHT = surface.GOAL_HEIGHT


# Font for score and Game Over
pygame.font.init()
font = pygame.font.SysFont("Arial", 36)
big_font = pygame.font.SysFont("Arial", 64, bold=True)


def check_goals(puck, score):
    """
    Checks if the puck has entered a goal area and updates the score accordingly.
    :param puck:
    :param score:
    :return:
    """
    center_x = surface.FIELD_WIDTH // 2
    goal_left = center_x - surface.GOAL_WIDTH // 2
    goal_right = center_x + surface.GOAL_WIDTH // 2
    # Top goal (AI scores)
    if puck.top <= surface.GOAL_HEIGHT:
        if goal_left < puck.centerx < goal_right:
            score[1] += 1
            return "player"
    # Bottom goal (Player scores)
    elif puck.bottom >= surface.FIELD_HEIGHT - surface.GOAL_HEIGHT:
        if goal_left < puck.centerx < goal_right:
            score[0] += 1
            return "ai"
    return None  # No goal


def reset_puck(puck, scorer):
    """
    Resets the puck to the center of the field and sets its velocity toward the scorer.
    :param puck:
    :param scorer:
    :return:
    """
    puck.center = (surface.FIELD_WIDTH // 2, surface.FIELD_HEIGHT // 2)
    # Slow down puck and direct it TOWARD the scorer
    # Debating if puck should go to victor or loser...?
    import physics
    if scorer == "player":
        physics.puck_vel[0] = 1.5
        physics.puck_vel[1] = 1.5  # down toward player
    else:
        physics.puck_vel[0] = -1.5
        physics.puck_vel[1] = -1.5  # up toward AI


def draw_score(screen, score, game_over):
    """
    Draws the current score and a Game Over message if applicable.
    :param screen:
    :param score:
    :param game_over:
    :return:
    """
    # Draw scores
    ai_score = font.render(f"AI: {score[0]}", True, (255, 0, 0))
    player_score = font.render(f"You: {score[1]}", True, (0, 0, 255))
    screen.blit(ai_score, (10, 10))
    screen.blit(player_score, (surface.FIELD_WIDTH - player_score.get_width() - 10, 10))
    # Game over message
    if game_over:
        text = big_font.render("GAME OVER", True, (50, 50, 50))
        screen.blit(text, (
            (surface.FIELD_WIDTH - text.get_width()) // 2,
            (surface.FIELD_HEIGHT - text.get_height()) // 2
        ))
