# svg_parser.py

import io
from dataclasses import dataclass
from typing import List, Optional
import pygame
import cairosvg


# Constants
CARD_WIDTH = 359
CARD_HEIGHT = 539
COLUMNS = 13
ROWS = 4

RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
POKER_RANK_ORDER = {
    "2": 2, "3": 3, "4": 4, "5": 5,
    "6": 6, "7": 7, "8": 8, "9": 9,
    "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14
}


@dataclass
class Card:
    """
    Represents a playing card with its attributes and image.
    """
    rank: str               # "2", "3", ..., "10", "J", "Q", "K", "A"
    suit: str               # "Hearts", "Diamonds", etc.
    value: int              # Blackjack value (2–10, A=11, face=10)
    poker_rank: int         # Poker rank (2–14)
    image: pygame.Surface


# --- Module cache ---
_cached_surface: Optional[pygame.Surface] = None
_cached_deck: Optional[List[Card]] = None


def _svg_to_surface(svg_path: str) -> pygame.Surface:
    """
    Converts an SVG file to a Pygame surface.
    :param svg_path:
    :return:
    """
    with open(svg_path, "rb") as svg_file:
        svg_data = svg_file.read()
    png_bytes = cairosvg.svg2png(bytestring=svg_data)
    return pygame.image.load(io.BytesIO(png_bytes)).convert_alpha()


def _calculate_value(rank: str) -> int:
    """
    Calculates the Blackjack value of a card based on its rank.
    :param rank:
    :return:
    """
    if rank in ["J", "Q", "K"]:
        return 10
    if rank == "A":
        return 11
    return int(rank)


def load_deck(svg_path: str) -> List[Card]:
    """
    Loads a full deck of cards from an SVG file and returns a list of Card objects.
    :param svg_path:
    :return:
    """
    global _cached_surface, _cached_deck
    if _cached_deck is not None:
        return _cached_deck
    if _cached_surface is None:
        _cached_surface = _svg_to_surface(svg_path)
    full_width = _cached_surface.get_width()
    full_height = _cached_surface.get_height()
    # Proportional layout based on reference raster
    border_w_pct = 8 / 1204 # Debugging tests
    card_w_pct = 84 / 1204 # Debugging tests
    border_h_pct = 8 / 544 # Debugging tests
    card_h_pct = 126 / 544 # Debugging tests
    border_w = full_width * border_w_pct
    card_w = full_width * card_w_pct
    border_h = full_height * border_h_pct
    card_h = full_height * card_h_pct
    deck = []
    for row, suit in enumerate(SUITS):
        for col, rank in enumerate(RANKS):
            x = round(border_w + col * (card_w + border_w))
            y = round(border_h + row * (card_h + border_h))
            w = round(card_w)
            h = round(card_h)
            card_image = _cached_surface.subsurface(pygame.Rect(x, y, w, h)).copy()
            poker_rank = POKER_RANK_ORDER[rank]
            value = _calculate_value(rank)
            deck.append(Card(rank=rank, suit=suit, value=value, poker_rank=poker_rank, image=card_image))
    _cached_deck = deck
    return deck


def get_card(rank: str, suit: str) -> Card:
    """
    Retrieves a specific card from the cached deck by its rank and suit.
    :param rank:
    :param suit:
    :return:
    """
    if _cached_deck is None:
        raise RuntimeError("Deck not loaded. Call load_deck(svg_path) first.")
    for card in _cached_deck:
        if card.rank == rank and card.suit == suit:
            return card
    raise ValueError(f"Card {rank} of {suit} not found.")
