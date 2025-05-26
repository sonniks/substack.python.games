# core/car.py

import pygame
import math
import random
from collections import deque

class BaseCar:
    def __init__(self, start_pos):
        self.x, self.y = start_pos
        self.prev_x, self.prev_y = self.x, self.y
        self.angle = 180
        self.speed = 0
        self.max_speed = 6
        self.acceleration = 0.2
        self.brake_force = 0.3
        self.turn_speed = 3
        self.drift = 0
        self.image = pygame.image.load("assets/cars/player_car.png").convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.lap_count = 0
        self.last_cross = False

    def update_physics(self, track, tag="ai"):
        """
        Update the car's position based on its speed and angle, checking for collisions with the track.
        :param track:
        :param tag:
        :return:
        """
        self.prev_x, self.prev_y = self.x, self.y
        if self.speed > 0:
            drift_strength = min(1.0, self.speed / self.max_speed)
            self.drift = drift_strength * math.sin(math.radians(self.angle)) * 1.5
        else:
            self.drift = 0
        rad = math.radians(self.angle + 90)
        dx = math.cos(rad) * self.speed
        dy = -math.sin(rad) * self.speed
        new_x = self.x + dx
        new_y = self.y + dy
        if track.is_crashing(new_x, new_y):
            self.speed *= -0.4
            if hasattr(self, 'crash_sound') and not self._crash_recently:
                self.crash_sound.play()
                self._crash_recently = True
        else:
            self.x = new_x + self.drift
            self.y = new_y
            self._crash_recently = False
        if track.is_crashing(self.x, self.y):
            max_radius = 20
            found = False
            for r in range(1, max_radius):
                for angle_deg in range(0, 360, 15):
                    rad = math.radians(angle_deg)
                    check_x = int(self.x + r * math.cos(rad))
                    check_y = int(self.y + r * math.sin(rad))
                    if track.is_on_track(check_x, check_y):
                        self.x = check_x
                        self.y = check_y
                        self.speed = 0
                        found = True
                        break
                if found:
                    break

    def draw(self, surface):
        """
        Draw the car on the given surface, rotated to its current angle.
        :param surface:
        :return:
        """
        rotated = pygame.transform.rotate(self.image, self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect)
        # If this car has an index, draw it (only AI cars do)
        if hasattr(self, 'index'):
            font = pygame.font.SysFont("Arial", 16, bold=True)
            text_surf = font.render(str(self.index), True, (255, 255, 255))
            text_shadow = font.render(str(self.index), True, (0, 0, 0))

            tx = rect.centerx - text_surf.get_width() // 2
            ty = rect.centery - text_surf.get_height() // 2

            surface.blit(text_shadow, (tx + 1, ty + 1))
            surface.blit(text_surf, (tx, ty))

