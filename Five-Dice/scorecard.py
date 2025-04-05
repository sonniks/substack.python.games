import pygame


CATEGORIES = [
    "Ones", "Twos", "Threes", "Fours", "Fives", "Sixes",
    "Three of a Kind", "Four of a Kind", "Full House",
    "Small Straight", "Large Straight", "Yahtzee", "Chance"
]
CATEGORY_SCORES = {name: None for name in CATEGORIES}
CATEGORY_RECTS = {}
CATEGORY_HEIGHT = 40
CATEGORY_WIDTH = 200
FONT = None


def init_scorecard():
    """
    Initialize the scorecard font.
    :return:
    """
    global FONT
    FONT = pygame.font.SysFont(None, 28)


def draw_scorecard(surface, x, y):
    """
    Draw the scorecard on the given surface.
    :param surface:
    :param x:
    :param y:
    :return:
    """
    left_x = x
    right_x = x + CATEGORY_WIDTH + 20
    for idx, name in enumerate(CATEGORIES):
        is_left = idx < 6
        col_x = left_x if is_left else right_x
        row_y = y + (idx if is_left else idx - 6) * CATEGORY_HEIGHT
        rect = pygame.Rect(col_x, row_y, CATEGORY_WIDTH, CATEGORY_HEIGHT)
        CATEGORY_RECTS[name] = rect
        color = (180, 255, 180) if CATEGORY_SCORES[name] is None else (200, 200, 200)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (0, 0, 0), rect, 2)
        label = f"{name}: {CATEGORY_SCORES[name] if CATEGORY_SCORES[name] is not None else ''}"
        text = FONT.render(label, True, (0, 0, 0))
        surface.blit(text, (col_x + 10, row_y + 8))


def handle_score_click(pos, dice_values):
    """
    Handle the click event for scoring.
    :param pos:
    :param dice_values:
    :return:
    """
    for name, rect in CATEGORY_RECTS.items():
        if rect.collidepoint(pos) and CATEGORY_SCORES[name] is None:
            score = calculate_score(name, dice_values)
            CATEGORY_SCORES[name] = score
            return True  # scored successfully
    return False


def calculate_score(category, dice):
    """
    Calculate the score for the given category and dice.
    :param category:
    :param dice:
    :return:
    """
    counts = [dice.count(i) for i in range(1, 7)]
    total = sum(dice)
    if category == "Ones": return counts[0] * 1
    if category == "Twos": return counts[1] * 2
    if category == "Threes": return counts[2] * 3
    if category == "Fours": return counts[3] * 4
    if category == "Fives": return counts[4] * 5
    if category == "Sixes": return counts[5] * 6
    if category == "Three of a Kind" and max(counts) >= 3:
        return total
    if category == "Four of a Kind" and max(counts) >= 4:
        return total
    if category == "Full House" and 3 in counts and 2 in counts:
        return 25
    if category == "Small Straight" and has_straight(dice, 4):
        return 30
    if category == "Large Straight" and has_straight(dice, 5):
        return 40
    if category == "Yahtzee" and max(counts) == 5:
        return 50
    if category == "Chance":
        return total
    return 0  # If the category doesn't match


def has_straight(dice, length):
    """
    Check if the dice have a straight of the given length.
    :param dice:
    :param length:
    :return:
    """
    unique = sorted(set(dice))
    for i in range(len(unique) - length + 1):
        if all(unique[i + j] - unique[i] == j for j in range(length)):
            return True
    return False


def total_score():
    """
    Returns the total score of the scorecard.
    :return:
    """
    return sum(score for score in CATEGORY_SCORES.values() if score is not None)


def reset_scorecard():
    """
    Reset the scorecard.
    :return:
    """
    for key in CATEGORY_SCORES:
        CATEGORY_SCORES[key] = None