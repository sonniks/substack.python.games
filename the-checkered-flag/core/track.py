# core/track.py


import pygame
import math


GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)
GREEN = (0, 255, 0)


class Track:
    def __init__(self, mask_path, laps_required):
        self.mask_image = pygame.image.load(mask_path).convert()
        self.width = self.mask_image.get_width()
        self.height = self.mask_image.get_height()
        self.laps_required = laps_required
        self.start_line_pixels = self._find_start_line_pixels()
        self.spawn_line_pixels = self._find_spawn_line_pixels()
        self.waypoints = self._find_waypoints()
        self.crossing_axis, self.crossing_direction = self._analyze_start_line_direction()
        self.start_pos = self._calculate_start_pos()
        try:
            self.font = pygame.font.SysFont("Arial", 18, bold=True)
        except pygame.error:
            print("Arial font not found, using default Pygame font for waypoint numbers.")
            self.font = pygame.font.Font(None, 22)
        # print(f"Track loaded: {mask_path}")
        # print(f"Start position: {self.start_pos}")
        # print(f"Waypoints found: {len(self.waypoints)}. Order: {[(int(w[0]), int(w[1])) for w in self.waypoints]}")
        # print(f"Crossing axis: {self.crossing_axis}, required direction: {self.crossing_direction}")

    def _find_spawn_line_pixels(self):
        """
        Find all pixels that are part of the spawn line (green pixels).
        :return:
        """
        pixels = set()
        for y in range(self.height):
            for x in range(self.width):
                if self.mask_image.get_at((x, y))[:3] == GREEN:
                    pixels.add((x, y))
        return pixels


    def _find_start_line_pixels(self):
        """
        Find all pixels that are part of the start line (black pixels).
        :return:
        """
        pixels = set()
        for y in range(self.height):
            for x in range(self.width):
                if self.mask_image.get_at((x, y))[:3] == BLACK:
                    pixels.add((x, y))
        return pixels


    def _analyze_start_line_direction(self):
        """
        Analyze the start line direction based on the start and spawn line pixels.
        :return:
        """
        if not self.start_line_pixels or not self.spawn_line_pixels:
            return ("x", 1)
        sfx, sfy = zip(*self.start_line_pixels)
        spawnx, spawny = zip(*self.spawn_line_pixels)
        avg_sfx = sum(sfx) / len(sfx)
        avg_sfy = sum(sfy) / len(sfy)
        avg_spawnx = sum(spawnx) / len(spawnx)
        avg_spawny = sum(spawny) / len(spawny)
        dx_line = max(sfx) - min(sfx)
        dy_line = max(sfy) - min(sfy)
        if dy_line > dx_line:
            # S/F is mostly vertical → check movement on x-axis
            crossing_axis = "x"
            crossing_direction = 1 if avg_spawnx < avg_sfx else -1
        else:
            # S/F is mostly horizontal → check movement on y-axis
            crossing_axis = "y"
            crossing_direction = 1 if avg_spawny < avg_sfy else -1
        return (crossing_axis, crossing_direction)

    def _calculate_start_pos(self):
        """
        Calculate a safe starting position near the start/finish line.
        :return:
        """
        for y in range(self.height):
            for x in range(self.width):
                if self.mask_image.get_at((x, y))[:3] == MAGENTA:
                    return (x, y)
        if not self.start_line_pixels:
            print("Warning: No start line pixels for _calculate_start_pos fallback. Using default.")
            return (100, 100)
        xs, ys = zip(*self.start_line_pixels)
        cx = sum(xs) // len(xs)
        cy = sum(ys) // len(ys)
        for radius in range(5, 60):
            for angle_deg in range(0, 360, 15):
                rad = math.radians(angle_deg)
                px = int(cx + radius * math.cos(rad))
                py = int(cy + radius * math.sin(rad))
                if not (0 <= px < self.width and 0 <= py < self.height):
                    continue
                is_safe_spot = True
                if self.mask_image.get_at((px, py))[:3] == GRAY:
                    for sx_offset in range(-1, 2):
                        for sy_offset in range(-1, 2):
                            check_x, check_y = px + sx_offset, py + sy_offset
                            if not (0 <= check_x < self.width and 0 <= check_y < self.height and \
                                    self.mask_image.get_at((check_x, check_y))[:3] == GRAY):
                                is_safe_spot = False
                                break
                        if not is_safe_spot:
                            break
                    if is_safe_spot:
                        return (px, py)
        print("Warning: No safe gray area found near S/F line for start_pos. Defaulting to S/F center.")
        return (cx, cy)

    def _find_waypoints(self):
        """
        Find all clusters of blue pixels in the mask image and calculate their centroids.
        :return:
        """
        visited = set()
        clusters_pixels_list = []
        for y_coord in range(self.height):
            for x_coord in range(self.width):
                if self.mask_image.get_at((x_coord, y_coord))[:3] == BLUE and (x_coord, y_coord) not in visited:
                    current_cluster_pixels = []
                    stack = [(x_coord, y_coord)]
                    visited.add((x_coord, y_coord))
                    while stack:
                        cx_pixel, cy_pixel = stack.pop()
                        current_cluster_pixels.append((cx_pixel, cy_pixel))
                        for dx_offset in [-1, 0, 1]:
                            for dy_offset in [-1, 0, 1]:
                                if dx_offset == 0 and dy_offset == 0:
                                    continue
                                nx, ny = cx_pixel + dx_offset, cy_pixel + dy_offset
                                if (0 <= nx < self.width and 0 <= ny < self.height and
                                        (nx, ny) not in visited and
                                        self.mask_image.get_at((nx, ny))[:3] == BLUE):
                                    visited.add((nx, ny))
                                    stack.append((nx, ny))
                    if current_cluster_pixels:
                        clusters_pixels_list.append(current_cluster_pixels)
        if not clusters_pixels_list:
            return []
        waypoint_centroids = []
        for pixel_list in clusters_pixels_list:
            if not pixel_list: continue
            xs, ys = zip(*pixel_list)
            centroid_x = sum(xs) / len(xs)
            centroid_y = sum(ys) / len(ys)
            waypoint_centroids.append((centroid_x, centroid_y))
        if not waypoint_centroids:
            return []
        if len(waypoint_centroids) > 1:
            sort_pivot_x = sum(p[0] for p in waypoint_centroids) / len(waypoint_centroids)
            sort_pivot_y = sum(p[1] for p in waypoint_centroids) / len(waypoint_centroids)
            def angle_from_pivot(point):
                point_x, point_y = point
                # --- THIS IS THE CRITICAL CHANGE FOR CCW SORTING ---
                # To get CCW order with atan2(y,x) where Pygame's Y increases downwards,
                # we use (pivot_y - point_y) as the "y" component for atan2.
                return math.atan2(sort_pivot_y - point_y, point_x - sort_pivot_x)
            waypoint_centroids.sort(key=angle_from_pivot)  # Sorts ascending by angle
        if self.start_line_pixels and waypoint_centroids:
            sfx_sum = sum(x_pix for x_pix, y_pix in self.start_line_pixels)
            sfy_sum = sum(y_pix for x_pix, y_pix in self.start_line_pixels)
            sfx_center = sfx_sum / len(self.start_line_pixels)
            sfy_center = sfy_sum / len(self.start_line_pixels)
            closest_index = 0
            min_dist_sq = float('inf')
            for i, (wp_x, wp_y) in enumerate(waypoint_centroids):
                dist_sq = (wp_x - sfx_center) ** 2 + (wp_y - sfy_center) ** 2
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    closest_index = i
            waypoint_centroids = waypoint_centroids[closest_index:] + waypoint_centroids[:closest_index]
        return waypoint_centroids

    def is_on_track(self, x, y):
        """
        Check if the given coordinates are on the track (gray area).
        :param x:
        :param y:
        :return:
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.mask_image.get_at((int(x), int(y)))[:3] == GRAY

    def is_crashing(self, x, y):
        """
        Check if the given coordinates are crashing (white area).
        :param x:
        :param y:
        :return:
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        pixel = self.mask_image.get_at((int(x), int(y)))[:3]
        return pixel == WHITE

    def crossed_start_line(self, x, y, prev_x, prev_y, tag="player"):
        """
        Check if the given coordinates crossed the start line in the correct direction.
        :param x:
        :param y:
        :param prev_x:
        :param prev_y:
        :param tag:
        :return:
        """
        if not (0 <= int(x) < self.width and 0 <= int(y) < self.height):
            return False
        if self.mask_image.get_at((int(x), int(y)))[:3] != BLACK:
            return False
        passed_correctly = False
        if self.crossing_axis == "x":
            if self.crossing_direction == -1 and prev_x > x:
                passed_correctly = True
            elif self.crossing_direction == 1 and prev_x < x:
                passed_correctly = True
        elif self.crossing_axis == "y":
            if self.crossing_direction == -1 and prev_y > y:
                passed_correctly = True
            elif self.crossing_direction == 1 and prev_y < y:
                passed_correctly = True
        return passed_correctly

    def draw(self, surface):
        """
        Draw the track mask and waypoints on the given surface.
        :param surface:
        :return:
        """
        surface.blit(self.mask_image, (0, 0))
        if self.waypoints:
            text_color = (255, 255, 0)
            shadow_color = (0, 0, 0)
            for i, (wp_x, wp_y) in enumerate(self.waypoints):
                shadow_surf = self.font.render(str(i), True, shadow_color)
                shadow_rect = shadow_surf.get_rect(center=(int(wp_x) + 1, int(wp_y) + 1))
                surface.blit(shadow_surf, shadow_rect)
                text_surf = self.font.render(str(i), True, text_color)
                text_rect = text_surf.get_rect(center=(int(wp_x), int(wp_y)))
                surface.blit(text_surf, text_rect)

    def get_counter_clockwise_bias_vector(self):
        """
        Calculate a vector that points in the counter-clockwise direction from the start line center
        :return:
        """
        if not self.start_line_pixels:
            return (0, 0)
        track_center_x = self.width // 2
        track_center_y = self.height // 2
        xs, ys = zip(*self.start_line_pixels)
        sfx = sum(xs) // len(xs)
        sfy = sum(ys) // len(ys)
        dx_vec = sfx - track_center_x
        dy_vec = sfy - track_center_y
        length = math.hypot(dx_vec, dy_vec)
        if length == 0:
            return (0, 0)
        norm_dx = dx_vec / length
        norm_dy = dy_vec / length
        return (-norm_dy, norm_dx)