class PlayerCar(BaseCar):
    def __init__(self, start_pos, waypoints):
        super().__init__(start_pos)
        self.crash_sound = pygame.mixer.Sound("assets/sounds/crash.wav")
        self.crash_sound.set_volume(0.6)
        self._crash_recently = False
        self.waypoints = waypoints
        self.checkpoints_hit = set()
        self.reset_checkpoint_progress()

    def update(self, mouse_pos, mouse_buttons, track):
        """
        Update the player's car based on keyboard input and mouse position.
        :param mouse_pos:
        :param mouse_buttons:
        :param track:
        :return:
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.angle += self.turn_speed
        if keys[pygame.K_RIGHT]:
            self.angle -= self.turn_speed
        if keys[pygame.K_UP]:
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN]:
            self.speed = max(self.speed - self.brake_force, -1)
        else:
            self.speed *= 0.98
        self.check_waypoints()
        self.update_physics(track, tag="player")
        crossed = track.crossed_start_line(self.x, self.y, self.prev_x, self.prev_y, tag="player")
        if crossed and not self.last_cross:
            if self.lap_ready():
                self.lap_count += 1
                # print(f"Lap {self.lap_count} completed!")
                self.reset_checkpoint_progress()
            self.last_cross = True
        elif not crossed:
            self.last_cross = False

    def check_waypoints(self):
        """
        Check if the car has hit any waypoints and update the checkpoints_hit set.
        :return:
        """
        for i, (wx, wy) in enumerate(self.waypoints):
            if i in self.checkpoints_hit:
                continue
            dist = math.hypot(self.x - wx, self.y - wy)
            if dist < 60:
                self.checkpoints_hit.add(i)

    def lap_ready(self):
        """
        Check if the car has hit all waypoints to determine if it is ready for a new lap.
        :return:
        """
        return len(self.checkpoints_hit) >= len(self.waypoints)

    def reset_checkpoint_progress(self):
        """
        Reset the checkpoints hit for a new lap.
        :return:
        """
        self.checkpoints_hit.clear()



class AICar(BaseCar):
    def __init__(self, start_pos, waypoints, track, index=0,
                 debug_this_ai=False):  # debug_this_ai can be kept for later
        super().__init__(start_pos)
        self.image = pygame.image.load("assets/cars/ai_car.png").convert_alpha()
        self.waypoints = waypoints  # CCW ordered list from track.py
        self.current_waypoint_index = 0
        self.speed_factor = random.uniform(0.85, 1.1)  # AI variety: slower to slightly faster
        self.steering_noise = random.uniform(3.5, 7.5)  # Aggressive corrections, visible wobble
        self.target_jitter = random.randint(8, 24)  # Noticeable drift off ideal line
        self.checkpoints_hit = set() # To track progress for lap_ready
        self.last_cross = False      # For debouncing S/F line crossing
        self.index = index  # For identification
        self.debug_ai = debug_this_ai  # Basic debug flag
        # Simpler initial angle: Try to face the first waypoint if waypoints exist
        if self.waypoints:
            target_x, target_y = self.waypoints[self.current_waypoint_index]
            dx = target_x - self.x
            dy = target_y - self.y
            # Angle to target. +90 because 0 angle for car sprite might be 'up'.
            self.angle = math.degrees(math.atan2(-dy, dx)) - 90
        else:
            # Fallback: Use the S/F line orientation if no waypoints
            if track.start_line_pixels:
                xs, ys = zip(*track.start_line_pixels)
                sfx = sum(xs) // len(xs)
                sfy = sum(ys) // len(ys)
                dx_sf = sfx - self.x
                dy_sf = sfy - self.y
                self.angle = math.degrees(math.atan2(-dy_sf, dx_sf)) - 90
            else:
                self.angle = 180  # Default if no other info
        self.angle %= 360

    def update(self, track):
        """
        Update the AI car's position and behavior based on the current track and waypoints.
        :param track:
        :return:
        """
        if not self.waypoints:
            self.speed = 0
            return
        target_waypoint = self.waypoints[self.current_waypoint_index]
        target_x, target_y = target_waypoint
        # Add random offset to simulate imperfect aim
        jitter = self.target_jitter
        target_x += random.randint(-jitter, jitter)
        target_y += random.randint(-jitter, jitter)
        delta_x = target_x - self.x
        delta_y = target_y - self.y
        angle_to_target_rad = math.atan2(-delta_y, delta_x)
        desired_angle_deg = math.degrees(angle_to_target_rad) - 90
        desired_angle_deg %= 360
        angle_diff = (desired_angle_deg - self.angle + 180 + 360) % 360 - 180
        turn_amount = 0
        if angle_diff > self.turn_speed:
            turn_amount = self.turn_speed
        elif angle_diff < -self.turn_speed:
            turn_amount = -self.turn_speed
        else:
            turn_amount = angle_diff
        self.angle += turn_amount
        self.angle %= 360
        self.speed = min(self.speed + self.acceleration * 0.3, self.max_speed * 0.6 * self.speed_factor)
        # Basic collision check (uses current self.angle and self.speed to project)
        lookahead_dist = 10
        rad_lookahead = math.radians(self.angle + 90)
        next_x_check = self.x + math.cos(rad_lookahead) * lookahead_dist
        next_y_check = self.y - math.sin(rad_lookahead) * lookahead_dist
        if track.is_crashing(next_x_check, next_y_check) or track.is_crashing(self.x, self.y):
            self.speed *= -0.5
        self.update_physics(track)
        delta_x_new = target_x - self.x
        delta_y_new = target_y - self.y
        distance_to_target_new = math.hypot(delta_x_new, delta_y_new)
        waypoint_reach_radius = 40
        if distance_to_target_new < waypoint_reach_radius:
            if self.current_waypoint_index not in self.checkpoints_hit:  # Add only if not already hit
                self.checkpoints_hit.add(self.current_waypoint_index)
                if self.debug_ai and self.index == 0:
                    print(
                        f"AI {self.index} added checkpoint {self.current_waypoint_index}. Hits: {self.checkpoints_hit}")
            self.current_waypoint_index = (self.current_waypoint_index + 1) % len(self.waypoints)
            if self.debug_ai and self.index == 0:
                print(f"AI {self.index} reached waypoint. Next target index: {self.current_waypoint_index}")
        crossed = track.crossed_start_line(self.x, self.y, self.prev_x, self.prev_y, tag=f"ai_{self.index}")
        if crossed and not self.last_cross:
            if self.lap_ready():
                self.lap_count += 1
                self.checkpoints_hit.clear()  # Reset checkpoints for the new lap
                if self.debug_ai and self.index == 0:
                    print(f"!!!!!!!! AI {self.index} COMPLETED LAP {self.lap_count} !!!!!!!!")
            elif self.debug_ai and self.index == 0:
                print(
                    f"  [AI {self.index}] Crossed S/F but not lap_ready (Hits:{len(self.checkpoints_hit)}/{len(self.waypoints)})")
            self.last_cross = True
        elif not crossed:
            self.last_cross = False

        # Basic HUD/debug print (very minimal)
        # if self.debug_ai and self.index == 0:
        #     print(
        #         f"AI {self.index}: Pos=({self.x:.0f},{self.y:.0f}) Angle={self.angle:.0f} "
        #         f"Speed={self.speed:.1f} TargetWP={self.current_waypoint_index} "
        #         f"({target_x:.0f},{target_y:.0f}) Dist={distance_to_target_new:.0f} "  # use new distance
        #         f"LapCount: {self.lap_count}"
        #     )


    def lap_ready(self):
        """
        Check if the AI car has hit all waypoints to determine if it is ready for a new lap.
        :return:
        """
        return len(self.checkpoints_hit) >= len(self.waypoints)
