# player.py

import pygame
from loader import TILE_SIZE

MOVE_SPEED = 2  # or try 4 if it's too slow

class Player:
    """
    Represents the player character in the game.
    """
    def __init__(self, map_data):
        self.sprites = self.load_player_sprites()
        self.frame = 0
        self.timer = 0
        self.x, self.y = self.find_spawn(map_data)


    def load_player_sprites(self):
        """
        Load player sprites from the spritesheet.
        :return:
        """
        sheet = pygame.image.load("assets/sprites/sheet.png").convert_alpha()
        return [sheet.subsurface(pygame.Rect(i * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)) for i in range(4)]


    def find_spawn(self, map_data):
        """
        Find the player's spawn position in the map data.
        :param map_data:
        :return:
        """
        for y, row in enumerate(map_data):
            for x, char in enumerate(row):
                if char == 'P':
                    return x * TILE_SIZE, y * TILE_SIZE
        return 0, 0


    def update(self, dx, dy, map_data):
        """
        Update the player's position based on input and map data.
        :param dx:
        :param dy:
        :param map_data:
        :return:
        """
        self.timer += 1
        if self.timer % 10 == 0:
            self.frame = (self.frame + 1) % len(self.sprites)
        self.try_move(dx, dy, map_data)


    def try_move(self, dx, dy, map_data):
        """
        Attempt to move the player in the specified direction.
        :param dx:
        :param dy:
        :param map_data:
        :return:
        """
        if dx == 0 and dy == 0:
            return
        new_x = self.x + dx * MOVE_SPEED
        new_y = self.y + dy * MOVE_SPEED
        cx = self.x // TILE_SIZE
        cy = self.y // TILE_SIZE
        tx = (new_x + TILE_SIZE - 1) // TILE_SIZE if dx > 0 else new_x // TILE_SIZE if dx < 0 else cx
        ty = (new_y + TILE_SIZE - 1) // TILE_SIZE if dy > 0 else new_y // TILE_SIZE if dy < 0 else cy
        if not self.in_bounds(tx, ty, map_data):
            return
        if self.blocks_lateral(dx, map_data, tx, ty, cx, cy):
            return
        if self.blocks_downward(dy, map_data, cx, cy):
            return
        if self.blocks_upward(dy, map_data, tx, ty):
            return
        self.x = new_x
        self.y = new_y


    def in_bounds(self, tx, ty, map_data):
        """
        Check if the new tile coordinates are within the bounds of the map data.
        :param tx:
        :param ty:
        :param map_data:
        :return:
        """
        return 0 <= ty < len(map_data) and 0 <= tx < len(map_data[0])


    def blocks_lateral(self, dx, map_data, tx, ty, cx, cy):
        """
        Check if the movement in the x direction is blocked by a wall or other obstacle.
        :param dx:
        :param map_data:
        :param tx:
        :param ty:
        :param cx:
        :param cy:
        :return:
        """
        if dx == 0:
            return False
        if map_data[ty][tx] == 'B':
            return True
        if map_data[cy][cx] == 'L':
            return True
        below_ty = ty + 1
        if not (0 <= below_ty < len(map_data)):
            return True
        return map_data[below_ty][tx] not in ['F', 'T']


    def blocks_downward(self, dy, map_data, cx, cy):
        """
        Check if the movement in the y direction is blocked by a wall or other obstacle.
        :param dy:
        :param map_data:
        :param cx:
        :param cy:
        :return:
        """
        if dy <= 0:
            return False
        below = map_data[cy + 1][cx] if cy + 1 < len(map_data) else ''
        return map_data[cy][cx] not in ['D', 'E'] and below not in ['L', 'E', 'U']


    def blocks_upward(self, dy, map_data, tx, ty):
        """
        Check if the movement in the y direction is blocked by a wall or other obstacle.
        :param dy:
        :param map_data:
        :param tx:
        :param ty:
        :return:
        """
        if dy >= 0:
            return False
        cell = map_data[ty][tx]
        return cell == 'F' or cell not in ['L', 'D', 'E', 'U', 'T']


    def draw(self, surface, offset_y=0):
        """
        Draw the player sprite on the given surface at the player's position.
        :param surface:
        :param offset_y:
        :return:
        """
        surface.blit(self.sprites[self.frame], (self.x, self.y + offset_y))
