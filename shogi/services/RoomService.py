import time
import random
import string

from shogi.models.ShogiModel import SessionInfo, ShogiPlayer, BoardState
from core.session_manager import game_sessions, room_map, start_game
import itertools


session_id_counter = itertools.count(1)

def generate_room_pw(length: int = 6) -> str:
    chars = string.ascii_uppercase + string.digits  # A-Z + 0-9
    return ''.join(random.choices(chars, k=length))


def create_new_room(user_id: int, room_name: str, room_pw: str = "", game: str = "shogi"):
    if room_name in room_map:
        return {"result": False, "error": "Room name already exists"}
    
    session_id = next(session_id_counter)
    room_pw = generate_room_pw()

    player = ShogiPlayer(userId=user_id, userName=f"Player{user_id}", playerId=1) # username 설정 확인
    board = BoardState()
    board.initialize()

    session = SessionInfo(
        sessionId=session_id,
        players={1: player},
        boardState=board,
        currPlayerId=1,
        is_end=False,
        roomName=room_name,
        roomPW=room_pw,
        winner=None
    )

    game_sessions[session_id] = session
    room_map[room_name] = session_id
    start_game[session_id] = False

    return {
        "result": True,
        "session_id": session_id,
        "player_id": 1,
        "roomName": room_name,
        "roomPW": room_pw
    }


def join_room(user_id, roomName, roomPW):
    if roomName not in room_map:
        return {"result": False, "error": "Room not found"}

    session_id = room_map[roomName]
    session = game_sessions[session_id]

    if session.roomPW != roomPW:
        return {"result": False, "error": "Incorrect room password"}

    if len(session.players) >= 2:
        return {"result": False, "error": "Room is full"}

    player_id = 2
    player = ShogiPlayer(userId=user_id, userName=f"Player{user_id}", playerId=player_id)
    session.players[player_id] = player

    # 게임 시작 신호 표시
    start_game[session_id] = True

    return {
        "result": True,
        "session_id": session_id,
        "player_id": player_id,
        "startSignal": True
    }


def check_ready(session_id: int, player_id: int, timeout: int = 20):
    # 세션 존재 여부 확인
    if session_id not in game_sessions:  
        return {"result": False, "error": "Invalid session ID"}

    # player_id가 1이 아닌 경우 요청 거부
    if player_id != 1:
        return {"result": False, "error": "Only Player 1 should call /ready"}
    
    # Long Poll: timeout 동안 반복 확인
    wait_time = 0
    poll_interval = 1  # 1초마다 확인

    while wait_time < timeout:
        if start_game.get(session_id, False):
            return {
                "result": True,
                "startSignal": True
            }
        time.sleep(poll_interval)
        wait_time += poll_interval

    # 아직 시작 안 됐을 경우
    return {
        "result": True,
        "startSignal": False
    }