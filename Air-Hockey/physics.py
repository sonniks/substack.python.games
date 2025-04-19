#physics.py
import pygame
import numpy as np
import surface


# Initialize mixer if not already done
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mixer.init()


# Puck velocity
puck_vel = [4, 4]


def generate_click():
    """
    Generates a click sound effect for puck collisions.
    :return:
    """
    freq = 1200  # Frequency in Hz
    duration_ms = 60
    sample_rate = 44100
    samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, duration_ms / 1000, samples, False)
    wave = 0.5 * np.sin(2 * np.pi * freq * t)
    wave *= np.exp(-30 * t)  # Fast decay
    # Convert to 16-bit PCM
    mono = (wave * 32767).astype(np.int16)
    # If stereo is enabled, duplicate mono into two channels
    stereo = np.column_stack((mono, mono))
    return pygame.sndarray.make_sound(stereo)


click_sound = generate_click()


def update_puck(puck, player, ai, slam_shot, air_resistance):
    """
    Updates the puck's position and handles collisions with walls, paddles, and air resistance.
    :param puck:
    :param player:
    :param ai:
    :param slam_shot:
    :param air_resistance:
    :return:
    """
    global puck_vel
    # Move puck
    puck.x += int(puck_vel[0])
    puck.y += int(puck_vel[1])
    # Air resistance
    puck_vel[0] *= air_resistance
    puck_vel[1] *= air_resistance
    # Wall collisions
    if puck.left <= 0:
        puck.left = 1  # push off wall
        puck_vel[0] = abs(puck_vel[0])
        click_sound.play()
    elif puck.right >= surface.FIELD_WIDTH:
        puck.right = surface.FIELD_WIDTH - 1
        puck_vel[0] = -abs(puck_vel[0])
        click_sound.play()
    # Vertical wall collisions (excluding goal area)
    goal_left = (surface.FIELD_WIDTH - surface.GOAL_WIDTH) // 2
    goal_right = goal_left + surface.GOAL_WIDTH
    # Top wall (outside goal)
    if puck.top <= 0 and not (goal_left < puck.centerx < goal_right):
        puck.top = 1
        puck_vel[1] = abs(puck_vel[1])
        click_sound.play()
    # Bottom wall (outside goal)
    elif puck.bottom >= surface.FIELD_HEIGHT and not (goal_left < puck.centerx < goal_right):
        puck.bottom = surface.FIELD_HEIGHT - 1
        puck_vel[1] = -abs(puck_vel[1])
        click_sound.play()
    if puck.top <= 0 or puck.bottom >= surface.FIELD_HEIGHT:
        puck_vel[1] *= -1
        click_sound.play()
    # Paddle collisions (player and AI)
    if puck.colliderect(player) and puck.centery > surface.CENTER_LINE:
        apply_slam(puck_vel, player, puck, slam_shot)
        click_sound.play()
    if puck.colliderect(ai) and puck.centery < surface.CENTER_LINE:
        apply_ai_hit(puck_vel, ai, puck)
        click_sound.play()


#
# This version allows inadvertent goals on self, just like real air hockey - but I don't like the collision
# detection behavior with this, and can't figure it out at the moment.
#
# def apply_slam(puck_vel, paddle, puck, slam_shot):
#     strength = 8 if slam_shot else 3
#
#     # Horizontal control stays dynamic
#     puck_vel[0] += (0.4 if slam_shot else 0.2) * (paddle.centerx - puck.centerx)
#
#     # Now intelligently apply vertical force AWAY from paddle
#     dy = puck.centery - paddle.centery
#
#     if abs(dy) < 20:
#         # Too close to apply solid directional force — skip Y change
#         return
#
#     if dy > 0:
#         # Puck is below paddle → push downward
#         puck_vel[1] += strength
#     else:
#         # Puck is above paddle → push upward
#         puck_vel[1] -= strength


def apply_slam(puck_vel, paddle, puck, slam_shot):
    """
    Applies a slam shot effect to the puck when the player paddle collides with it (mouse down on hit).
    :param puck_vel:
    :param paddle:
    :param puck:
    :param slam_shot:
    :return:
    """
    if slam_shot:
        puck_vel[1] -= 8  # strong upward force (toward AI goal)
        puck_vel[0] += (0.4 * (paddle.centerx - puck.centerx))
    else:
        puck_vel[1] -= 3  # weaker upward
        puck_vel[0] += (0.2 * (paddle.centerx - puck.centerx))


def apply_ai_hit(puck_vel, ai, puck):
    """
    Applies the AI paddle hit effect to the puck when it collides with the AI paddle.
    :param puck_vel:
    :param ai:
    :param puck:
    :return:
    """
    puck_vel[1] = abs(puck_vel[1]) + 3  # Force puck downward
    puck_vel[0] += (0.3 * (puck.centerx - ai.centerx))  # Directional bounce
