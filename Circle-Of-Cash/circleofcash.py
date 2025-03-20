import random
import time
import curses

# Wheel values, including Bankrupt and Lose a Turn
BASE_WHEEL_VALUES = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, "BANKRUPT", "LOSE A TURN"]

# Expanded Phrases and Categories
PHRASES = [
    # MOVIE TITLES
    ("MOVIE TITLE", "THE GODFATHER"),
    ("MOVIE TITLE", "STAR WARS"),
    ("MOVIE TITLE", "THE SHAWSHANK REDEMPTION"),
    ("MOVIE TITLE", "PULP FICTION"),
    ("MOVIE TITLE", "FORREST GUMP"),
    ("MOVIE TITLE", "THE DARK KNIGHT"),
    ("MOVIE TITLE", "INCEPTION"),
    ("MOVIE TITLE", "THE MATRIX"),
    ("MOVIE TITLE", "JURASSIC PARK"),
    ("MOVIE TITLE", "FIGHT CLUB"),
    ("MOVIE TITLE", "CASABLANCA"),
    ("MOVIE TITLE", "THE LORD OF THE RINGS"),
    ("MOVIE TITLE", "BACK TO THE FUTURE"),
    ("MOVIE TITLE", "GLADIATOR"),
    ("MOVIE TITLE", "TITANIC"),
    ("MOVIE TITLE", "SCHINDLER'S LIST"),
    ("MOVIE TITLE", "THE SILENCE OF THE LAMBS"),
    ("MOVIE TITLE", "THE AVENGERS"),
    ("MOVIE TITLE", "GOODFELLAS"),
    ("MOVIE TITLE", "ROCKY"),

    # FAMOUS PEOPLE
    ("FAMOUS PERSON", "ALBERT EINSTEIN"),
    ("FAMOUS PERSON", "MARILYN MONROE"),
    ("FAMOUS PERSON", "LEONARDO DA VINCI"),
    ("FAMOUS PERSON", "WILLIAM SHAKESPEARE"),
    ("FAMOUS PERSON", "ELON MUSK"),
    ("FAMOUS PERSON", "ABRAHAM LINCOLN"),
    ("FAMOUS PERSON", "MICHAEL JORDAN"),
    ("FAMOUS PERSON", "WINSTON CHURCHILL"),
    ("FAMOUS PERSON", "MARTIN LUTHER KING JR"),
    ("FAMOUS PERSON", "JULIUS CAESAR"),
    ("FAMOUS PERSON", "OPRAH WINFREY"),
    ("FAMOUS PERSON", "STEVE JOBS"),
    ("FAMOUS PERSON", "BARACK OBAMA"),
    ("FAMOUS PERSON", "NELSON MANDELA"),
    ("FAMOUS PERSON", "ISAAC NEWTON"),
    ("FAMOUS PERSON", "BENJAMIN FRANKLIN"),
    ("FAMOUS PERSON", "MOZART"),
    ("FAMOUS PERSON", "NIKOLA TESLA"),
    ("FAMOUS PERSON", "MOTHER TERESA"),
    ("FAMOUS PERSON", "BEYONCE"),

    # PLACES
    ("PLACE", "GRAND CANYON"),
    ("PLACE", "EIFFEL TOWER"),
    ("PLACE", "STATUE OF LIBERTY"),
    ("PLACE", "GREAT WALL OF CHINA"),
    ("PLACE", "MOUNT EVEREST"),
    ("PLACE", "THE AMAZON RAINFOREST"),
    ("PLACE", "SAHARA DESERT"),
    ("PLACE", "DISNEYLAND"),
    ("PLACE", "TIMES SQUARE"),
    ("PLACE", "BIG BEN"),
    ("PLACE", "GOLDEN GATE BRIDGE"),
    ("PLACE", "TAJ MAHAL"),
    ("PLACE", "THE COLOSSEUM"),
    ("PLACE", "STONEHENGE"),
    ("PLACE", "NIAGARA FALLS"),
    ("PLACE", "VENICE CANALS"),
    ("PLACE", "HOLLYWOOD WALK OF FAME"),
    ("PLACE", "LOUVRE MUSEUM"),
    ("PLACE", "MOUNT RUSHMORE"),
    ("PLACE", "LAS VEGAS STRIP"),

    # THINGS
    ("THING", "COMPUTER KEYBOARD"),
    ("THING", "SMARTPHONE"),
    ("THING", "GUITAR"),
    ("THING", "MICROWAVE OVEN"),
    ("THING", "HEADPHONES"),
    ("THING", "WRISTWATCH"),
    ("THING", "WASHING MACHINE"),
    ("THING", "TELEVISION REMOTE"),
    ("THING", "VACUUM CLEANER"),
    ("THING", "COFFEE MAKER"),
    ("THING", "DIGITAL CAMERA"),
    ("THING", "ELECTRIC TOOTHBRUSH"),
    ("THING", "ROLLER COASTER"),
    ("THING", "PAPER CLIP"),
    ("THING", "VIDEO GAME CONTROLLER"),
    ("THING", "3D PRINTER"),
    ("THING", "ELECTRIC SCOOTER"),
    ("THING", "FINGERPRINT SCANNER"),
    ("THING", "SECURITY CAMERA"),
    ("THING", "SATELLITE DISH"),

    # PHRASES
    ("PHRASE", "A BLESSING IN DISGUISE"),
    ("PHRASE", "BREAK A LEG"),
    ("PHRASE", "BETTER LATE THAN NEVER"),
    ("PHRASE", "A PIECE OF CAKE"),
    ("PHRASE", "HIT THE NAIL ON THE HEAD"),
    ("PHRASE", "BITE THE BULLET"),
    ("PHRASE", "CUTTING CORNERS"),
    ("PHRASE", "THE BALL IS IN YOUR COURT"),
    ("PHRASE", "UNDER THE WEATHER"),
    ("PHRASE", "THE EARLY BIRD GETS THE WORM"),
    ("PHRASE", "A PENNY FOR YOUR THOUGHTS"),
    ("PHRASE", "PULLING YOUR LEG"),
    ("PHRASE", "LET THE CAT OUT OF THE BAG"),
    ("PHRASE", "ONCE IN A BLUE MOON"),
    ("PHRASE", "WHEN PIGS FLY"),
    ("PHRASE", "NO PAIN NO GAIN"),
    ("PHRASE", "BURNING THE MIDNIGHT OIL"),
    ("PHRASE", "THROW IN THE TOWEL"),
    ("PHRASE", "SPILL THE BEANS"),
    ("PHRASE", "HIT THE ROAD"),

    # SPORTS TEAMS
    ("SPORTS TEAM", "NEW YORK YANKEES"),
    ("SPORTS TEAM", "LOS ANGELES LAKERS"),
    ("SPORTS TEAM", "DALLAS COWBOYS"),
    ("SPORTS TEAM", "CHICAGO BULLS"),
    ("SPORTS TEAM", "GOLDEN STATE WARRIORS"),
    ("SPORTS TEAM", "GREEN BAY PACKERS"),
    ("SPORTS TEAM", "MANCHESTER UNITED"),
    ("SPORTS TEAM", "BOSTON RED SOX"),
    ("SPORTS TEAM", "PITTSBURGH STEELERS"),
    ("SPORTS TEAM", "TORONTO MAPLE LEAFS"),
    ("SPORTS TEAM", "BOSTON CELTICS"),
    ("SPORTS TEAM", "MIAMI HEAT"),
    ("SPORTS TEAM", "SEATTLE SEAHAWKS"),
    ("SPORTS TEAM", "REAL MADRID"),
    ("SPORTS TEAM", "BAYERN MUNICH"),
    ("SPORTS TEAM", "SAN FRANCISCO 49ERS"),
    ("SPORTS TEAM", "NEW ENGLAND PATRIOTS"),
    ("SPORTS TEAM", "CHICAGO CUBS"),
    ("SPORTS TEAM", "ATLANTA BRAVES"),
    ("SPORTS TEAM", "LOS ANGELES DODGERS"),

    # SONG TITLES
    ("SONG TITLE", "BOHEMIAN RHAPSODY"),
    ("SONG TITLE", "HOTEL CALIFORNIA"),
    ("SONG TITLE", "THRILLER"),
    ("SONG TITLE", "IMAGINE"),
    ("SONG TITLE", "LIKE A ROLLING STONE"),
    ("SONG TITLE", "SWEET CHILD O MINE"),
    ("SONG TITLE", "PURPLE RAIN"),
    ("SONG TITLE", "HEY JUDE"),
    ("SONG TITLE", "STAIRWAY TO HEAVEN"),
    ("SONG TITLE", "LET IT BE"),
    ("SONG TITLE", "SMELLS LIKE TEEN SPIRIT"),
    ("SONG TITLE", "DANCING QUEEN"),
    ("SONG TITLE", "WE WILL ROCK YOU"),
    ("SONG TITLE", "SOMEBODY TO LOVE"),
    ("SONG TITLE", "PIANO MAN"),
    ("SONG TITLE", "DON'T STOP BELIEVING"),
    ("SONG TITLE", "I WILL SURVIVE"),
    ("SONG TITLE", "EVERY BREATH YOU TAKE"),
    ("SONG TITLE", "BORN TO RUN"),
    ("SONG TITLE", "ANOTHER BRICK IN THE WALL"),
]


