import curses
import math
import random


def draw_battlefield(stdscr, angle, power, player, wind_speed, wind_direction, day, trajectory=None, east_fortress=None, west_fortress=None):
    """
    Draws the battlefield, fortresses, and projectiles.
    :param stdscr: screen reference for curses
    :param angle: angle of the cannon (indicator)
    :param power: power of the cannon (indicator)
    :param player: player (string for player indicator)
    :param wind_speed: wind speed (indicator)
    :param wind_direction: wind direction (indicator)
    :param day: day (indicator)
    :param trajectory: trajectory of the projectile (list of tuples)
    :param east_fortress: list of lists representing the EAST fortress
    :param west_fortress: list of lists representing the WEST fortress
    :return:
    """
    curses.curs_set(0)  # Hide the cursor
    stdscr.clear()
    height, width = 25, 80  # Game screen dimensions
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    stdscr.attron(curses.color_pair(1))
    # Ensure fortresses are initialized before rendering
    if east_fortress is None:
        east_fortress = [["*", "*", "*"] for _ in range(3)]
    if west_fortress is None:
        west_fortress = [["*", "*", "*"] for _ in range(3)]
    # Draw battlefield borders
    stdscr.border()
    # Draw Fortresses
    east_x, west_x = 65, 10  # Fortress positions
    for i, row in enumerate(east_fortress):
        stdscr.addstr(20 - i, east_x, "".join(row))  # EAST fortress
    for i, row in enumerate(west_fortress):
        stdscr.addstr(20 - i, west_x, "".join(row))  # WEST fortress
    # Ensure trajectory is a valid list before iterating
    if trajectory is None:
        trajectory = []  # Set to an empty list to avoid unpacking errors
    for point in trajectory:
        if isinstance(point, (list, tuple)) and len(point) == 2:
            proj_x, proj_y = point
            if 0 < proj_x < 80 and 0 < proj_y < 25:  # Ensure within screen limits
                stdscr.addstr(proj_y, proj_x, "o")
        else:
            stdscr.addstr(23, 2, f"Invalid Traj: {point}")  # Debug for unexpected values
            curses.napms(2000)
    # Game Info
    stdscr.addstr(1, 2, "CASTLES AND CANNONS")
    stdscr.addstr(3, 2, f"Wind: {wind_speed} {wind_direction}")
    stdscr.addstr(4, 2, f"Day: {day}")
    stdscr.addstr(6, 2, f"Player: {player} | Angle: {angle:.1f} | Power: {power:.1f}")
    stdscr.attroff(curses.color_pair(1))
    stdscr.refresh()


def check_hit(trajectory, east_x, west_x, east_fortress, west_fortress, player):
    """
    Checks if the projectile hits the opponent's fortress.
    :param trajectory: trajectory of the projectile (list of tuples)
    :param east_x: east x coordinate value
    :param west_x: west x coordinate value
    :param east_fortress: current list of lists representing the EAST fortress
    :param west_fortress: current list of lists representing the WEST fortress
    :param player: string of player to ensure they don't hit their own fortress
    :return: boolean indicating if a hit occurred, and debug log
    """
    debug_log = []
    hit = False
    debug_log.append(f"Expected WEST fortress: X={west_x}-{west_x + 2}, Y=17-19")
    debug_log.append(f"Expected EAST fortress: X={east_x}-{east_x + 2}, Y=17-19")
    for x, y in trajectory:
        # Skip checking the launching player's own fortress
        if (player == "EAST" and east_x <= x <= east_x + 2) or (player == "WEST" and west_x <= x <= west_x + 2):
            continue
        # Fortress Y-values must be within exact boundaries
        if 17 <= y <= 19:
            row = 19 - int(y)  # Convert y to fortress row (0-2)
            debug_log.append(f"Checking X: {x}, Y: {y} (Row: {row})")
            # Show column calculations
            col_origin_east = x - east_x
            col_origin_west = x - west_x
            debug_log.append(f"East Fortress: Expected X={east_x}-{east_x + 2}, Checking col {round(col_origin_east)}")
            debug_log.append(f"West Fortress: Expected X={west_x}-{west_x + 2}, Checking col {round(col_origin_west)}")
            # Determine column relative to the fortress origin
            col_origin_east = x - east_x
            col_origin_west = x - west_x
            if 0 <= row < 3 and 0 <= col_origin_east < 3 and east_fortress[row][col_origin_east] == "*":
                debug_log.append(f"**ACTUAL HIT on EAST fortress** at row {row}, col {col_origin_east}")
                east_fortress[row][col_origin_east] = " "  # Remove fortress block
                hit = True
                return hit, debug_log  # Stop checking after first hit
            if 0 <= row < 3 and 0 <= col_origin_west < 3 and west_fortress[row][col_origin_west] == "*":
                debug_log.append(f"**ACTUAL HIT on WEST fortress** at row {row}, col {col_origin_west}")
                west_fortress[row][col_origin_west] = " "  # Remove fortress block
                hit = True
                return hit, debug_log  # Stop checking after first hit
    if not hit:
        debug_log.append("No valid hit detected.")
    return hit, debug_log


