from typing import List, Dict
from shogi.models.ShogiModel import PieceType, BoardState, Piece, ShogiPlayer
from .ShogiLogic import PIECE_DIRECTIONS

# ✅ 이동 가능한 위치 반환 (드롭 or 말 이동)
def GetAvailableMoves(player_id: int, piece: str, position: Dict, boardState: BoardState) -> List[List[int]]:
    from_pos = position.get("from")
    to_pos = position.get("to")

    if (to_pos is not None):
        raise ValueError(f"[ShogiService] Invalid request: 'to' should be null for available-moves. Received to={to_pos}")
    if from_pos is not None:
        # 드롭 가능한 위치 계산
        return get_available_move_positions(player_id=player_id, piece=piece, from_pos=from_pos, boardState=boardState)
    elif from_pos is None:
        # 이동 가능한 위치 계산
        return get_available_drop_positions(player_id=player_id, piece=piece, boardState=boardState)

# ✅ 실제 말 이동 처리
def MovePieces(player:ShogiPlayer, player_id:int, piece:str, position:Dict, boardState:BoardState):
    result = False
    capture = {
        "is_capture": False,
        "piece": None
        }
    is_end = False

    from_pos = position["from"]
    to_pos = position["to"]
    if (from_pos is None) or (to_pos is None):
        raise ValueError(f"[ShogiService] Invalid position: There must be 'from', 'to' position to move piece. Received position: from={from_pos}, to={to_pos}")

    # capture 여부 확인
    targetPiece = boardState.board[to_pos[0]][to_pos[1]]
    if (targetPiece.pieceType != PieceType.EMPTY):
        if (targetPiece.owner == player_id):
            raise ValueError(f"[ShogiService] Invalid position: Your piece is already there.")
        
        # 상대 말을 잡는 경우
        capture["is_capture"] = True
        capture["piece"] = targetPiece.pieceType.ToString()
        if (targetPiece.pieceType == PieceType.WANG): # 승리조건1: 왕 잡기
            is_end = True
        
        player.capturedPieces.append(targetPiece.pieceType) # capturedPieces 리스트 업데이트

        # 보드판 업데이트
            # to_pos
        targetPiece.pieceType = PieceType(piece)
        if (player_id==1 and to_pos[1]==3) or (player_id==2 and to_pos[1]==0): # 승리조건2(준비): 상대 진영 들어가기
            targetPiece.stayedTurns = 1 # 카운트 시작
        else:
            targetPiece.stayedTurns = 0
        targetPiece.owner = player_id
            # from_pos
        boardState.board[from_pos[0]][from_pos[1]].pieceType = PieceType.EMPTY
        boardState.board[from_pos[0]][from_pos[1]].stayedTurns = 0
        boardState.board[from_pos[0]][from_pos[1]].owner = 0

        result = True

        return {
            "result": True,
            "capture": capture,
            "is_end": is_end
        }


# ✅ 드롭 처리
def DropPieces(player:ShogiPlayer, player_id:int, piece:str, position:Dict, boardState:BoardState):
    result = False
    matching = next(
        (p for p in player.capturedPieces if p.pieceType == PieceType(piece)),
        None
    )
    if (matching is None): # Drop 하려는 말이 CapturedPieces에 없을 때
        raise ValueError(f"[ShogiService] Invalid Piece: There is no '{piece}' in your captured pieces list.")

    if (position["from"] is not None): # Drop 요청인데 from이 None이 아닐 때
        raise ValueError(f"[ShogiService] Invalid Position: Position['from'] should be None. Received position['from'] = {position["from"]}")

    to_x, to_y = position["to"]
    # 놓으려고 하는 위치가 잘못됐을 때
    if (player_id==1 and to_y[1]==3) or (player_id==2 and to_y[1]==0): # 상대 진영에 놓으려 하는 경우
        raise ValueError(f"[ShogiService] Invalid Position: You cannot drop a piece in the opponent's territory.")
    if (boardState.board[to_x][to_y].pieceType != PieceType.EMPTY): # 말이 있는 곳에 놓으려 하는 경우
        raise ValueError(f"[ShogiService] Invalid Position: That position is already occupied. Received position['to']: {position["to"]}")

    # 보드 업데이트
    targetPiece = boardState.board[to_x][to_y]
    targetPiece.pieceType = PieceType(piece)
    targetPiece.stayedTurns = 0
    targetPiece.owner = player_id

    # capturedPieces 업데이트
    player.capturedPieces.remove(PieceType(piece))

    result = True
    return result

    
# ✅ 말 이동 가능한 좌표 계산 - 상대 말이 있는 곳은 이동할 수 있어야 함.
def get_available_move_positions(player_id: int, piece: str, from_pos: List[int], boardState: BoardState) -> List[List[int]]:
    directions = get_piece_direction(piece=piece, player_id=player_id)
    result = []
    x, y = from_pos

    # 말 종류별 방향 정의 후 위치 계산
    for dx, dy in directions:
        nx, ny = dx+x, dy+y
        if (0 <= nx < 3) and (0 <= ny < 4):
            result.append([nx, ny])

    # 보드 정보와 함께 실제 이동 가능한 좌표 계산
    for x, y in result:
        if (boardState.board[x][y].pieceType != PieceType.EMPTY): # 만약 해당 좌표에 말이 놓여 있다면
            if(boardState.board[x][y].owner == player_id):
                result.remove([x, y])

    return result

def get_piece_direction(piece: str, player_id: int) -> List[tuple[int, int]]:
    directions = PIECE_DIRECTIONS.get(piece)
    if directions is None:
        raise ValueError(f"[ShogiService] Invalid piece type: {piece}")
    
    if player_id == 2:
        directions = [(dx, -dy) for dx, dy in directions] # player2 일 경우 상하 뒤집기
    return directions


# ✅ 드롭 가능한 좌표 계산
def get_available_drop_positions(player_id: int, piece: str, boardState: BoardState) -> List[List[int]]:
    result = []
    for x in range(3):
        for y in range(4):
            if (player_id==1 and y==3) or (player_id==2 and y==0):
                continue

            targetPiece = boardState[x][y]
            if targetPiece.pieceType == PieceType.EMPTY:
                result.append([x, y])

    return result

# ✅ 턴 종료 처리 (타이머 + 턴 교대)
def waitTurn(session_id: int, player_id: int):
    return True

# ✅ 시간 초과 처리
def CallTimeOut(session_id: int, player_id: int):
    # 게임 종료 처리
    # 승자 결정, reason: "timeout"
    pass

# ✅ 승리 조건 검사 (예: 왕 제거 or 왕 도착)
def check_win(boardState: BoardState, currentPlayerId: int) -> bool:
    # 조건 만족 시 True
    return False
