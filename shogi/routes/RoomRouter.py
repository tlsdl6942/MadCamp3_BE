from flask import request, jsonify
from shogi import shogi_bp
from shogi.services.RoomService import create_new_room, join_room, check_ready, delete_room


@shogi_bp.route("/create-room", methods=["POST"])
def create_room():
    data = request.get_json()
    user_id = data["user_id"]
    room_name = data["roomName"]
    game = data.get("game", "shogi")

    result = create_new_room(user_id=user_id, room_name=room_name, game=game)
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

    result = join_room(user_id=user_id, roomName=room_name, roomPW=room_pw)
    if result["result"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@shogi_bp.route("/ready", methods=["POST"])
def ready():
    data = request.get_json()
    session_id = data["session_id"]
    player_id = data["player_id"]

    result = check_ready(session_id=session_id, player_id=player_id)
    if result["result"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 400
    

@shogi_bp.route("/delete-room", methods=["POST"])
def delelt_room():
    data = request.get_json()
    session_id = data["session_id"]

    result = delete_room(session_id)
    if [result["result"]]:
        return jsonify(result), 200
    else:
        return jsonify(result), 400
