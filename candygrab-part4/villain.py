# villain.py

import pygame
from loader import TILE_SIZE
from logger import conlog
from visualeffects import hue_shift_sprite
from movement import (
    get_tile_position, get_surrounding_tiles,
    maybe_snap_to_floor, try_move
)
from collections import deque

DISABLE_WINDOW_MS = 2000
DISABLE_DURATION_MS = 30000


class Villain:
    def __init__(self, map_data, spawn_xy, hue_shift=0, index=0, total=1, speed_multiplier=1.0):
        self.index = index
        self.name = f"Villain{index}"
        self.MOVE_SPEED = self.compute_speed(index, total, speed_multiplier)
        self.x, self.y = spawn_xy
        self.facing_left = False
        self.timer = 0
        self.frame = 0
        self.disabled_until = 0
        self.hit_times = deque()
        self._hue_shift = hue_shift
        self.sprites = self._load_villain_anim(hue_shift)
        self.disabled_sprite = self._load_disabled_sprite()
        # For maintaining committed direction of travel
        self.last_dx = 0
        self.last_dy = 0
        self.tile_x = int(self.x // TILE_SIZE) # spawn location
        self.tile_y = int(self.y // TILE_SIZE) # spawn location


    def compute_speed(self, index, total, speed_multiplier=1.0):
        min_speed = 1.2
        max_speed = 1.8
        t = index / max(1, total - 1)
        return (min_speed + t * (max_speed - min_speed)) * speed_multiplier

    def _load_villain_anim(self, hue_shift):
        sheet = pygame.image.load("assets/sprites/sheet.png").convert_alpha()
        base = [sheet.subsurface(pygame.Rect(i * TILE_SIZE, TILE_SIZE, TILE_SIZE, TILE_SIZE)) for i in range(4)]
        return [hue_shift_sprite(s, hue_shift) for s in base]

    def _load_disabled_sprite(self):
        sheet = pygame.image.load("assets/sprites/sheet.png").convert_alpha()
        rect = pygame.Rect(5 * TILE_SIZE, 1 * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        return sheet.subsurface(rect)

    def is_disabled(self):
        return self.disabled_until and pygame.time.get_ticks() < self.disabled_until

    def register_hit(self, now_ms):
        self.hit_times.append(now_ms)
        while self.hit_times and now_ms - self.hit_times[0] > DISABLE_WINDOW_MS:
            self.hit_times.popleft()
        if len(self.hit_times) >= 3 and not self.is_disabled():
            self.disabled_until = now_ms + DISABLE_DURATION_MS

    def handle_floor_collision(self, current_tile, cx, cy):
        if current_tile == 'F':
            self.y -= 1.0
            return True
        return False

    def update(self, player, map_data):
        self.timer += 1
        now = pygame.time.get_ticks()
        # Wake-up warning 2 seconds before recovery
        if self.is_disabled() and self.disabled_until - now <= 1000:
            if not hasattr(self, "_wake_warned") or not self._wake_warned:
                if not hasattr(self, "_wake_sound"):
                    self._wake_sound = pygame.mixer.Sound("assets/sounds/villain-wake.wav")
                    self._wake_sound.set_volume(0.6)
                self._wake_sound.play()
                self._wake_warned = True
        # Clear disabled state if expired
        if self.disabled_until and now >= self.disabled_until:
            self.disabled_until = 0
            self._wake_warned = False  # reset for next disable cycle
        if self.is_disabled():
            return
        maybe_snap_to_floor(self, map_data)
        if self.timer % 10 == 0:
            self.frame = (self.frame + 1) % len(self.sprites)
        cx, cy = get_tile_position(self)
        current_tile = map_data[cy][cx]
        if self.handle_floor_collision(current_tile, cx, cy):
            return
        self._decide_movement(player, cx, cy, map_data)


    def delta_to_align_x(self) -> int:
        """
        Return the number of pixels the villain is offset from perfect X alignment.
        """
        return int(self.x % TILE_SIZE)

    def delta_to_align_y(self) -> int:
        """
        Return the number of pixels the villain is offset from perfect Y alignment.
        """
        return int(self.y % TILE_SIZE)

    def _decide_movement(self, player, cx, cy, map_data):
        st = get_surrounding_tiles(self, map_data)
        conlog(f"{self.name} at tile ({cx},{cy}) sees: {st['locen']} {ord(st['locen'])}")
        if self.delta_to_align_x() > 1 and st['right'] != 'B' and st['left'] != 'B' and st['locen'] != ' ':
            if self.last_dx != 0 :
                #conlog("not aligned x")
                try_move(self, self.last_dx, 0, map_data)
            return
        if st['locen'] == ' ':
            conlog(f"{self.name} trying to snap to floor")
            self.choose_snap(map_data)
            return
        if self.delta_to_align_y() > 1:
            if self.last_dy != 0:
                #conlog("not aligned y")
                try_move(self, 0, self.last_dy, map_data)
            return
        # Determine player offset (tile-based)
        pcx, pcy = get_tile_position(player)
        dx = pcx - cx
        dy = pcy - cy
        center_tile = map_data[cy][cx]
        on_ladder = center_tile in {'U', 'D', 'E', 'T', 'L'}
        # Determine initial dominant axis
        prefer_horizontal = abs(dx) >= abs(dy)
        idax = -1 if dx < 0 else 1 if dx > 0 else 0
        iday = -1 if dy < 0 else 1 if dy > 0 else 0
        #conlog(f"{self.name} at ({cx},{cy}) sees Player at ({pcx},{pcy}) => dx={dx}, dy={dy}")
        #conlog(f"{self.name} center tile: '{center_tile}' | on_ladder={on_ladder}")
        #conlog(f"{self.name} initial intended direction: idax={idax}, iday={iday}")
        # Restrict vertical if not on ladder
        if not on_ladder and iday != 0:
            # conlog(f"{self.name} cannot move vertically (not on ladder), switching to horizontal.")
            iday = 0
            idax = -1 if dx < 0 else 1 if dx > 0 else 0
        # Restrict horizontal if on ladder
        elif on_ladder and iday != 0:
            if iday == -1 and center_tile == 'D':
                iday = 0
                idax = self.last_dx
            elif iday == 1 and center_tile in {'D', 'E', 'L', 'T'}:
                iday = 1
                idax = 0
            elif iday == 1 and center_tile == 'U':
                iday = 0
                idax = self.last_dx
            elif  iday == -1 and center_tile in {'U', 'E', 'L', 'T'}:
                iday = -1
                idax = 0
            # conlog(f"{self.name} is on a ladder; switching to vertical climb.")
            # idax = 0
            # iday = -1 if dy < 0 else 1 if dy > 0 else 0
        # conlog(f"{self.name} final intended direction: idax={idax}, iday={iday}")
        if st['locen'] == " ":
            conlog(f"ALERT {self.name} is over empty space, cannot move.")
            self.choose_snap(map_data)
        # At this point you can proceed with movement attempt based on idax/iday
        self.last_dx = idax
        self.last_dy = iday
        if idax != 0:
            if st['loleft'] not in {'F', 'T'} and idax == -1:
                conlog(f"no floor left {st['loleft']}")
                return
            if st['loright'] not in {'F', 'T'} and idax == 1:
                conlog(f"no floor right {st['loright']}")
                return
            self.facing_left = idax > 0  # optional flip
            moved = try_move(self, idax, 0, map_data)
            if moved:
                conlog(f"{self.name} moved horizontally: idax={idax}")
            return
        if iday != 0:
            moved = try_move(self, 0, iday, map_data)
            if moved:
                conlog(f"{self.name} moved vertically: iday={iday}")
            return
        # conlog(f"{self.name} did not move this frame.")


    def choose_snap(self, map_data):
        st = get_surrounding_tiles(self, map_data)
        cx, cy = get_tile_position(self)
        conlog(f"ALERT {self.name} is over empty space, cannot move.")
        if st['loleft'] != " ":
            conlog(f"{self.name} snapping left to ({cx - 1}, {cy})")
            self.teleport_to_tile(cx - 1, cy)
            return
        if st['loright'] != " ":
            conlog(f"{self.name} snapping right to ({cx + 1}, {cy})")
            self.teleport_to_tile(cx + 1, cy)
            return
        if st['upcen'] != " ":
            conlog(f"{self.name} snapping right to ({cx}, {cy - 1})")
            self.teleport_to_tile(cx, cy - 1)
            return

    def teleport_to_tile(self, tile_x, tile_y):
        """
        Instantly move the villain to a specific tile position.
        :param tile_x: Tile X-coordinate
        :param tile_y: Tile Y-coordinate
        """
        self.x = tile_x * TILE_SIZE
        self.y = tile_y * TILE_SIZE

    def draw(self, surface, offset_y=0):
        if self.is_disabled():
            sprite = self.disabled_sprite
        else:
            sprite = self.sprites[self.frame]
            if self.facing_left:
                sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (int(self.x), int(self.y + offset_y)))
