
# games/poker.py

import pygame
import random
from svg_parser import get_card
from hud import HUD
from soundfx import play_card_sound


FONT_PATH = "assets/fonts/8-bit-pusab.ttf"
FONT_SIZE = 12
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 200)
CARD_WIDTH = 100
CARD_HEIGHT = 150
CARD_GAP = 20
TOP_MARGIN = 80


payout_table = [
    ("Royal Flush", 250),
    ("Straight Flush", 50),
    ("Four of a Kind", 25),
    ("Full House", 9),
    ("Flush", 6),
    ("Straight", 4),
    ("Three of a Kind", 3),
    ("Two Pair", 2),
    ("Jacks or Better", 1),
]


def get_font():
    """
    Returns a pygame font object for rendering text.
    :return:
    """
    return pygame.font.Font(FONT_PATH, FONT_SIZE)


def draw_text(surface, text, x, y, color=WHITE):
    """
    Draws text on the given surface at the specified position with the specified color.
    :param surface:
    :param text:
    :param x:
    :param y:
    :param color:
    :return:
    """
    font = get_font()
    rendered = font.render(text, True, color)
    surface.blit(rendered, (x, y))


def deal_hand():
    """
    Deals a random poker hand of 5 cards from a shuffled deck.
    :return:
    """
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    deck = [(rank, suit) for rank in ranks for suit in suits]
    random.shuffle(deck)
    return deck[:5], deck[5:]


def evaluate_hand(hand):
    """
    Evaluates the poker hand and returns the hand type and payout multiplier.
    :param hand:
    :return:
    """
    values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    ranks = [card.rank for card in hand]
    suits = [card.suit for card in hand]
    counts = {r: ranks.count(r) for r in set(ranks)}
    unique_counts = sorted(counts.values(), reverse=True)
    rank_indexes = sorted([values.index(r) for r in ranks])
    is_flush = len(set(suits)) == 1
    is_straight = rank_indexes == list(range(min(rank_indexes), min(rank_indexes)+5))
    if set(ranks) == set("TJQKA") and is_flush:
        return "Royal Flush", 250
    if is_straight and is_flush:
        return "Straight Flush", 50
    if unique_counts == [4, 1]:
        return "Four of a Kind", 25
    if unique_counts == [3, 2]:
        return "Full House", 9
    if is_flush:
        return "Flush", 6
    if is_straight:
        return "Straight", 4
    if unique_counts == [3, 1, 1]:
        return "Three of a Kind", 3
    if unique_counts == [2, 2, 1]:
        return "Two Pair", 2
    if any(r in ["J", "Q", "K", "A"] and c == 2 for r, c in counts.items()):
        return "Jacks or Better", 1
    return "No Win", 0


def mainloop(SCREEN, hud):
    """
    Main loop for the Poker game.
    :param SCREEN:
    :param hud:
    :return:
    """
    running = True
    clock = pygame.time.Clock()
    font = get_font()
    state = "bet"
    held = [False] * 5
    wager = 0
    payout_msg = ""
    deck = []
    hand = []
    redraw = []
    while running:
        SCREEN.fill(BLUE)
        hud.draw(SCREEN)
        if state == "bet":
            bet_prompt = "Enter Bet Amount (then press ENTER): "
            draw_text(SCREEN, bet_prompt + str(wager if wager >= 0 else ""), 100, 160, YELLOW)
            if wager == -1:
                draw_text(SCREEN, "Invalid bet. Try again.", 100, 190, RED)
        elif state in ("hold", "result"):
            draw_text(SCREEN,
                      "Click cards or press 1,2,3,4,5 to HOLD. Press SPACE or ENTER to DRAW.",
                      100, 800, WHITE)
            for i, card in enumerate(hand):
                card_img = pygame.transform.smoothscale(card.image, (CARD_WIDTH, CARD_HEIGHT))
                x = 100 + i * (CARD_WIDTH + CARD_GAP)
                y = 300 if held[i] else 320
                SCREEN.blit(card_img, (x, y))
                card_number = str(i + 1)
                number_text = get_font().render(card_number, True, WHITE)
                number_rect = number_text.get_rect(center=(x + CARD_WIDTH // 2, y + CARD_HEIGHT + 10))
                SCREEN.blit(number_text, number_rect)
                if held[i]:
                    draw_text(SCREEN, "HELD", x+15, y-30, YELLOW)
        if state == "result":
            draw_text(SCREEN, payout_msg, 450, 200, GREEN)
            draw_text(SCREEN, "Press SPACE to continue or Q to quit", 300, 500)
        # Draw payout table
        draw_text(SCREEN, "PAYOUTS", 950, 80, YELLOW)
        for idx, (handname, payout) in enumerate(payout_table):
            draw_text(SCREEN, f"{handname}: {payout}x", 850, 110 + idx * 25)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q and state != "bet":
                    return
                if state == "bet":
                    if pygame.K_0 <= event.key <= pygame.K_9:
                        digit = event.key - pygame.K_0
                        wager = wager * 10 + digit
                    elif event.key == pygame.K_BACKSPACE:
                        wager = wager // 10
                    elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                        if 1 <= wager <= hud.get_bankroll():
                            hud.set_wager(wager)
                            hud.set_bankroll(hud.get_bankroll() - wager)
                            card_defs, deck = deal_hand()
                            hand = [get_card(r, s) for r, s in card_defs]
                            held = [False] * 5
                            state = "hold"
                        else:
                            wager = -1  # Trigger error message
                elif state == "hold":
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                        i = event.key - pygame.K_1
                        held[i] = not held[i]
                    elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        for i in range(5):
                            if not held[i]:
                                r, s = deck.pop()
                                hand[i] = get_card(r, s)
                                play_card_sound()
                                pygame.time.delay(300)
                        result, payout = evaluate_hand(hand)
                        if payout > 0:
                            hud.set_bankroll(hud.get_bankroll() + wager + (wager * payout))
                        payout_msg = f"{result}! You won {wager * payout}" if payout else "No win. Better luck next time."
                        hud.clear_wager()
                        state = "result"
                elif state == "result" and event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    state = "bet"
            elif event.type == pygame.MOUSEBUTTONDOWN and state == "hold":
                mx, my = pygame.mouse.get_pos()
                for i in range(5):
                    x = 100 + i * (CARD_WIDTH + CARD_GAP)
                    y = 320
                    if x <= mx <= x + CARD_WIDTH and y <= my <= y + CARD_HEIGHT + 20:
                        held[i] = not held[i]
        pygame.display.flip()
        clock.tick(30)
