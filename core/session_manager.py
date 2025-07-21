from typing import Dict
from typing import Union
from shogi.models.ShogiModel import SessionInfo as ShogiSession

# 앞으로 Shogi, Poker, Othello 등의 게임 세션을 다 여기에 저장
game_sessions: Dict[int, Union[ShogiSession]] = {}  # session_id -> SessionInfo
room_map: Dict[str, int] = {}  # roomName -> session_id
user_map: Dict[int, str] = {}  # user_id -> userName