import pygame
import sys
import math

# Initialize
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Wireframe with CRT Effect")
clock = pygame.time.Clock()

# Cube 3D points
points = [
    [-1, -1, -1], [1, -1, -1],
    [1, 1, -1], [-1, 1, -1],
    [-1, -1, 1], [1, -1, 1],
    [1, 1, 1], [-1, 1, 1]
]

# Edges between points
edges = [
    (0,1), (1,2), (2,3), (3,0),
    (4,5), (5,6), (6,7), (7,4),
    (0,4), (1,5), (2,6), (3,7)
]

def project(x, y, z):
    """Simple perspective projection."""
    factor = 400 / (z + 5)
    x = x * factor + 400
    y = y * factor + 300
    return int(x), int(y)

angle = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Rotate cube
    rotated_points = []
    for p in points:
        x, y, z = p
        # Rotate around Y axis
        temp_x = x * math.cos(angle) - z * math.sin(angle)
        temp_z = x * math.sin(angle) + z * math.cos(angle)
        x, z = temp_x, temp_z
        # Rotate around X axis
        temp_y = y * math.cos(angle/2) - z * math.sin(angle/2)
        temp_z = y * math.sin(angle/2) + z * math.cos(angle/2)
        y, z = temp_y, temp_z
        rotated_points.append(project(x, y, z))

    screen.fill((0, 0, 0))

    # Draw scanlines (CRT effect)
    for i in range(0, 600, 4):
        pygame.draw.line(screen, (10, 10, 10), (0, i), (800, i))

    # Draw cube edges
    for edge in edges:
        pygame.draw.aaline(screen, (0, 255, 0), rotated_points[edge[0]], rotated_points[edge[1]])

    # Glow effect: draw again slightly larger and blurred (fake it)
    # Create glow layers
    glow_layers = [
        (2, (0, 255, 0, 100)),
        (4, (0, 255, 0, 60)),
        (6, (80, 255, 80, 40)),
        (8, (120, 255, 120, 30)),
        (10, (180, 255, 180, 20))
    ]

    for size, color in glow_layers:
        surface_glow = pygame.Surface((800, 600), pygame.SRCALPHA)
        for edge in edges:
            start = rotated_points[edge[0]]
            end = rotated_points[edge[1]]
            pygame.draw.line(surface_glow, color, start, end, size)
        screen.blit(surface_glow, (0, 0))

    pygame.display.flip()
    clock.tick(60)
    angle += 0.01
