#ai_player.py
import surface
import random


# Difficulty settings — tweak these!
DEFENSE_SPEED = 4       # Max pixels per frame the AI can move
AIM_ACCURACY = 0.8      # 0.0 = terrible aim, 1.0 = sniper mode


def move_ai(ai_rect, puck_rect):
    """
    Handles general AI movement logic based on puck position.
    :param ai_rect:
    :param puck_rect:
    :return:
    """
    # Only move when puck is on AI's side
    if puck_rect.centery < surface.CENTER_LINE:
        # Move horizontally
        if puck_rect.centerx < ai_rect.centerx:
            ai_rect.centerx -= DEFENSE_SPEED
        elif puck_rect.centerx > ai_rect.centerx:
            ai_rect.centerx += DEFENSE_SPEED
        # Move vertically
        if puck_rect.centery < ai_rect.centery:
            ai_rect.centery -= DEFENSE_SPEED
        elif puck_rect.centery > ai_rect.centery:
            ai_rect.centery += DEFENSE_SPEED
    else:
        # Chill near centerline if puck is on player's side
        center_x = surface.FIELD_WIDTH // 2
        center_y = surface.CENTER_LINE // 2
        if ai_rect.centerx < center_x:
            ai_rect.centerx += 1
        elif ai_rect.centerx > center_x:
            ai_rect.centerx -= 1
        if ai_rect.centery < center_y:
            ai_rect.centery += 1
        elif ai_rect.centery > center_y:
            ai_rect.centery -= 1
    # Clamp to top half of the field
    ai_rect.centerx = max(0, min(ai_rect.centerx, surface.FIELD_WIDTH))
    ai_rect.centery = max(20, min(ai_rect.centery, surface.CENTER_LINE - 20))