def get_player_input(stdscr, prompt):
    """
    Get input from the player with a prompt.  Allow Q or QUIT of game.
    :param stdscr: curses screen reference
    :param prompt: prompt to display to user
    :return: value of input
    """
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    while True:
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(22, 2, " " * (len(prompt) + 5))  # Clear previous input
        stdscr.addstr(22, 2, prompt)
        stdscr.attroff(curses.color_pair(1))
        stdscr.refresh()
        curses.echo()
        # Enable color for user input
        stdscr.attron(curses.color_pair(1))
        input_value = stdscr.getstr(22, len(prompt) + 2, 5).decode('utf-8').strip().upper()
        stdscr.attroff(curses.color_pair(1))
        curses.noecho()
        if input_value in ["Q", "QUIT"]:
            stdscr.addstr(23, 2, "Quitting the game...", curses.color_pair(1))
            stdscr.refresh()
            curses.napms(2000)
            curses.endwin()
            exit()
        try:
            return float(input_value)  # Convert to float instead of int
        except ValueError:
            stdscr.addstr(23, 2, "Invalid input! Enter a number.")
            stdscr.refresh()
            curses.napms(1000)
            stdscr.addstr(23, 2, " " * 30)  # Clear error message


def check_win_condition(east_fortress, west_fortress):
    """
    Check if either fortress is completely destroyed.
    :param east_fortress: list of lists representing the EAST fortress
    :param west_fortress: list of lists representing the WEST fortress
    :return: string representing winner
    """
    east_destroyed = all("".join(row).strip() == "" for row in east_fortress)
    west_destroyed = all("".join(row).strip() == "" for row in west_fortress)
    if east_destroyed:
        return "WEST WINS!"
    if west_destroyed:
        return "EAST WINS!"
    return None  # No winner yet


def calculate_projectile(angle, power, origin_x, origin_y, player, wind_speed, wind_direction):
    """
    Physics routine for calculating the path of the projectile
    :param angle: User selected angle of cannon
    :param power: User selected power of cannon
    :param origin_x: The x coordinate of the launching cannon
    :param origin_y: The y coordinate of the launching cannon
    :param player: string for EAST or WEST
    :param wind_speed: current wind speed (int)
    :param wind_direction: current wind direction (string)
    :return:
    """
    g = 9.8  # Gravity
    angle_rad = math.radians(180 - angle) if player == "EAST" else math.radians(angle)
    time_of_flight = (2 * power * math.sin(angle_rad)) / g
    resolution = 0.03  # Smaller step size for more precise trajectory
    trajectory = []
    prev_x, prev_y = origin_x, origin_y
    t = 0
    while t <= time_of_flight:
        x = origin_x + (power * math.cos(angle_rad) * t)
        y = origin_y - (power * math.sin(angle_rad) * t - 0.5 * g * t ** 2)
        # Apply wind effect based on direction and player
        wind_effect = (wind_speed / 10) * t  # Wind influence increases over time
        if wind_direction == "EAST":
            if player == "EAST":
                x += wind_effect  # Boost EAST's shots
            else:
                x -= wind_effect  # Shorten WEST's shots
        elif wind_direction == "WEST":
            if player == "WEST":
                x += wind_effect  # Boost WEST's shots
            else:
                x -= wind_effect  # Shorten EAST's shots
        # Ensure x, y are integers when used in rendering
        x_rounded, y_rounded = round(x), round(y)
        # Append interpolated points
        if (x_rounded, y_rounded) not in trajectory:
            trajectory.append((x_rounded, y_rounded))
        t += resolution  # Smaller time step
    return trajectory


def ai_choose_shot(player, wind_speed, wind_direction):
    """
    "AI" chooses angle and power for the cannon
    :param player: string for EAST or WEST (whichever computer is subbing for)
    :param wind_speed: integer of wind speed
    :param wind_direction: string of direction
    :return: float angle, float power
    """
    base_angle = random.uniform(35, 55)  # AI now chooses an angle between 35-55
    base_power = random.uniform(15, 35)
    # Adjust for wind
    if wind_direction == "EAST":
        if player == "EAST":
            base_power += wind_speed * 0.5  # Boost EAST's shots if wind is EAST
        else:
            base_power -= wind_speed * 0.5  # Reduce WEST's shots if wind is EAST
    elif wind_direction == "WEST":
        if player == "WEST":
            base_power += wind_speed * 0.5  # Boost WEST's shots if wind is WEST
        else:
            base_power -= wind_speed * 0.5  # Reduce EAST's shots if wind is WEST
    # Introduce slight randomness to avoid perfect accuracy
    angle_variation = random.uniform(-5, 5)
    power_variation = random.uniform(-5, 5)
    return round(base_angle + angle_variation, 1), round(base_power + power_variation, 1)


