#airhockey.py
import pygame
import sys
import surface
import ai_player
import physics
import scoring


# Initialize
screen = surface.init_window()
clock = pygame.time.Clock()


# Game state
running = True
game_over = False
air_resistance = 0.98  # Placeholder for air resistance setting
score = [0, 0]  # [AI, Player]

# Play to Score
play_to_score = 5  # Placeholder for score limit, can be set to any value


# Placeholder puck and paddles
puck = pygame.Rect(surface.FIELD_WIDTH // 2 - 10, surface.FIELD_HEIGHT // 2 - 10, 20, 20)
player = pygame.Rect(surface.FIELD_WIDTH // 2 - 20, surface.FIELD_HEIGHT - 60, 40, 40)
ai = pygame.Rect(surface.FIELD_WIDTH // 2 - 20, 20, 40, 40)


# Slam shot flag
slam_shot = False


# Game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_r:
                puck.center = (surface.FIELD_WIDTH // 2, surface.FIELD_HEIGHT // 2)
                score = [0, 0]
                game_over = False
            elif event.key == pygame.K_j:
                puck.move_ip(0, -10 if puck.centery > surface.CENTER_LINE else 10)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                slam_shot = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                slam_shot = False
    if not game_over:
        # Move player paddle
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Limit player movement to bottom half only
        player.centerx = max(0, min(mouse_x, surface.FIELD_WIDTH))
        player.centery = max(surface.CENTER_LINE + 20, min(mouse_y, surface.FIELD_HEIGHT - 20))
        # Move AI
        ai_player.move_ai(ai, puck)
        # Update puck
        physics.update_puck(puck, player, ai, slam_shot, air_resistance)
        # Check scoring
        scorer = scoring.check_goals(puck, score)
        if scorer:
            scoring.reset_puck(puck, scorer)
        if score[0] + score[1] >= play_to_score:
            game_over = True
    # Draw everything
    surface.draw_surface(screen)
    pygame.draw.ellipse(screen, (0, 0, 0), puck)
    pygame.draw.ellipse(screen, (0, 0, 255), player)
    pygame.draw.ellipse(screen, (255, 0, 0), ai)
    scoring.draw_score(screen, score, game_over)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
sys.exit()