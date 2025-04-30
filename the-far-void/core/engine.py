# core/engine.py
import pygame
from render.draw import draw_frame, draw_game_over
from objects.entities import update_entities
from objects.enemy import is_game_over, spawn_boss


spawn_boss_enabled = False


def run_game():
    """
    Main function to run the game loop.
    :return:
    """
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("The Far Void")
    clock = pygame.time.Clock()
    state = "playing"
    fire_laser_now = False
    while True:
        fire_laser_now = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return "quit"
                if state == "game_over" and event.key == pygame.K_RETURN:
                    from objects.enemy import reset_enemies
                    reset_enemies()
                    return "restart"
                if state == "playing" and event.key == pygame.K_SPACE:
                    fire_laser_now = True
                if state == "playing" and event.key == pygame.K_b:
                    if spawn_boss_enabled:
                        spawn_boss()
        if state == "playing":
            update_entities(fire_laser_now)
            draw_frame(screen)
            if is_game_over():
                state = "game_over"
                continue
        elif state == "game_over":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return "quit"
                    elif event.key == pygame.K_RETURN:
                        from objects.enemy import reset_enemies
                        reset_enemies()
                        return "restart"
            draw_game_over(screen)
        pygame.display.flip()
        clock.tick(60)