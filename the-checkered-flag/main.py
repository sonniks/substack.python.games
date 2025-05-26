import pygame
import sys
import json
import math
from core.track import Track
from core.car import PlayerCar, AICar
from core.game import Game


SCREEN_WIDTH, SCREEN_HEIGHT = 640, 520
FPS = 60


def load_circuit(json_path):
    """
    Load the racing circuit data from a JSON file.
    :param json_path:
    :return:
    """
    with open(json_path) as f:
        return json.load(f)


def define_args():
    """
    Define command line arguments for the script.
    :return:
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("circuit", help="Path to racing circuit JSON file")
    return parser.parse_args()


def show_text_centered(text, color, delay_ms=0, y_offset=0):
    """
    Display text centered on the screen with a shadow effect.
    :param text:
    :param color:
    :param delay_ms:
    :param y_offset:
    :return:
    """
    font = pygame.font.SysFont("Arial", 36, bold=True)
    shadow = font.render(text, True, (0, 0, 0))
    label = font.render(text, True, color)
    surface = pygame.display.get_surface()
    rect = label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    surface.blit(shadow, (rect.x + 2, rect.y + 2))
    surface.blit(label, rect)
    pygame.display.flip()
    if delay_ms:
        pygame.time.wait(delay_ms)


def run_track(track_info):
    """
    Run a single track with the given track information.
    :param track_info:
    :return:
    """
    track = Track(track_info["mask"], track_info["laps"])
    player, ai_cars = initialize_cars(track)
    engine_sound = pygame.mixer.Sound("assets/sounds/engine_loop.wav")
    engine_sound.set_volume(4.5)
    engine_playing = False
    crash_sound = pygame.mixer.Sound("assets/sounds/crash.wav")
    crash_sound.set_volume(0.6)  # tweak to taste
    game = Game(track, player, ai_cars)
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_q
            ):
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            if not engine_playing:
                engine_sound.play(-1)
                engine_playing = True
        else:
            if engine_playing:
                engine_sound.stop()
                engine_playing = False
        game.update(pygame.mouse.get_pos(), pygame.mouse.get_pressed())
        screen = pygame.display.get_surface()
        screen.fill((0, 0, 0))
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
        if game.check_race_complete():
            if engine_playing:
                engine_sound.stop()
                engine_playing = False
            if player.lap_count >= track.laps_required:
                show_text_centered("Player Wins!", (255, 255, 0), 2000, y_offset=-40)
            else:
                winner = next(ai for ai in ai_cars if ai.lap_count >= track.laps_required)
                show_text_centered(f"AI {winner.index} Wins!", (255, 255, 0), 2000, y_offset=-40)
            running = False


def initialize_cars(track):
    """
    Initialize the player and AI cars based on the track's spawn and start lines.
    :param track:
    :return:
    """
    gx, gy = zip(*track.spawn_line_pixels)
    spawn_x = sum(gx) // len(gx)
    spawn_y = sum(gy) // len(gy)
    sx, sy = zip(*track.start_line_pixels)
    sfx = sum(sx) // len(sx)
    sfy = sum(sy) // len(sy)
    dx = sfx - spawn_x
    dy = sfy - spawn_y
    initial_angle = math.degrees(math.atan2(-dy, dx)) - 90
    player = PlayerCar((spawn_x, spawn_y), track.waypoints)
    player.angle = initial_angle
    ai_cars = []
    for i in range(4):
        offset = (i - 1.5) * 25
        angle_rad = math.radians(initial_angle + 90)
        ox = spawn_x + math.cos(angle_rad) * offset
        oy = spawn_y - math.sin(angle_rad) * offset
        debug = (i == 0)
        ai = AICar((ox, oy), track.waypoints, track, i, debug_this_ai=debug)
        ai.angle = initial_angle
        ai_cars.append(ai)
    return player, ai_cars


def end_of_circuit_prompt():
    """
    Prompt the user at the end of the circuit series to either restart or quit.
    :return:
    """
    show_text_centered("Series Complete! (R)estart or (Q)uit", (255, 255, 255), 2000,40)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                    return
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


def main():
    """
    Main function to initialize the game, load the circuit, and run the tracks.
    :return:
    """
    args = define_args()
    pygame.init()
    pygame.mixer.init()
    try:
        pygame.mixer.music.load("assets/sounds/music.mod")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.2)
    except pygame.error as e:
        print(f"Failed to load music: {e}")
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("The Checkered Flag")
    circuit_data = load_circuit(args.circuit)
    for i, track_info in enumerate(circuit_data):
        run_track(track_info)
        if i < len(circuit_data) - 1:
            show_text_centered("Next Course!", (255, 255, 255), 2000)

    end_of_circuit_prompt()


if __name__ == "__main__":
    main()
