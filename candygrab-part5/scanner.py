# scanner.py


from typing import Iterable, Tuple, Set, List, Any
from logger import conlog
from movement import get_tile_position
from constants import *

def _safe_cell(map_data: List[List[str]], cx: int, cy: int) -> str:
    """
    Safely get the character at map_data[cy][cx], returning '~' if out-of-bounds.
    :param map_data:
    :param cx:
    :param cy:
    :return:
    """
    try:
        if 0 <= cy < len(map_data) and 0 <= cx < len(map_data[0]):
            return map_data[cy][cx]
    except (IndexError, TypeError) as e:
        # IndexError: out-of-bounds
        # TypeError: bad map_data or row not subscriptable
        pass
    return '~'  # out-of-bounds marker


def _find_all_candy_tiles(map_data: List[List[str]], candy_chars: Set[str]) -> List[Tuple[int, int, str]]:
    """
    Scan the entire map_data for tiles that match any in candy_chars.
    :param map_data:
    :param candy_chars:
    :return:
    """
    hits = []
    for y, row in enumerate(map_data):
        for x, ch in enumerate(row):
            if ch in candy_chars:
                hits.append((x, y, ch))
    return hits


def _score_for_char(ch: str, tile_lookup: Any) -> int:
    """
    Given a character and a tile_lookup (from tiles.csv), return the score for that tile.
    :param ch:
    :param tile_lookup:
    :return:
    """
    if not tile_lookup or ch not in tile_lookup:
        return 0
    entry = tile_lookup[ch]
    if isinstance(entry, dict):
        try:
            return int(entry.get('score', 0))
        except Exception:
            return 0
    if isinstance(entry, (tuple, list)) and len(entry) >= 3:
        try:
            return int(entry[2])
        except Exception:
            return 0
    return 0


def scan_world(map_data: List[List[str]], player, villains: Iterable, tile_lookup,
               hud, candy_chars: Set[str] = None, candy_sound =     None) -> None:
    """
    Scan the game world for player, villains, and candy states.
    :param map_data:
    :param player:
    :param villains:
    :param tile_lookup:
    :param hud:
    :param candy_chars:
    :return:
    """
    candy_chars = candy_chars or DEFAULT_CANDY
    # Player tile and cell
    pcx, pcy = get_tile_position(player)
    pcell = _safe_cell(map_data, pcx, pcy)
    #conlog(f"[Scanner] Player tile=({pcx},{pcy}) cell='{pcell}'")
    # Villain tiles and cells
    vtiles = []
    for v in villains:
        vcx, vcy = get_tile_position(v)
        vcell = _safe_cell(map_data, vcx, vcy)
        vtiles.append((v, vcx, vcy, vcell))
        #conlog(f"[Scanner] {v.name} tile=({vcx},{vcy}) cell='{vcell}'")
    # Candy tiles (scan by map chars)
    candy_list = _find_all_candy_tiles(map_data, candy_chars)
    if candy_list:
        preview = ", ".join([f"({x},{y}) '{ch}'" for x, y, ch in candy_list[:6]])
        more = "" if len(candy_list) <= 6 else f" (+{len(candy_list)-6} more)"
        #conlog(f"[Scanner] Candy tiles: {preview}{more}")
    else:
        conlog("[Scanner] Candy tiles: none found")
        # This may be where to trigger stage progression in future
    # Checks for impact/attackable
    for v, vcx, vcy, vcell in vtiles:
        if vcx == pcx and vcy == pcy:
            if vcell not in NON_ELIGIBLE and pcell not in NON_ELIGIBLE:
                # conlog(f"[Scanner] IMPACT: {v.name} and Player share tile ({pcx},{pcy}) on '{vcell}'")
                pass
        dx_tiles = abs(vcx - pcx)
        if vcy == pcy and dx_tiles <= 3 and dx_tiles != 0:
            if vcell not in NON_ELIGIBLE and pcell not in NON_ELIGIBLE:
                # conlog(f"[Scanner] ATTACKABLE: {v.name} within {dx_tiles} tiles of Player on row {pcy}")
                pass
    # Candy collection
    if pcell in candy_chars:
        gained = _score_for_char(pcell, tile_lookup)
        map_data[pcy][pcx] = ' '  # remove candy
        hud.score += gained
        conlog(f"[Scanner] Player collected '{pcell}' for +{gained}. Score={hud.score}")
        # If you have a helper to consume candy, use it
        if candy_sound:
            candy_sound.play()
        # After removal, check if any candy remains
        remaining = _find_all_candy_tiles(map_data, candy_chars)
        if not remaining:
            # Hook for future stage progression
            conlog("[Scanner] All candy collected. Stage progression trigger pending.")
