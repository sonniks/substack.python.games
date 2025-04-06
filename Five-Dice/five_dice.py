import pygame
import sys
from dice_module import Die, roll_dice, reset_dice, init_dice_audio, draw_roll_indicator, can_score
from scorecard import draw_scorecard, handle_score_click, total_score, init_scorecard, reset_scorecard, CATEGORY_SCORES


pygame.init()
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Five Dice")
FONT = pygame.font.SysFont(None, 36)


dice_list = []
die_spacing = 100
start_x = 50
for i in range(5):
    die = Die(start_x + i * die_spacing, 100)
    dice_list.append(die)


def is_game_over():
    """
    Check if the game is over.
    :return:
    """
    return all(score is not None for score in CATEGORY_SCORES.values())


def draw_game_over():
    """
    Draw the game over screen.
    :return:
    """
    screen.fill((0, 0, 0))
    final_score = total_score()
    text1 = FONT.render("Game Over! Final Score:", True, (255, 255, 255))
    text2 = FONT.render(str(final_score), True, (255, 255, 255))
    text3 = FONT.render("Press any key to restart", True, (200, 200, 200))
    screen.blit(text1, (150, 200))
    screen.blit(text2, (260, 250))
    screen.blit(text3, (120, 320))
    pygame.display.flip()

def draw():
    """
    Draw the game screen.
    :return:
    """
    screen.fill((220, 220, 220))
    for die in dice_list:
        die.draw(screen)
    draw_scorecard(screen, 50, 250)
    draw_roll_indicator(screen)
    total = total_score()
    score_text = FONT.render(f"Total Score: {total}", True, (0, 0, 0))
    screen.blit(score_text, (50, 540))
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
    game_over = False
    while True:
        if game_over:
            draw_game_over()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    reset_scorecard()
                    reset_dice(dice_list)
                    game_over = False
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if can_score():
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
            if is_game_over():
                game_over = True
            else:
                draw()
        clock.tick(30)


if __name__ == '__main__':
    main()
