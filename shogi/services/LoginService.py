import time
import random
import string

from shogi.models.ShogiModel import SessionInfo, ShogiPlayer, BoardState
from core.session_manager import game_sessions, room_map, user_map
import itertools

user_id_counter = itertools.count(1)

def make_user(user_name:str):
    user_id = next(user_id_counter)
    user_map[user_id] = user_name

    return {
        "result": True,
        "user_id": user_id,
        "user_name": user_name
    }