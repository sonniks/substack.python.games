import pygame
import random

# Initialize Pygame
pygame.init()

# CGA 320x200 resolution (scaled for better visibility)
WIDTH, HEIGHT = 320, 200
SCALE = 3  # Scale factor (try 2, 3, or 4 for a bigger window)
screen = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE), pygame.RESIZABLE)

pygame.display.set_caption("Breakout - CGA Style")

# Create a smaller internal surface at CGA resolution
game_surface = pygame.Surface((WIDTH, HEIGHT))

# CGA Colors
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)

# Paddle
PADDLE_WIDTH = 50
PADDLE_HEIGHT = 5
paddle_x = WIDTH // 2 - PADDLE_WIDTH // 2
paddle_y = HEIGHT - 20

# Ball
BALL_SIZE = 5
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_dx = random.choice([-2, 2])  # Random left or right start
ball_dy = -2  # Always start moving up

# Bricks
BRICK_ROWS = 5
BRICK_COLS = 10
BRICK_WIDTH = WIDTH // BRICK_COLS
BRICK_HEIGHT = 10
bricks = []

for row in range(BRICK_ROWS):
    for col in range(BRICK_COLS):
        brick_x = col * BRICK_WIDTH
        brick_y = row * BRICK_HEIGHT + 20
        bricks.append(pygame.Rect(brick_x, brick_y, BRICK_WIDTH, BRICK_HEIGHT))

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    game_surface.fill(BLACK)  # Fill the internal surface

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get mouse position, scaled down to CGA resolution
    mouse_x, _ = pygame.mouse.get_pos()
    paddle_x = max(0, min((mouse_x // SCALE) - PADDLE_WIDTH // 2, WIDTH - PADDLE_WIDTH))

    # Move ball
    ball_x += ball_dx
    ball_y += ball_dy

    # Ball collision with walls
    if ball_x <= 0 or ball_x >= WIDTH - BALL_SIZE:
        ball_dx *= -1
    if ball_y <= 0:
        ball_dy *= -1

    # Ball collision with paddle
    paddle_rect = pygame.Rect(paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
    if paddle_rect.colliderect(pygame.Rect(ball_x, ball_y, BALL_SIZE, BALL_SIZE)):
        ball_dy *= -1

    # Ball collision with bricks
    for brick in bricks[:]:
        if brick.colliderect(pygame.Rect(ball_x, ball_y, BALL_SIZE, BALL_SIZE)):
            bricks.remove(brick)
            ball_dy *= -1
            break

    # Ball falls below paddle (Game Over)
    if ball_y > HEIGHT:
        ball_x, ball_y = WIDTH // 2, HEIGHT // 2
        ball_dx, ball_dy = random.choice([-2, 2]), -2

    # Draw bricks
    for brick in bricks:
        pygame.draw.rect(game_surface, CYAN if (brick.y // BRICK_HEIGHT) % 2 == 0 else MAGENTA, brick)

    # Draw paddle
    pygame.draw.rect(game_surface, WHITE, (paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))

    # Draw ball
    pygame.draw.circle(game_surface, WHITE, (ball_x, ball_y), BALL_SIZE)

    # Scale the internal surface up to fit the window
    scaled_surface = pygame.transform.scale(game_surface, (WIDTH * SCALE, HEIGHT * SCALE))
    screen.blit(scaled_surface, (0, 0))

    pygame.display.flip()
    clock.tick(60)  # 60 FPS

pygame.quit()