def initialize_game(stdscr):
    """
    Initialize the game by setting up the screen and getting player information.
    :param stdscr:
    :return:
    """
    curses.curs_set(1)
    stdscr.clear()
    num_players = int(get_key_choice(stdscr, "Enter number of human players (0-3): ", "0123"))
    players, overall_scores = get_players(stdscr, num_players)
    return players, overall_scores


def get_players(stdscr, num_players):
    """
    Get player names and types (human or AI) based on the number of players.
    :param stdscr:
    :param num_players:
    :return:
    """
    players = []
    overall_scores = {}
    for i in range(num_players):
        stdscr.addstr(24, 0, f"Enter name for Player {i+1}: ")
        stdscr.refresh()
        curses.echo()
        name = stdscr.getstr().decode("utf-8")
        curses.noecho()
        players.append((name, "human"))
        overall_scores[name] = 0
    for i in range(3 - num_players):
        difficulty = get_key_choice(stdscr, f"Select AI difficulty for Player {num_players + i + 1} ([E]asy/[M]edium/[H]ard): ", "emh")
        ai_name = f"AI Player {i+1}"
        players.append((ai_name, difficulty))
        overall_scores[ai_name] = 0
    return players, overall_scores


def play_round(stdscr, round_number, players, overall_scores, used_phrases):
    """
    Play a single round of the game, where players take turns guessing letters or solving the puzzle.
    :param stdscr:
    :param round_number:
    :param players:
    :param overall_scores:
    :param used_phrases:
    :return:
    """
    category, puzzle = get_new_puzzle(used_phrases)
    revealed = [char == " " for char in puzzle]
    cash = {p[0]: 0 for p in players}
    guessed_letters = set()
    current_player = 0
    round_winner = [None]  # Updated to be mutable
    while not all(revealed):
        stdscr.clear()
        display_scores(stdscr, players, cash, overall_scores)
        display_puzzle_board(stdscr, category, puzzle, revealed, guessed_letters)
        player_name, player_type = players[current_player]
        stdscr.addstr(16, 0, f"{player_name}'s turn!")
        stdscr.refresh()
        choice = get_player_choice(stdscr, player_name, player_type, cash, round_number, revealed, puzzle)
        if choice == "q":
            return None
        retain_turn = handle_choice(stdscr, choice, player_name, player_type, cash, round_number, puzzle, revealed, guessed_letters, round_winner)
        if not retain_turn:
            current_player = (current_player + 1) % len(players)
        if round_winner[0]:  # If a winner was set
            overall_scores[round_winner[0]] += cash[round_winner[0]]
            stdscr.addstr(18, 0, f"{round_winner[0]} wins the round!", curses.A_BOLD | curses.A_REVERSE)
            stdscr.refresh()
            time.sleep(4)  # Pause to display the winner message
            break
    return round_winner[0]


