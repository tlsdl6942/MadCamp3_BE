from flask import request, jsonify
from shogi import shogi_bp
from shogi.models.ShogiModel import SessionInfo, ShogiPlayer
from core.session_manager import game_sessions, room_map, start_game
from shogi.services.RoomService import create_new_room, join_room, check_ready
import itertools


@shogi_bp.route("/create-room", methods=["POST"])
def create_room():
    data = request.get_json()
    user_id = data["user_id"]
    room_name = data["roomName"]
    game = data.get("game", "shogi")

    result = create_new_room(user_id, room_name, game)
    if result["result"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 400
    

@shogi_bp.route("/enter-room", methods=["POST"])
def enter_room():
    data = request.get_json()
    user_id = data["user_id"]
    room_name = data["roomName"]
    room_pw = data["roomPW"]

    result = join_room(user_id, room_name, room_pw)
    if result["result"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@shogi_bp.route("/ready", methods=["POST"])
def ready():
    data = request.get_json()
    session_id = data["session_id"]
    player_id = data["player_id"]

    result = check_ready(session_id, player_id)
    if result["result"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 400
    

@shogi_bp.route("/debug/sessions", methods=["GET"])
def debug_sessions():
    from core.session_manager import game_sessions

    serialized_sessions = {}
    for session_id, session in game_sessions.items():
        serialized_sessions[session_id] = {
            "player1": session.player1.userName if session.player1 else None,
            "player2": session.player2.userName if session.player2 else None,
            "isReady1": session.readyFlags.get(1, False),
            "isReady2": session.readyFlags.get(2, False),
            "startSignal": session.startSignal,
        }

    return jsonify(serialized_sessions)
