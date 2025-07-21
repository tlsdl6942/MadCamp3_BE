# TurnRouter.py
from flask import request, jsonify
from shogi import shogi_bp
from shogi.services.TurnService import wait, timeout


@shogi_bp.route("/wait-turn", methods=["POST"])
def wait_turn_route():
    data = request.get_json()
    session_id = data.get("session_id")
    player_id = data.get("player_id")

    try:
        result = wait(session_id=session_id, player_id=player_id)
        return jsonify({
            "result": True,
            "turn": result["turn"],
            "op_position": result["op_position"],
            "is_end": result["is_end"],
            "winner": result["winner"]
        }), 200
    except Exception as e:
        return jsonify({
            "result": True,
            "turn": result["turn"],
            "op_position": result["op_position"],
            "is_end": result["is_end"],
            "winner": result["winner"]
        }), 500


@shogi_bp.route("/timeout", methods=["POST"])
def timeout_route():
    data = request.get_json()
    session_id = data.get("session_id")
    player_id = data.get("player_id")

    try:
        result = timeout(session_id=session_id, player_id=player_id)
        return jsonify({
            "result": result["result"],
            "is_end": result["is_end"],
            "winner": result["winner"]
        }), 200
    except Exception as e:
        return jsonify({
            "result": True,
            "is_end": result["is_end"],
            "winner": result["winner"]
            # "error": str(e)
        }), 500
