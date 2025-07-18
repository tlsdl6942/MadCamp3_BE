from flask import request, jsonify
from shogi import shogi_bp
from shogi.models.ShogiModel import SessionInfo, ShogiPlayer
from core.session_manager import game_sessions
from shogi.services.ShogiService import GetAvailableMoves, MovePieces, UpdateBoard
import itertools

# 세션 ID 자동 증가
session_id_counter = itertools.count(1)

@shogi_bp.route("/create-session", methods=["POST"])
def create_session():
    ##
    pass


@shogi_bp.route("/available-moves", methods=["POST"])
def avaiable_moves():
    data = request.get_json()
    '''{
        "session_id": 1,
        "player_id": 1, (1 or 2)
        "piece": "Chang",
        "position": {
            "from": [1, 0],
            "to": null
            }
        }'''
    session_id = data["session_id"]
    player_id = data["player_id"]
    piece = data["piece"]
    position = data["position"] # 만약 AttributeError 터지면 position 정보를 req에서 못받은거

    session = game_sessions.get(session_id)

    if not session: # 요청한 세션이 없을 경우(존재하지 않는 게임에서의 요청 방지)
        return jsonify({"result": False, "error": "Invalid session ID"}), 400 

    boardState = session.boardState # 해당 게임의 보드판
    player = session.players.get(player_id) # 요청을 보낸 플레이어 객체
    if not player: # 유효하지 않은 플레이어
        return jsonify({"result": False, "error": "Invalid player ID"}), 400

    try:
        moves = GetAvailableMoves(player, piece, position, boardState)
        return jsonify({"result": True, "moves": moves}), 200
    except Exception as e:
        return jsonify({"result": False, "error": str(e)}), 500
    

@shogi_bp.route("/move", methods=["POST"])
def move():
    data = request.get_json()
    session_id = data["session_id"]
    player_id = data["player_id"]
    piece = data["piece"]
    position = data["position"] # 만약 AttributeError 터지면 position 정보를 req에서 못받은거

    session = game_sessions.get(session_id)

    if not session: # 요청한 세션이 없을 경우(존재하지 않는 게임에서의 요청 방지)
        return jsonify({"result": False, "error": "Invalid session ID"}), 400 

    boardState = session.boardState # 해당 게임의 보드판
    player = session.players.get(player_id) # 요청을 보낸 플레이어 객체
    dropState = player.capturedPieces # 요청을 보낸 플레이어의 dropState
    if not player: # 유효하지 않은 플레이어
        return jsonify({"result": False, "error": "Invalid player ID"}), 400

    try:
        res = MovePieces(player, piece, position, boardState)
        capture = res.get("capture")  # dict: { is_capture: bool, piece: str|null }
        is_end = res.get("is_end")    # bool
        UpdateBoard(player, piece, position, boardState, dropState)
        return jsonify({
            "result": True, 
            "capture": capture,
            "is_end": is_end
        }), 200
    except Exception as e:
        return jsonify({"result": False, "error": str(e)}), 500
    

@shogi_bp.route("/available-drop", methods=["POST"])
def available_drop():
    data = request.get_json()
    session_id = data["session_id"]
    player_id = data["player_id"]
    piece = data["piece"]
    position = data["position"]

    session = game_sessions.get(session_id)

    if not session: # 요청한 세션이 없을 경우(존재하지 않는 게임에서의 요청 방지)
        return jsonify({"result": False, "error": "Invalid session ID"}), 400 

    boardState = session.boardState # 해당 게임의 보드판
    player = session.players.get(player_id) # 요청을 보낸 플레이어 객체

    if not player: # 유효하지 않은 플레이어
        return jsonify({"result": False, "error": "Invalid player ID"}), 400

    try:
        moves = GetAvailableMoves(player, piece, position, boardState)
        return jsonify({"result": True, "moves": moves}), 200

    except Exception as e:
        return jsonify({"result": False, "error": str(e)}), 500
    

@shogi_bp.route("/drop", methods=["POST"])
def drop():
    data = request.get_json()
    session_id = data["session_id"]
    player_id = data["player_id"]
    piece = data["piece"]
    position = data["position"] # 만약 AttributeError 터지면 position 정보를 req에서 못받은거

    session = game_sessions.get(session_id)

    if not session: # 요청한 세션이 없을 경우(존재하지 않는 게임에서의 요청 방지)
        return jsonify({"result": False, "error": "Invalid session ID"}), 400 

    boardState = session.boardState # 해당 게임의 보드판
    player = session.players.get(player_id) # 요청을 보낸 플레이어 객체
    dropState = player.capturedPieces # 요청을 보낸 플레이어의 dropState
    if not player: # 유효하지 않은 플레이어
        return jsonify({"result": False, "error": "Invalid player ID"}), 400

    try:
        UpdateBoard(player, piece, position, boardState, dropState)
        return jsonify({
            "result": True, 
        }), 200
    except Exception as e:
        return jsonify({"result": False, "error": str(e)}), 500
    