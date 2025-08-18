# movement.py

from loader import TILE_SIZE
from logger import conlog


FUDGE = 0 # No Longer Used?


def get_tile_position(entity):
    """
    Get the tile position of an entity based on its coordinates.
    :param entity:
    :return:
    """
    cx = round(entity.x / TILE_SIZE)
    cy = int(entity.y // TILE_SIZE)
    cy = round(entity.y / TILE_SIZE)
    return cx, cy


def get_target_tile(entity, dx, dy):
    """
    Calculate the target tile position based on the entity's current position and movement direction.
    :param entity:
    :param dx:
    :param dy:
    :return:
    """
    new_x = entity.x + dx * entity.MOVE_SPEED
    new_y = entity.y + dy * entity.MOVE_SPEED
    cx, cy = get_tile_position(entity)
    tx = round(new_x / TILE_SIZE)
    ty = int(new_y // TILE_SIZE)
    return new_x, new_y, tx, ty, cx, cy


def try_move(entity, dx, dy, map_data):
    """
    Attempt to move the entity in the specified direction, checking for obstacles and boundaries.
    :param entity:
    :param dx:
    :param dy:
    :param map_data:
    :return:
    """
    force_up = 1  # pixels to nudge upward if standing in a floor
    tiles = get_surrounding_tiles(entity, map_data)
    if tiles['center'] == 'F':
        conlog(f"[{entity.name}] Standing on floor, nudging up by {force_up} pixels")
        entity.y -= force_up
        return True
    if dx == 0 and dy == 0:
        return False
    new_x, new_y, tx, ty, cx, cy = get_target_tile(entity, dx, dy)
    if new_x < 0:
        # conlog(f"[{entity.name}] Aborting move: new_x < 0")
        return False
    if new_x > 768:
        # conlog(f"[{entity.name}] Aborting move: new_x > 768")
        return False
    # Prevent vertical movement unless horizontally aligned with tile edge
    if dy != 0:
        remainder = entity.x % TILE_SIZE
        distance_to_edge = min(remainder, TILE_SIZE - remainder)
        if distance_to_edge > 3:
            # conlog(f"[{type(entity).__name__}] Blocked: not aligned for vertical move (x={entity.x:.2f})")
            return False
    if not in_bounds(tx, ty, map_data):
        return False
    if blocks_lateral(entity, dx, map_data, tx, ty, cx, cy):
        return False
    if blocks_downward(entity, dx, map_data):
        return False
    if blocks_upward(entity, dy, map_data, tx, ty):
        return False
    entity.x = new_x
    entity.y = new_y
    return True


def in_bounds(tx, ty, map_data):
    """
    Check if the target tile coordinates are within the bounds of the map data.
    :param tx:
    :param ty:
    :param map_data:
    :return:
    """
    return 0 <= ty < len(map_data) and 0 <= tx < len(map_data[0])


def blocks_lateral(caller, dx, map_data, tx, ty, cx, cy):
    """
    Check if the movement in the specified direction is blocked by a wall or obstacle.
    :param caller:
    :param dx:
    :param map_data:
    :param tx:
    :param ty:
    :param cx:
    :param cy:
    :return:
    """
    upleft, upcen, upright, left, center, right, loleft, locen, loright = (
        get_surrounding_tiles(caller, map_data).values())
    if dx == 0:
        return False
    if center in ['L']:
        return True
    if caller.name == "Player" and entity_is_tile_aligned_horizontally(caller):
        if loleft not in ['F', 'T'] and dx == -1:
            return True
        if loright not in ['F', 'T'] and dx == 1:
            return True
    #if map_data[ty][tx] == 'B':
    #    conlog(f"[{type(caller).__name__}] Blocked: target is B")
    #    return True
    # allow player clipping for debug
    if entity_is_tile_aligned_horizontally(caller):
        if caller.name != "Player":
            if dx == -1 and left in ['B']:
                conlog(f"[{caller.name}] Blocked: target left is B")
                return True
            if dx == 1 and right in ['B']:
                conlog(f"[{caller.name}] Blocked: target right is B")
                return True
    if center in ['T']:
        return True
    if center in ['U', 'D', 'E'] and (loleft == 'F' or loright == 'F'):
        pass
    below_ty = ty + 1
    if not (0 <= below_ty < len(map_data)):
        return True
    return False


def blocks_downward(entity, dy, map_data):
    """
    Check if the downward movement is blocked by a wall or obstacle.
    :param entity:
    :param dy:
    :param map_data:
    :return:
    """
    if dy <= 0:
        return False
    tiles = get_surrounding_tiles(entity, map_data)
    return tiles['center'] not in ['D', 'E'] and tiles['locen'] not in ['L', 'E', 'U', 'F']


def blocks_upward(caller, dy, map_data, tx, ty):
    """
    Check if the upward movement is blocked by a wall or obstacle.
    :param caller:
    :param dy:
    :param map_data:
    :param tx:
    :param ty:
    :return:
    """
    if dy >= 0:
        return False
    if not (0 <= ty < len(map_data)):
        return True
    cell = map_data[ty][tx]
    # conlog(f"[{type(caller).__name__}] blocks_upward check: climbing into '{cell}' at ({tx},{ty})")
    return cell not in ['L', 'D', 'E', 'U', 'T']

def on_ladder(entity, map_data):
    """
    Check if the entity is currently on a ladder or vine.
    :param entity:
    :param map_data:
    :return:
    """
    cx = int(entity.x // TILE_SIZE)
    cy = int(entity.y // TILE_SIZE)
    return map_data[cy][cx] in ['L', 'U', 'D', 'E']


def valid_floor_below(entity, map_data):
    """
    Check if there is a valid floor below the entity.
    :param entity:
    :param map_data:
    :return:
    """
    # log_surrounding_tiles(entity, map_data)
    tiles = get_surrounding_tiles(entity, map_data)
    return tiles['loleft'] == 'F' or tiles['loright'] == 'F'


def can_climb(direction, map_data, cx, cy):
    """
    Check if the entity can climb in the specified direction.
    :param direction:
    :param map_data:
    :param cx:
    :param cy:
    :return:
    """
    target_y = cy + direction
    if not (0 <= target_y < len(map_data)):
        return False
    return map_data[target_y][cx] in ['L', 'D', 'U', 'T']


def log_surrounding_tiles(entity, map_data):
    """
    Log the surrounding tiles of the entity for debugging purposes.
    :param entity:
    :param map_data:
    :return:
    """
    tiles = get_surrounding_tiles(entity, map_data)
    cx, cy = get_tile_position(entity)
    conlog(f"{entity.name} [TILES] ↖{tiles['upleft']} ↑{tiles['upcen']} ↗{tiles['upright']}")
    conlog(f"{entity.name} [TILES] ←{tiles['left']} -{tiles['center']} →{tiles['right']}")
    conlog(f"{entity.name} [TILES] ↙{tiles['loleft']} ↓{tiles['locen']} ↘{tiles['loright']}")
    conlog(f"{entity.name} POS=({entity.x:.1f},{entity.y:.1f}) TILE=({cx},{cy})")


def get_surrounding_tiles(entity, map_data):
    """
    Get the surrounding tiles of the entity based on its current position.
    :param entity:
    :param map_data:
    :return:
    """
    cx, cy = get_tile_position(entity)
    def safe_get(x, y):
        if 0 <= y < len(map_data) and 0 <= x < len(map_data[0]):
            return map_data[y][x]
        return '~'  # out-of-bounds marker
    return {
        'upleft':  safe_get(cx - 1, cy - 1),
        'upcen':   safe_get(cx,     cy - 1),
        'upright': safe_get(cx + 1, cy - 1),
        'left':    safe_get(cx - 1, cy),
        'center':  safe_get(cx,     cy),
        'right':   safe_get(cx + 1, cy),
        'loleft':  safe_get(cx - 1, cy + 1),
        'locen':  safe_get(cx,     cy + 1),
        'loright':safe_get(cx + 1, cy + 1)
    }


def maybe_snap_to_floor(entity, map_data):
    """
    Snap the entity to the floor if it is not already aligned.
    :param entity:
    :param map_data:
    :return:
    """
    if entity.timer % 120 != 0:
        return
    cx, cy = get_tile_position(entity)
    tiles = get_surrounding_tiles(entity, map_data)
    if tiles['center'] == ' ' and tiles['locen'] == 'F':
        snap_x = cx * TILE_SIZE
        snap_y = cy * TILE_SIZE
        if int(entity.x) != snap_x or int(entity.y) != snap_y:
            # conlog(f"[{entity.name}] Snapping to floor at ({cx},{cy})")
            # entity.x = snap_x
            entity.y = snap_y

def entity_is_tile_aligned_horizontally(entity):
    """
    Check if the entity is horizontally aligned with a tile edge.
    :param entity:
    :return:
    """
    remainder = entity.x % TILE_SIZE
    return remainder <= 3 or remainder >= (TILE_SIZE - 3)

