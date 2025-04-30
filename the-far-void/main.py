# main.py
import pygame
from core.engine import run_game


def main():
    """
    Main function to initialize the game and run the main loop.
    :return:
    """
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2)
    while True:
        result = run_game()
        if result == "quit" or result is None:
            break
        elif result == "restart":
            print("[DEBUG] Game restarted")
            continue

    pygame.quit()


if __name__ == "__main__":
    main()
