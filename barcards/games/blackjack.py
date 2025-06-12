# games/blackjack.py

import pygame
import random
from svg_parser import get_card
from hud import HUD
from soundfx import play_card_sound
from soundfx import play_card_sound


FONT_PATH = "assets/fonts/8-bit-pusab.ttf"
FONT_SIZE = 12
WHITE = (255, 255, 255)
GREEN = (0, 180, 0)
BLUE = (0, 0, 200)


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

def hand_value(hand):
    """
    Calculates the total value of a blackjack hand.
    :param hand:
    :return:
    """
    value = sum(card.value for card in hand)
    aces = sum(1 for card in hand if card.rank == "A")
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value


def draw_hand(surface, hand, x, y, label, hide_first=False):
    """
    Draws a blackjack hand on the given surface at the specified position.
    :param surface:
    :param hand:
    :param x:
    :param y:
    :param label:
    :param hide_first:
    :return:
    """
    display_value = hand_value(hand) if not hide_first else "?"
    draw_text(surface, f"{label} ({display_value})", x, y - 20)
    spacing = 110
    if hide_first and len(hand) >= 2:
        scaled = pygame.transform.smoothscale(hand[1].image, (100, 150))
        surface.blit(scaled, (x, y))
        back = pygame.Surface((100, 150))
        back.fill((30, 30, 30))
        pygame.draw.rect(back, (200, 0, 0), back.get_rect(), 4)
        surface.blit(back, (x + spacing, y))
    else:
        for i, card in enumerate(hand):
            scaled = pygame.transform.smoothscale(card.image, (100, 150))
            surface.blit(scaled, (x + i * spacing, y))


def get_bet(SCREEN, hud):
    """
    Prompts the user to enter a bet amount and validates it against the current bankroll.
    :param SCREEN:
    :param hud:
    :return:
    """
    clock = pygame.time.Clock()
    bet = 0
    active = True
    input_text = ""
    while active:
        SCREEN.fill(BLUE)
        draw_text(SCREEN, f"Bankroll: ${hud.get_bankroll()}", 20, 20)
        draw_text(SCREEN, "Enter your bet:", 20, 60)
        draw_text(SCREEN, input_text, 200, 60)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                #pygame.quit()
                #exit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    try:
                        bet = int(input_text)
                        if 1 <= bet <= hud.get_bankroll():
                            active = False
                    except:
                        input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.unicode.isdigit():
                    input_text += event.unicode
        clock.tick(30)
    return bet


def deal_card():
    """
    Deals a random card from a standard deck of playing cards.
    :return:
    """
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    return get_card(random.choice(ranks), random.choice(suits))


def check_for_initial_blackjack(player_hand, dealer_hand, bet, hud, SCREEN):
    """
    Checks if either player or dealer has an initial blackjack (21 with two cards).
    :param player_hand:
    :param dealer_hand:
    :param bet:
    :param hud:
    :param SCREEN:
    :return:
    """
    clock = pygame.time.Clock()
    if hand_value(player_hand) == 21:
        SCREEN.fill(BLUE)
        hud.draw(SCREEN)
        draw_hand(SCREEN, dealer_hand, 50, 120, "Dealer")
        draw_hand(SCREEN, player_hand, 50, 650, "Your Hand")
        draw_text(SCREEN, "Dealer stands on 17. Blackjack pays 3:2", 50, 280)
        if hand_value(dealer_hand) == 21:
            result = "Push. Both have Blackjack."
            hud.set_bankroll(hud.get_bankroll() + bet)
        else:
            payout = int(bet * 2.5)
            result = f"Blackjack! You win! (+${int(bet * 1.5)})"
            hud.set_bankroll(hud.get_bankroll() + payout)
        hud.clear_wager()
        draw_text(SCREEN, result, 50, 500, GREEN)
        draw_text(SCREEN, "Press SPACE to play again or Q to quit", 50, 530)
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    #pygame.quit()
                    #exit()
                    return True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return False  # continue to next hand
                    elif event.key == pygame.K_q:
                        return True  # quit game
        return False
    return None  # no blackjack, continue normal play


def mainloop(SCREEN, hud):
    """
    Main loop for the Blackjack game.
    :param SCREEN:
    :param hud:
    :return:
    """
    clock = pygame.time.Clock()
    running = True
    while running:
        player_hand = [deal_card(), deal_card()]
        dealer_hand = [deal_card(), deal_card()]
        bet = get_bet(SCREEN, hud)
        hud.set_wager(bet)
        hud.set_bankroll(hud.get_bankroll() - bet)
        resolved = check_for_initial_blackjack(player_hand, dealer_hand, bet, hud, SCREEN)
        if resolved is True:
            return
        elif resolved is False:
            continue
        player_turn = True
        player_busted = False
        while player_turn:
            SCREEN.fill(BLUE)
            hud.draw(SCREEN)
            draw_hand(SCREEN, dealer_hand, 50, 120, "Dealer", hide_first=True)
            draw_text(SCREEN, "Dealer stands on 17. Blackjack pays 3:2", 50, 280)
            draw_hand(SCREEN, player_hand, 50, 650, "Your Hand")
            draw_text(SCREEN, "Press H to Hit, S to Stand, Q to Quit", 50, 600)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    #pygame.quit()
                    #exit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        #pygame.quit()
                        #exit()
                        return
                    elif event.key == pygame.K_h:
                        player_hand.append(deal_card())
                        play_card_sound()
                        if hand_value(player_hand) > 21:
                            player_busted = True
                            player_turn = False
                    elif event.key == pygame.K_s:
                        player_turn = False
            clock.tick(30)
        dealer_busted = False
        if not player_busted:
            while hand_value(dealer_hand) < 17:
                dealer_hand.append(deal_card())
                play_card_sound()
                pygame.time.delay(300)
            if hand_value(dealer_hand) > 21:
                dealer_busted = True
        SCREEN.fill(BLUE)
        hud.draw(SCREEN)
        draw_hand(SCREEN, dealer_hand, 50, 120, "Dealer")
        draw_text(SCREEN, "Dealer stands on 17. Blackjack pays 3:2", 50, 280)
        draw_hand(SCREEN, player_hand, 50, 650, "Your Hand")
        player_val = hand_value(player_hand)
        dealer_val = hand_value(dealer_hand)
        if player_busted:
            result = "You busted! You lose."
        elif dealer_busted or player_val > dealer_val:
            result = f"You win! (+${bet})"
            hud.set_bankroll(hud.get_bankroll() + (bet * 2))
        elif player_val == dealer_val:
            result = "Push."
            hud.set_bankroll(hud.get_bankroll() + bet)
        else:
            result = "Dealer wins."
        hud.clear_wager()
        hud.draw(SCREEN)
        draw_text(SCREEN, result, 50, 500, GREEN)
        draw_text(SCREEN, "Press SPACE to play again or Q to quit", 50, 530)
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    #pygame.quit()
                    #exit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                    elif event.key == pygame.K_q:
                        running = False
                        waiting = False
            clock.tick(30)