from typing import Dict
from shogi.models.ShogiModel import SessionInfo as ShogiSession

# 앞으로 Shogi, Poker, Othello 등의 게임 세션을 다 여기에 저장
game_sessions: Dict[int, object] = {}
