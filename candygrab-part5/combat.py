# combat.py

import pygame
from fire import FireBeam
from scanner import NON_ELIGIBLE
from movement import get_tile_position
from tilemap import player_cell
from logger import conlog
from constants import *


def handle_firing(player, map_data, villains, beams, now_ms, hud):
    """
    Handle the player's firing action: create a beam, apply damage to villains, update score.
    :param player:
    :param map_data:
    :param villains:
    :param beams:
    :param now_ms:
    :param hud:
    :return:
    """
    allowed = player_cell(map_data, player) not in NON_ELIGIBLE
    if hasattr(player, "can_fire"):
        allowed = allowed and player.can_fire(map_data)
    if not allowed:
        return
    beam = FireBeam(player, now_ms)
    newly_disabled = beam.apply_damage_once(villains, map_data, player, now_ms) or 0
    if newly_disabled:
        gained = 100 * newly_disabled
        hud.score += gained
        conlog(f"[Combat] Disabled {newly_disabled} robot(s); +{gained} points. Total={hud.score}")
    beams.append(beam)
    global FIRE_SOUND
    if FIRE_SOUND is None:
        FIRE_SOUND = pygame.mixer.Sound("assets/sounds/ghost-neutron.wav")
        FIRE_SOUND.set_volume(0.5)
    FIRE_SOUND.play()


def check_and_trigger_player_death(player, villains, map_data, now_ms):
    """
    Check if the player is colliding with any villains and trigger death if so.
    :param player:
    :param villains:
    :param map_data:
    :param now_ms:
    :return:
    """
    if getattr(player, "is_dying", lambda: False)() or getattr(player, "is_invulnerable", lambda _t: False)(now_ms):
        return
    if player_cell(map_data, player) in NON_ELIGIBLE:
        return
    pcx, pcy = get_tile_position(player)
    for v in villains:
        if getattr(v, "is_disabled", lambda: False)():
            continue
        vcx, vcy = get_tile_position(v)
        if vcx == pcx and vcy == pcy:
            player.start_death(now_ms)
            break
