# objects/entities.py
from objects.player import update_player
from objects.lasers import update_lasers, fire_laser, lasers
from objects.enemy import update_enemies, check_collision
from objects.player import player_pos


def update_entities(fire_laser_now=False):
    """
    Update all game entities and handle laser firing.
    :param fire_laser_now:
    :return:
    """
    update_player()
    update_lasers()
    update_enemies()
    check_collision(lasers, player_pos)
    if fire_laser_now:
        # print("[DEBUG] Firing laser from event KEYDOWN")
        fire_laser(player_pos[0], player_pos[1])
