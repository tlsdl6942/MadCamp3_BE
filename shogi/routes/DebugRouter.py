from flask import jsonify
from shogi import shogi_bp



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