def main(stdscr):
    """
    Main function to run the game
    :param stdscr: stdscr reference for curses
    :return:
    """
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Green text on black
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(10, 2, "Number of players (0-2)? ")
    stdscr.attroff(curses.color_pair(1))
    stdscr.refresh()
    curses.echo()
    num_players = stdscr.getstr(10, 27, 1).decode("utf-8").strip()
    curses.noecho()
    # Ensure valid input
    if num_players not in ["0", "1", "2"]:
        num_players = "2"  # Default to 2 humans if input is invalid
    num_players = int(num_players)
    # Determine AI control
    is_east_ai = num_players < 2  # AI controls EAST if only 1 or 0 human players
    is_west_ai = num_players < 1  # AI controls WEST if no human players
    angle, power = 45, 50  # Default values
    player = "EAST"
    day = 1
    turn_count = 0
    # Initialize fortresses
    east_fortress = [["*", "*", "*"] for _ in range(3)]
    west_fortress = [["*", "*", "*"] for _ in range(3)]
    # Initialize wind
    wind_speed = random.randint(3, 35)
    wind_direction = random.choice(["EAST", "WEST"])
    while True:
        # Check if the game is won before rendering anything
        winner = check_win_condition(east_fortress, west_fortress)
        if winner:
            stdscr.clear()
            stdscr.addstr(10, 30, winner, curses.A_BOLD)
            stdscr.addstr(12, 25, "Press R to restart or Q to quit", curses.A_BOLD)
            stdscr.refresh()
            while True:
                key = stdscr.getch()
                if key in [ord('r'), ord('R')]:
                    main(stdscr)  # Restart game
                    return
                elif key in [ord('q'), ord('Q')]:
                    exit()  # Quit game
        # Determine cannon origin based on current player
        origin_x, origin_y = (10, 19) if player == "WEST" else (65, 19)
        trajectory = []  # Set to None instead of an empty list
        draw_battlefield(stdscr, angle, power, player, wind_speed, wind_direction, day, trajectory, east_fortress,
                         west_fortress)
        # Determine if AI should play this turn
        if (player == "EAST" and is_east_ai) or (player == "WEST" and is_west_ai):
            angle, power = ai_choose_shot(player, wind_speed, wind_direction)
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(22, 2, f"Computer chooses Angle: {angle:.1f}, Power: {power:.1f}")
            stdscr.refresh()
            curses.napms(2000)  # Pause briefly so player can see AI's choice
        else:
            # Human player turn
            angle = get_player_input(stdscr, "Enter Angle (0-90): ")
            power = get_player_input(stdscr, "Enter Power (1-100): ")
        stdscr.addstr(21, 2, " " * 30)  # Clear input line
        # Calculate projectile trajectory with wind effects
        trajectory = calculate_projectile(angle, power, origin_x, origin_y, player, wind_speed, wind_direction)
        # Animate projectile motion
        for i in range(len(trajectory)):
            draw_battlefield(stdscr, angle, power, player, wind_speed, wind_direction, day, trajectory[:i+1], east_fortress, west_fortress)
            stdscr.refresh()
            curses.napms(50)
        # Debug: Display last 10 trajectory points
        #if len(trajectory) > 0:
        #    stdscr.addstr(22, 2, f"Last 10 Trajectory: {trajectory[-10:]}".ljust(76))
        # Check if the shot hits the opponent's fortress
        hit, debug_log = check_hit(trajectory, 65, 10, east_fortress, west_fortress, player)
        if hit:
            stdscr.addstr(23, 2, "Hit detected! Fortress damaged.", curses.color_pair(1))
        else:
            stdscr.addstr(23, 2, "Missed!", curses.color_pair(1))
        # Display up to 10 lines of debug output
        #max_debug_lines = min(len(debug_log), 10)
        #for i in range(max_debug_lines):
        #    if 24 + i < 25:  # Prevent writing past screen limits
        #        stdscr.addstr(24 + i, 2, debug_log[i][:76])
        stdscr.refresh()
        curses.napms(4000)  # Pause before next turn
        # Toggle player turn
        player = "WEST" if player == "EAST" else "EAST"
        turn_count += 1
        # Update wind every 8 turns (each player gets 4 turns per day)
        if turn_count % 8 == 0:
            day += 1
            wind_speed = random.randint(3, 35)
            wind_direction = random.choice(["EAST", "WEST"])


if __name__ == "__main__":
    curses.wrapper(main)