def get_new_puzzle(used_phrases):
    """
    Select a new puzzle from the list of phrases, ensuring it hasn't been used in the current game.
    :param used_phrases:
    :return:
    """
    while True:
        category, puzzle = random.choice(PHRASES)
        if puzzle not in used_phrases:
            used_phrases.add(puzzle)
            return category, puzzle

def handle_choice(stdscr, choice, player_name, player_type, cash, round_number, puzzle, revealed, guessed_letters, round_winner):
    """
    Handle the player's choice of action (spin the wheel, solve the puzzle, or buy a vowel).
    :param stdscr:
    :param choice:
    :param player_name:
    :param player_type:
    :param cash:
    :param round_number:
    :param puzzle:
    :param revealed:
    :param guessed_letters:
    :param round_winner:
    :return:
    """
    if choice == "w":
        return handle_wheel_spin(stdscr, player_name, player_type, cash, round_number, puzzle, revealed, guessed_letters)
    elif choice == "s":
        return handle_solve_attempt(stdscr, player_name, player_type, puzzle, cash, round_winner)
    return False


def handle_wheel_spin(stdscr, player_name, player_type, cash, round_number, puzzle, revealed, guessed_letters):
    """
    Handle the player's choice to spin the wheel and guess a letter.
    :param stdscr:
    :param player_name:
    :param player_type:
    :param cash:
    :param round_number:
    :param puzzle:
    :param revealed:
    :param guessed_letters:
    :return:
    """
    result = spin_wheel(stdscr, round_number)
    stdscr.addstr(19, 0, f"Spun: {result}     ")
    stdscr.refresh()
    time.sleep(1)
    if result == "BANKRUPT":
        cash[player_name] = 0
    elif result == "LOSE A TURN":
        return False
    else:
        if player_type != "human":
            letter, _ = ai_guess_letter(player_type, guessed_letters, buying_vowel=False, cash=cash[player_name],
                                        round_number=round_number)
        else:
            letter = get_key_choice(stdscr, "Guess a consonant: ", "bcdfghjklmnpqrstvwxyz").upper()

        if letter and letter not in guessed_letters:
            guessed_letters.add(letter)
            if letter in puzzle:
                revealed[:] = [r or (c == letter) for r, c in zip(revealed, puzzle)]
                cash[player_name] += int(result)
                return True
    return False


