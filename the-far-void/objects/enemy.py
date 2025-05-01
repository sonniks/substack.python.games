# objects/enemy.py
import pygame
import random
from audio.sfx import play_tone


enemies = []
explosions = []
boss_active = False
boss_triggered_stage = None
BOSS_WIDTH = 800
BOSS_HEIGHT = 60
ENEMY_SIZE = 30
# Below, items for adjusting game difficulty
speed = 2
spawn_timer = 0
spawn_interval = 1000
score = 0
lives = 3
stage = 1
boss_hp = 0
boss_pos = [0, -100]
boss_speed = 1
SHIELD_REWARD_SCORE = 3000


def spawn_enemy():
    """
    Spawn a new enemy at a random horizontal position at the top of the screen.
    :return:
    """
    x = random.randint(ENEMY_SIZE, 800 - ENEMY_SIZE)
    y = -ENEMY_SIZE
    enemies.append([x, y])


def spawn_boss():
    """
    Spawn a boss enemy when the stage is appropriate.
    :return:
    """
    global boss_active, boss_hp, boss_pos, boss_speed, boss_triggered_stage
    boss_active = True
    boss_hp = 20 + stage * 2
    boss_speed = 1 + stage // 5
    boss_pos = [0, -BOSS_HEIGHT]
    boss_triggered_stage = stage
    play_tone(220, 0.5, volume=0.5, wave_type='saw')


def update_enemies():
    """
    Update the position of enemies, spawn new ones, and handle boss spawning logic.
    :return:
    """
    global spawn_timer, boss_pos, boss_active, boss_hp
    if not boss_active and stage >= 3 and stage % 3 == 0 and boss_triggered_stage != stage:
        spawn_boss()
    if boss_active:
        boss_pos[1] += boss_speed
        if boss_pos[1] > 600:
            boss_active = False
        return
    now = pygame.time.get_ticks()
    spawn_rate = max(300, spawn_interval - (stage - 1) * 100)
    if now - spawn_timer > spawn_rate:
        spawn_enemy()
        spawn_timer = now
    for enemy in enemies:
        enemy[1] += speed
    enemies[:] = [e for e in enemies if e[1] < 640]
    for ex in explosions:
        ex[2] -= 1
    explosions[:] = [e for e in explosions if e[2] > 0]


