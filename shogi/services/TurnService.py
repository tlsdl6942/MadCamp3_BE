# TurnService.py
from core.session_manager import game_sessions
# from models.ShogiModel import PieceType, BoardState, Piece, ShogiPlayer, SessionInfo
from shogi.services.ShogiService import checkStayWin

def wait(session_id: int, player_id: int):
    session = game_sessions.get(session_id)
    if not session:
        raise ValueError("Invalid session ID")

    is_turn = (session.currPlayerId == player_id)

    if (is_turn): # 내 턴 돌아왔을 때
        checkStayWin(session=session) # 승리조건2: 왕이 1턴 이상 상대 진영에 머물렀는지 확인


    return {
        "result": True,
        "turn": is_turn,
        "op_position": session.last_move,
        "op_piece": session.last_moved_piece,
        "is_end": session.is_end,
        "winner" : session.winner
    }


def timeout(session_id: int, player_id: int):
    session = game_sessions.get(session_id)
    if not session:
        raise ValueError("Invalid session ID")

    session.is_end = True
    session.winner = 2 if player_id == 1 else 1  # 상대방이 승리

    session.last_move["from"] = None
    session.last_move["to"] = None
    session.last_moved_piece = "Empty"

    return {
        "result": True,
        "is_end": True,
        "winner": session.winner
    }
