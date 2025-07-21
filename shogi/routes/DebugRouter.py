# from flask import jsonify
# from shogi import shogi_bp



# @shogi_bp.route("/debug/sessions", methods=["GET"])
# def debug_sessions():
#     from core.session_manager import game_sessions

#     serialized_sessions = {}
#     for session_id, session in game_sessions.items():
#         serialized_sessions[session_id] = {
#             "session_id": session.sessionId,
#             "player1": session.players[1].userName if session.players[1] else None,
#             "player2": session.players[2].userName if session.players[2] else None,
#             "boardState": session.boardState,
#             "currPlayerId": session.currPlayerId,
#             "startSignal": session.startSignal,
#             "is_end": session.is_end,
#             "room_name": session.roomName,
#             "roomPW": session.roomPW,
#             "winner": session.winner
#         }

#     return jsonify(serialized_sessions)

from flask import jsonify
from shogi import shogi_bp
from core.session_manager import game_sessions
from shogi.models.ShogiModel import Piece

def serialize_piece(piece: Piece):
    return {
        "pieceType": piece.pieceType.value,
        "stayedTurns": piece.stayedTurns,
        "owner": piece.owner,
    }

def serialize_board(board):
    return [[serialize_piece(piece) for piece in row] for row in board]

def serialize_session(session):
    return {
        "session_id": session.sessionId,
        "player1_id": session.players.get(1).playerId if session.players.get(1) else None,
        "player2_id": session.players.get(2).playerId if session.players.get(2) else None,
        "boardState": serialize_board(session.boardState.board),
        "currPlayerId": session.currPlayerId,
        "startSignal": session.startSignal,
        "is_end": session.is_end,
        "room_name": session.roomName,
        "roomPW": session.roomPW,
        "winner": session.winner
    }

@shogi_bp.route("/debug/sessions", methods=["GET"])
def debug_sessions():
    serialized_sessions = {
        session_id: serialize_session(session)
        for session_id, session in game_sessions.items()
    }

    return jsonify(serialized_sessions)