def handle_solve_attempt(stdscr, player_name, player_type, puzzle, cash, round_winner):
    """
    Handle the player's attempt to solve the puzzle.
    :param stdscr:
    :param player_name:
    :param player_type:
    :param puzzle:
    :param cash:
    :param round_winner:
    :return:
    """
    stdscr.addstr(22, 0, " " * 50)  # Clear previous text
    stdscr.addstr(22, 0, "Enter your solution: ")
    stdscr.refresh()
    if player_type == "human":
        curses.echo()
        guess = stdscr.getstr().decode("utf-8").strip().upper()
        curses.noecho()
    else:
        time.sleep(1)
        stdscr.addstr(22, 0, f"{player_name} is attempting to solve...")
        stdscr.refresh()
        time.sleep(2)
        guess = puzzle if random.random() < 0.6 else "INCORRECT GUESS"
    stdscr.addstr(23, 0, f"{player_name} guessed: {guess}")
    stdscr.refresh()
    time.sleep(3)
    if guess == puzzle:
        round_winner[0] = player_name  # Store the round winner
        return True
    return False


def get_player_choice(stdscr, player_name, player_type, cash, round_number, revealed, puzzle):
    """
    Get the player's choice of action based on their type (human or AI).
    :param stdscr:
    :param player_name:
    :param player_type:
    :param cash:
    :param round_number:
    :param revealed:
    :param puzzle:
    :return:
    """
    valid_choices = "ws"
    if cash[player_name] >= 250 * round_number:
        valid_choices += "v"
    if player_type == "human":
        valid_choices += "q"  # Only humans can quit
        return get_key_choice(stdscr, "(W)heel, " + ("(V)owel, " if "v" in valid_choices else "") + "(S)olve, (Q)uit: ",
                              valid_choices)
    else:
        time.sleep(1)
        revealed_ratio = float(sum(revealed) / len(puzzle))  # Ensure floating-point calculation
        difficulty_threshold = {"e": 0.8, "m": 0.5, "h": 0.3}
        ta = float(difficulty_threshold.get(player_type, 1.0))  # Ensure proper threshold type
        stdscr.addstr(16, 0, f"{player_name} Thinking: Revealed {revealed_ratio:.4f}, Threshold {ta:.4f}")
        stdscr.refresh()
        time.sleep(2)
        # Explicit comparison
        if revealed_ratio >= ta:
            stdscr.refresh()
            time.sleep(2)
            return "s"  # AI will attempt to solve if enough letters are revealed
        return random.choice(valid_choices)


