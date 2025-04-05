import pygame
import sys
from dice_module import Die, roll_dice, reset_dice, init_dice_audio, draw_roll_indicator, can_score
from scorecard import draw_scorecard, handle_score_click, total_score, init_scorecard


pygame.init()
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 650
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Five Dice")
FONT = pygame.font.SysFont(None, 36)


# Create five dice spaced evenly
dice_list = []
die_spacing = 100
start_x = 50
for i in range(5):
    die = Die(start_x + i * die_spacing, 100)
    dice_list.append(die)


def draw():
    """
    Draw the game state.
    :return:
    """
    screen.fill((220, 220, 220))
    for die in dice_list:
        die.draw(screen)
    draw_scorecard(screen, 50, 250)
    draw_roll_indicator(screen)
    total = total_score()
    score_text = FONT.render(f"Total Score: {total}", True, (0, 0, 0))
    screen.blit(score_text, (50, 570))  # You can tweak Y if needed
    roll_text = FONT.render("Press SPACE to roll", True, (0, 0, 0))
    quit_text = FONT.render("Press Q to quit", True, (0, 0, 0))
    screen.blit(roll_text, (20, 20))
    screen.blit(quit_text, (20, 60))
    pygame.display.flip()


def main():
    """
    Main game loop.
    :return:
    """
    init_dice_audio()
    init_scorecard()
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if can_score():  # Only allow hold-clicks after roll 1
                    for die in dice_list:
                        if die.rect.collidepoint(event.pos):
                            die.toggle_hold()
                dice_values = [die.value for die in dice_list]
                if can_score() and handle_score_click(event.pos, dice_values):
                    reset_dice(dice_list)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    roll_dice(dice_list, screen)
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        draw()
        clock.tick(30)


if __name__ == '__main__':
    main()
