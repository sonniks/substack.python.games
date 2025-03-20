import pygame

pygame.init()
screen = pygame.display.set_mode((320, 200))  # CGA resolution
palette = [(0, 0, 0), (255, 0, 0), (0, 255, 255), (255, 255, 255)]  # Classic CGA palette

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill(palette[1])  # Fill with red
    pygame.display.flip()

pygame.quit()
