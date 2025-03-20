import pygame

# Initialize Pygame
pygame.init()

# CGA 320x200 resolution
WIDTH, HEIGHT = 320, 200
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# CGA Palette (Classic Cyan/Magenta/White)
CGA_COLORS = [(0, 0, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255)]

def draw_checkerboard():
    block_size = 20  # Size of each square in the checkerboard
    for y in range(0, HEIGHT, block_size):
        for x in range(0, WIDTH, block_size):
            color = CGA_COLORS[(x // block_size + y // block_size) % 2 + 1]  # Alternate colors
            pygame.draw.rect(screen, color, (x, y, block_size, block_size))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(CGA_COLORS[0])  # Fill with black
    draw_checkerboard()  # Draw CGA checkerboard
    pygame.display.flip()  # Update screen

pygame.quit()
