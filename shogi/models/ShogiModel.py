from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict



class PieceType(Enum):
    WANG = "Wang"
    CHANG = "Chang"
    SANG = "Sang"
    JA = "Ja"
    HOO = "Hoo"
    EMPTY = "Empty"


@dataclass
class Piece:
    pieceType: PieceType
    stayedTurns: int # 0 -> 1 -> ok
    owner: int  # 1 or 2 // 0이면 droplist에 있는거


@dataclass
class ShogiPlayer:
    userId: int # 회원가입용 전체 user id
    userName: str
    playerId: int # 게임 세션 내 player1 or 2
    capturedPieces: List[Piece] = field(default_factory=list)


@dataclass
class BoardState:
    board: List[List[Piece]] = field(default_factory=list)
    currPlayerId: int = 1

    def initialize(self):
        width, height = 3, 4
        self.board = [[
            Piece(pieceType=PieceType.EMPTY, stayedTurns=0, owner=0)
            for _ in range(height)
        ] for _ in range(width)]

        # Player 1 (owner 1)
        self.board[0][0] = Piece(pieceType=PieceType.SANG, stayedTurns=0, owner=1)
        self.board[1][0] = Piece(pieceType=PieceType.WANG, stayedTurns=0, owner=1)
        self.board[2][0] = Piece(pieceType=PieceType.CHANG, stayedTurns=0, owner=1)
        self.board[1][1] = Piece(pieceType=PieceType.JA, stayedTurns=0, owner=1)

        # Player 2 (owner 2)
        self.board[2][3] = Piece(pieceType=PieceType.SANG, stayedTurns=0, owner=2)
        self.board[1][3] = Piece(pieceType=PieceType.WANG, stayedTurns=0, owner=2)
        self.board[0][3] = Piece(pieceType=PieceType.CHANG, stayedTurns=0, owner=2)
        self.board[1][2] = Piece(pieceType=PieceType.JA, stayedTurns=0, owner=2)

    # def getPlayerId(self) -> int:
    #     return self.currPlayerId

    
@dataclass
class SessionInfo:
    sessionId: int
    players: Dict[int, ShogiPlayer]  # playerId → ShogiPlayer
    boardState: BoardState = field(default_factory=BoardState)
    currPlayerId: int = 1

    # 방/게임 정보 추가
    is_end: bool = False
    roomName: str = ""
    roomPW: str = ""
    winner: int = None  # 1 or 2
    
    def __post_init__(self):
        self.boardState.initialize()