def spin_wheel(stdscr, round_number):
    """
    Simulate spinning the wheel and return a random value based on the round number.
    :param stdscr:
    :param round_number:
    :return:
    """
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    multiplier = 1 if round_number == 1 else (2.5 if round_number == 2 else 5)
    wheel_values = [int(v * multiplier) if isinstance(v, int) else v for v in BASE_WHEEL_VALUES]
    for _ in range(random.randint(10, 20)):
        result = str(random.choice(wheel_values)).ljust(15)
        stdscr.addstr(18, 0, f"Spinning... {result}   ", curses.color_pair(1))
        stdscr.refresh()
        time.sleep(0.1)
    return result.strip()


# def display_game_state(stdscr, round_number, puzzle, revealed, cash, overall_scores, guessed_letters, players):
#     """
#     Display the current game state including the round number, puzzle, scores, and guessed letters.
#     :param stdscr:
#     :param round_number:
#     :param puzzle:
#     :param revealed:
#     :param cash:
#     :param overall_scores:
#     :param guessed_letters:
#     :param players:
#     :return:
#     """
#     stdscr.clear()
#     stdscr.addstr(1, 0, f"Round {round_number}")
#     stdscr.addstr(3, 0, f"Puzzle: {display_puzzle(puzzle, revealed)}")
#     stdscr.addstr(5, 0, "Scores (Current Round)", curses.A_REVERSE)
#     for i, (player, _) in enumerate(players):
#         stdscr.addstr(6 + i, 0, f"{player}: ${cash[player]}")
#     stdscr.addstr(10, 0, "Overall Scores", curses.A_REVERSE)
#     for i, (player, _) in enumerate(players):
#         stdscr.addstr(11 + i, 0, f"{player}: ${overall_scores[player]}")
#     stdscr.addstr(17, 0, f"Guessed Letters: {' '.join(sorted(guessed_letters))}")
#     stdscr.refresh()


def display_puzzle(puzzle, revealed):
    """
    Create a string representation of the puzzle, showing revealed letters and underscores for hidden letters.
    :param puzzle:
    :param revealed:
    :return:
    """
    return " ".join([char if revealed[i] else "_" for i, char in enumerate(puzzle)])

def display_message(stdscr, message, delay=4):
    """
    Display a message on the screen for a specified duration, then clear it.
    :param stdscr:
    :param message:
    :param delay:
    :return:
    """
    stdscr.addstr(18, 0, message, curses.A_BOLD | curses.A_REVERSE)
    stdscr.refresh()
    time.sleep(delay)
    stdscr.addstr(18, 0, " " * len(message))
    stdscr.refresh()

