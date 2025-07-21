from flask import request, jsonify
from shogi import shogi_bp
from shogi.models.ShogiModel import SessionInfo, ShogiPlayer
from core.session_manager import game_sessions
from shogi.services.ShogiService import GetAvailableMoves, MovePieces, DropPieces
import itertools

# 세션 ID 자동 증가
session_id_counter = itertools.count(1)


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
        return jsonify({"result": True, "moves": None}), 400 

    boardState = session.boardState # 해당 게임의 보드판
    player = session.players.get(player_id) # 요청을 보낸 플레이어 객체
    if not player: # 유효하지 않은 플레이어
        return jsonify({"result": True, "moves": None}), 400

    try:
        moves = GetAvailableMoves(player_id, piece, position, boardState)
        return jsonify({"result": True, "moves": moves}), 200
    except Exception as e:
        print(f"[DEBUG /available-move] request: {data}")
        print(f"[DEBUG /available-move] response: {moves}")
        return jsonify({"result": True, "moves": None}), 500
    

@shogi_bp.route("/move", methods=["POST"])
def move():
    data = request.get_json()
    session_id = data["session_id"]
    player_id = data["player_id"]
    piece = data["piece"]
    position = data["position"] # 만약 AttributeError 터지면 position 정보를 req에서 못받은거

    session = game_sessions.get(session_id)

    if not session: # 요청한 세션이 없을 경우(존재하지 않는 게임에서의 요청 방지)
        return jsonify({
            "result": True, 
            "capture": None,
            "is_end": session.is_end,
            "winner": session.winner
        }), 400 

    boardState = session.boardState # 해당 게임의 보드판
    player = session.players.get(player_id) # 요청을 보낸 플레이어 객체
    dropState = player.capturedPieces # 요청을 보낸 플레이어의 dropState
    if not player: # 유효하지 않은 플레이어
        return jsonify({
            "result": True, 
            "capture": None,
            "is_end": session.is_end,
            "winner": session.winner
        }), 400

    try:
        res = MovePieces(session=session, player=player, player_id=player_id, piece=piece, position=position, boardState=boardState)
        capture = res.get("capture")  # dict: { is_capture: bool, piece: str|null }
        return jsonify({
            "result": True, 
            "capture": capture,
            "is_end": session.is_end,
            "winner": session.winner
        }), 200
    except Exception as e:
        print(f"[DEBUG /move] request: {data}")
        print(f"[DEBUG /move] response: {res}")
        return jsonify({
            "result": True, 
            "capture": None,
            "is_end": session.is_end,
            "winner": session.winner
        }), 500
    

@shogi_bp.route("/available-drop", methods=["POST"])
def available_drop():
    data = request.get_json()
    session_id = data["session_id"]
    player_id = data["player_id"]
    piece = data["piece"]
    position = data["position"]

    session = game_sessions.get(session_id)

    if not session: # 요청한 세션이 없을 경우(존재하지 않는 게임에서의 요청 방지)
        return jsonify({"result": True, "moves": None}), 400 

    boardState = session.boardState # 해당 게임의 보드판
    player = session.players.get(player_id) # 요청을 보낸 플레이어 객체

    if not player: # 유효하지 않은 플레이어
        return jsonify({"result": True, "moves": None}), 400

    try:
        moves = GetAvailableMoves(player_id, piece, position, boardState)
        return jsonify({"result": True, "moves": moves}), 200

    except Exception as e:
        print(f"[DEBUG /available-move] request: {data}")
        print(f"[DEBUG /available-move] response: {moves}")
        return jsonify({"result": True, "moves": None}), 500
    

@shogi_bp.route("/drop", methods=["POST"])
def drop():
    data = request.get_json()
    session_id = data["session_id"]
    player_id = data["player_id"]
    piece = data["piece"]
    position = data["position"] # 만약 AttributeError 터지면 position 정보를 req에서 못받은거

    session = game_sessions.get(session_id)

    if not session: # 요청한 세션이 없을 경우(존재하지 않는 게임에서의 요청 방지)
        return jsonify({
            "result": True, 
            "is_end": session.is_end,
            "winner": session.winner
        }), 400 

    boardState = session.boardState # 해당 게임의 보드판
    player = session.players.get(player_id) # 요청을 보낸 플레이어 객체
    dropState = player.capturedPieces # 요청을 보낸 플레이어의 dropState
    if not player: # 유효하지 않은 플레이어
        return jsonify({
            "result": True, 
            "is_end": session.is_end,
            "winner": session.winner
        }), 400

    try:
        res = DropPieces(session=session, player=player, player_id=player_id, piece=piece, position=position, boardState=boardState)
        return jsonify({
            "result": True, 
            "is_end": session.is_end,
            "winner": session.winner
        }), 200
    except Exception as e:
        print(f"[DEBUG /move] request: {data}")
        print(f"[DEBUG /move] response: {res}")
        return jsonify({
            "result": True, 
            "is_end": session.is_end,
            "winner": session.winner
        }), 500
    