def draw_enemies(screen):
    """
    Draw all enemies and the boss on the screen, including their flickering effect.
    :param screen:
    :return:
    """
    time = pygame.time.get_ticks()
    flicker = (time // 100) % 2 == 0
    color = (255, 50, 50) if flicker else (255, 100, 100)
    if boss_active:
        pulse_color = (255, 0, 255) if (pygame.time.get_ticks() // 250) % 2 == 0 else (255, 0, 0)
        x, y = boss_pos
        pygame.draw.rect(screen, pulse_color, (x, y, BOSS_WIDTH, BOSS_HEIGHT), 3)
        for i in range(0, BOSS_WIDTH, 32):
            pygame.draw.line(screen, pulse_color, (x + i, y + BOSS_HEIGHT), (x + i + 16, y + BOSS_HEIGHT + 12), 2)
        pygame.draw.circle(screen, pulse_color, (x + BOSS_WIDTH // 2, y + BOSS_HEIGHT // 2), 10, 1)
    for x, y in enemies:
        base = [
            (x, y - ENEMY_SIZE // 2),
            (x - ENEMY_SIZE // 2, y + ENEMY_SIZE // 2),
            (x + ENEMY_SIZE // 2, y + ENEMY_SIZE // 2)
        ]
        pygame.draw.polygon(screen, color, base, 2)
        pygame.draw.line(screen, color, (x - ENEMY_SIZE // 2, y + ENEMY_SIZE // 2), (x - ENEMY_SIZE, y), 1)
        pygame.draw.line(screen, color, (x + ENEMY_SIZE // 2, y + ENEMY_SIZE // 2), (x + ENEMY_SIZE, y), 1)
        pygame.draw.line(screen, color, (x, y + ENEMY_SIZE // 2), (x, y + ENEMY_SIZE), 1)
    for x, y, t in explosions:
        pygame.draw.circle(screen, (255, 255, 0), (x, y), 20, 2)


def point_in_triangle(pt, v1, v2, v3):
    """
    Check if a point is inside a triangle defined by three vertices.
    :param pt:
    :param v1:
    :param v2:
    :param v3:
    :return:
    """
    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    b1 = sign(pt, v1, v2) < 0.0
    b2 = sign(pt, v2, v3) < 0.0
    b3 = sign(pt, v3, v1) < 0.0
    return (b1 == b2 == b3)


def check_collision(lasers, player_pos):
    """
    Check for collisions between lasers, enemies, and the player.
    :param lasers:
    :param player_pos:
    :return:
    """
    global enemies, score, lives, explosions, stage, boss_active, boss_hp, boss_triggered_stage
    remaining = []
    player_rect = pygame.Rect(player_pos[0] - 8, player_pos[1] - 10, 16, 18)
    if boss_active:
        boss_rect = pygame.Rect(boss_pos[0], boss_pos[1], BOSS_WIDTH, BOSS_HEIGHT)
        if boss_rect.colliderect(player_rect):
            if lives > 0:
                lives -= 1
                explosions.append([player_pos[0], player_pos[1], 10])
                play_tone(110, 0.3, volume=0.8, wave_type='saw')
        for lx, ly in lasers:
            if boss_rect.collidepoint(lx, ly):
                boss_hp -= 1
                explosions.append([lx, ly, 6])
                play_tone(100 + boss_hp * 10, 0.05, volume=0.4, wave_type='square')
                if boss_hp <= 0:
                    boss_active = False
                    boss_triggered_stage = stage
                    previous_score = score
                    score += 1000
                    if score // SHIELD_REWARD_SCORE > previous_score // SHIELD_REWARD_SCORE:
                        lives += 1
                        play_tone(880, 0.2, volume=0.6, wave_type='sine')
                    explosions.append([boss_pos[0] + BOSS_WIDTH // 2, boss_pos[1] + BOSS_HEIGHT // 2, 15])
                    play_tone(220, 0.4, wave_type='saw')
                break
    for ex, ey in enemies:
        enemy_rect = pygame.Rect(ex - ENEMY_SIZE // 2, ey - ENEMY_SIZE // 2, ENEMY_SIZE, ENEMY_SIZE)
        if enemy_rect.colliderect(player_rect):
            if lives > 0:
                lives -= 1
                explosions.append([player_pos[0], player_pos[1], 10])
                play_tone(110, 0.3, volume=0.8, wave_type='saw')
            continue
        hit = False
        triangle = [
            (ex, ey - ENEMY_SIZE // 2),
            (ex - ENEMY_SIZE // 2, ey + ENEMY_SIZE),
            (ex + ENEMY_SIZE // 2, ey + ENEMY_SIZE)
        ]
        for lx, ly in lasers:
            if point_in_triangle((lx, ly), *triangle):
                previous_score = score
                previous_stage = stage
                score += 100
                explosions.append([ex, ey, 10])
                play_tone(440, 0.1, wave_type='saw')
                if score // SHIELD_REWARD_SCORE > previous_score // SHIELD_REWARD_SCORE:
                    lives += 1
                    play_tone(880, 0.2, volume=0.6, wave_type='sine')
                stage = max(1, score // 2000 + 1)
                if stage > previous_stage:
                    play_tone(660, 0.2, wave_type='square')
                hit = True
                break
        if not hit:
            remaining.append([ex, ey])
    enemies = remaining


def get_score():
    """
    Get the current score of the game.
    :return:
    """
    return score


def get_lives():
    """
    Get the current number of lives remaining.
    :return:
    """
    return lives


def get_stage():
    """
    Get the current stage of the game.
    :return:
    """
    return stage


def is_game_over():
    """
    Check if the game is over based on the number of lives remaining.
    :return:
    """
    global lives
    if lives < 0:
        lives = 0
    return lives <= 0


def reset_enemies():
    """
    Reset the game state, including enemies, explosions, lives, score, stage, and boss status.
    :return:
    """
    global enemies, explosions, lives, score, spawn_timer, stage, boss_active, boss_triggered_stage
    enemies = []
    explosions = []
    lives = 3
    score = 0
    stage = 1
    boss_active = False
    boss_triggered_stage = None
    spawn_timer = pygame.time.get_ticks()
