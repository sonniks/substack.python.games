import pygame
import sys
import random

# --- CONFIG ---
CELL_SIZE = 40
PADDING = 2
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 120, 255)

# --- INITIAL SETUP ---
pygame.init()
font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()


def draw_text(surface, text, size, x, y, color=WHITE):
    """
    Draws text on the given surface.
    :param surface:
    :param text:
    :param size:
    :param x:
    :param y:
    :param color:
    :return:
    """
    font_obj = pygame.font.SysFont(None, size)
    text_surface = font_obj.render(text, True, color)
    surface.blit(text_surface, (x, y))


def get_neighbors(x, y, grid):
    """
    Get the valid neighbors of a cell in the grid.
    :param x:
    :param y:
    :param grid:
    :return:
    """
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    result = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and grid[nx][ny] in ['1', 'S', 'F']:
            result.append((nx, ny))
    return result


def count_playable(grid):
    """
    Counts playable cells in the grid.
    :param grid:
    :return:
    """
    return sum(row.count('1') + row.count('S') + row.count('F') for row in grid)


def reachable_count(grid, start):
    """
    Count reachable cells from the start position using BFS.
    :param grid:
    :param start:
    :return:
    """
    visited = set()
    queue = [start]
    while queue:
        x, y = queue.pop(0)
        if (x, y) in visited:
            continue
        visited.add((x, y))
        for nx, ny in get_neighbors(x, y, grid):
            if (nx, ny) not in visited:
                queue.append((nx, ny))
    return len(visited)


def generate_solvable_grid(rows, cols, level=0, max_attempts=20):
    """
    Generate a solvable grid with a path from start to finish.
    :param rows:
    :param cols:
    :param level:
    :param max_attempts:
    :return:
    """
    def neighbors(x, y, visited):
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        result = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                result.append((nx, ny))
        random.shuffle(result)
        return result
    for _ in range(max_attempts):
        grid = [['0' for _ in range(cols)] for _ in range(rows)]
        start_x = random.randint(0, rows - 1)
        start_y = random.randint(0, cols - 1)
        target_path_len = int(rows * cols * 0.4) + level
        stack = [((start_x, start_y), [(start_x, start_y)], set([(start_x, start_y)]))]
        while stack:
            (x, y), path, visited = stack.pop()
            if len(path) >= target_path_len:
                for px, py in path:
                    grid[px][py] = '1'
                grid[path[0][0]][path[0][1]] = 'S'
                grid[path[-1][0]][path[-1][1]] = 'F'
                return grid, path
            for nx, ny in neighbors(x, y, visited):
                new_path = path + [(nx, ny)]
                new_visited = visited | {(nx, ny)}
                stack.append(((nx, ny), new_path, new_visited))
    return None, []


def base_grid_size(diff):
    """
    Get the base grid size based on difficulty.
    :param diff:
    :return:
    """
    return 3 + diff, 3 + diff  # Easy=4x4, Medium=5x5, Hard=6x6


def main():
    """
    Main function to run the game.
    :return:
    """
    difficulty = 0
    selecting = True
    screen = pygame.display.set_mode((600, 400))
    show_solution = False
    while selecting:
        screen.fill(BLACK)
        draw_text(screen, "Select Difficulty (1 = Easy, 3 = Hard):", 36, 50, 100)
        draw_text(screen, "Right-click to reset any board.", 28, 50, 160)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    difficulty = int(event.unicode)
                    selecting = False
                elif event.key == pygame.K_TAB:
                    show_solution = not show_solution
    level = 0
    while True:
        rows, cols = base_grid_size(difficulty)
        rows += level
        cols += level
        screen.fill(BLACK)
        draw_text(screen, "Generating board...", 32, 40, 40)
        pygame.display.flip()
        grid = None
        solution_path = []
        for attempt in range(5000):
            if attempt % 100 == 0:
                screen.fill(BLACK)
                draw_text(screen, "Generating board...", 32, 40, 40)
                draw_text(screen, f"Attempt {attempt}/5000", 28, 40, 80)
                pygame.display.flip()
            grid, solution_path = generate_solvable_grid(rows, cols, level=level, max_attempts=20)
            if grid is not None:
                break
        else:
            print("Skipping unsolvable level...")
            level += 1
            continue
        width = cols * CELL_SIZE
        height = rows * CELL_SIZE
        screen = pygame.display.set_mode((width, height))
        path = []
        mouse_down = False
        completed = False
        win_displayed = False
        win_timer = 0
        while True:
            screen.fill(BLACK)
            for i in range(rows):
                for j in range(cols):
                    color = GRAY if grid[i][j] == '0' else WHITE
                    if grid[i][j] == 'S':
                        color = GREEN
                    elif grid[i][j] == 'F':
                        color = RED
                    rect = pygame.Rect(j * CELL_SIZE + PADDING, i * CELL_SIZE + PADDING,
                                       CELL_SIZE - PADDING * 2, CELL_SIZE - PADDING * 2)
                    pygame.draw.rect(screen, color, rect)
            # Draw the player's current path
            if len(path) > 1:
                for i in range(len(path) - 1):
                    x1, y1 = path[i][1] * CELL_SIZE + CELL_SIZE // 2, path[i][0] * CELL_SIZE + CELL_SIZE // 2
                    x2, y2 = path[i + 1][1] * CELL_SIZE + CELL_SIZE // 2, path[i + 1][0] * CELL_SIZE + CELL_SIZE // 2
                    pygame.draw.line(screen, BLUE, (x1, y1), (x2, y2), 6)
            # 🔍 Solution overlay if TAB is toggled
            if show_solution and len(solution_path) > 1:
                for i in range(len(solution_path) - 1):
                    x1, y1 = solution_path[i][1] * CELL_SIZE + CELL_SIZE // 2, solution_path[i][0] * CELL_SIZE + CELL_SIZE // 2
                    x2, y2 = solution_path[i + 1][1] * CELL_SIZE + CELL_SIZE // 2, solution_path[i + 1][0] * CELL_SIZE + CELL_SIZE // 2
                    pygame.draw.line(screen, (100, 255, 100), (x1, y1), (x2, y2), 3)
            if win_displayed:
                wintext = "You Win!"
                draw_text(screen, wintext, 48, width // 2 - 80, height // 2 - 30, BLACK)
                draw_text(screen, wintext, 48, width // 2 - 82, height // 2 - 32, BLUE)
                win_timer += 1
                if win_timer > 90:  # ~1.5 seconds
                    level += 1
                    break
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_down = True
                    elif event.button == 3:
                        path = []  # Right click to reset
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        mouse_down = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        show_solution = not show_solution
            if mouse_down and not completed:
                mx, my = pygame.mouse.get_pos()
                gx, gy = my // CELL_SIZE, mx // CELL_SIZE
                if 0 <= gx < rows and 0 <= gy < cols:
                    if grid[gx][gy] in ['1', 'S', 'F'] and (gx, gy) not in path:
                        if not path or (gx, gy) in get_neighbors(*path[-1], grid):
                            path.append((gx, gy))
                            if grid[gx][gy] == 'F' and len(path) == count_playable(grid):
                                completed = True
                                win_displayed = True
            clock.tick(60)




if __name__ == '__main__':
    main()