def get_key_choice(stdscr, prompt, valid_keys):
    """
    Display a prompt and wait for the user to press a key that is in the valid_keys string.
    :param stdscr:
    :param prompt:
    :param valid_keys:
    :return:
    """
    stdscr.addstr(22, 0, " " * 50)
    stdscr.addstr(22, 0, prompt)
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        key = chr(key).lower()
        if key in valid_keys:
            return key


def ai_guess_letter(difficulty, guessed_letters, buying_vowel=False, cash=0, round_number=1):
    """
    AI logic to guess a letter based on the difficulty level and current game state.
    :param difficulty:
    :param guessed_letters:
    :param buying_vowel:
    :param cash:
    :param round_number:
    :return:
    """
    consonants = "BCDFGHJKLMNPQRSTVWXYZ"
    vowels = "AEIOU"
    available_consonants = [char for char in consonants if char not in guessed_letters]
    available_vowels = [char for char in vowels if char not in guessed_letters]
    vowel_cost = 250 * round_number
    if buying_vowel:
        if cash >= vowel_cost and available_vowels:
            return random.choice(available_vowels), -vowel_cost  # Deduct the cost
        return None, 0  # Not enough cash or no vowels left
    if difficulty == "e":
        return (random.choice(available_consonants), 0) if available_consonants else (None, 0)
    elif difficulty == "m":
        return (random.choice(available_consonants[:len(available_consonants) // 2]), 0) if available_consonants else (
        None, 0)
    else:
        return (random.choice(available_consonants[:len(available_consonants) // 3]), 0) if available_consonants else (
        None, 0)


def display_scores(stdscr, players, cash, overall_scores):
    """
    Display the current scores for each player, including their cash for the current round and overall scores.
    :param stdscr:
    :param players:
    :param cash:
    :param overall_scores:
    :return:
    """
    stdscr.addstr(9, 0, "SCORES", curses.A_BOLD | curses.A_UNDERLINE)
    # Print column headers (Player Names)
    stdscr.addstr(10, 0, " | ".join([f"{p[0]:^12}" for p in players]))
    # Separator
    stdscr.addstr(11, 0, "-" * (len(players) * 15))
    # Current Round Scores (Inverted)
    stdscr.addstr(12, 0, " | ".join([f"{cash[p[0]]:^12}" for p in players]), curses.A_REVERSE)
    # Separator
    stdscr.addstr(13, 0, "-" * (len(players) * 15))
    # Overall Scores
    stdscr.addstr(14, 0, " | ".join([f"{overall_scores[p[0]]:^12}" for p in players]))
    stdscr.refresh()

def display_puzzle_board(stdscr, category, puzzle, revealed, guessed_letters):
    """
    Display the puzzle board, including the category, current puzzle state, and guessed letters.
    :param stdscr:
    :param category:
    :param puzzle:
    :param revealed:
    :param guessed_letters:
    :return:
    """
    stdscr.addstr(1, 0, "PUZZLE BOARD", curses.A_BOLD | curses.A_UNDERLINE)
    # Display puzzle category
    stdscr.addstr(2, 0, f"Category: {category}", curses.A_BOLD)
    # Display current puzzle state
    stdscr.addstr(4, 0, "Puzzle: " + display_puzzle(puzzle, revealed))
    # Display guessed letters
    stdscr.addstr(6, 0, f"Guessed Letters: {' '.join(sorted(guessed_letters))}")


def main(stdscr):
    """
    Main function to run the Circle of Cash game. It initializes the game, plays rounds, and determines the winner.
    :param stdscr:
    :return:
    """
    players, overall_scores = initialize_game(stdscr)
    used_phrases = set()
    for round_number in range(1, 4):
        round_winner = play_round(stdscr, round_number, players, overall_scores, used_phrases)
        if round_winner is None:
            return
    winner = max(overall_scores, key=overall_scores.get)
    stdscr.addstr(25, 0, f"Game over! The winner is {winner} with ${overall_scores[winner]} points!")
    stdscr.refresh()
    time.sleep(4)

if __name__ == "__main__":
    curses.wrapper(main)