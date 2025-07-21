from typing import List, Dict
from shogi.models.ShogiModel import PieceType, BoardState, Piece, ShogiPlayer, SessionInfo
from core.session_manager import game_sessions
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
def MovePieces(session:SessionInfo, player:ShogiPlayer, player_id:int, piece:str, position:Dict, boardState:BoardState):
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
        capture["piece"] = targetPiece.pieceType.value
        captureWang(session=session, player_id=player_id, captured=targetPiece.pieceType)
        
        targetPiece.owner = player_id
        player.capturedPieces.append(targetPiece) # capturedPieces 리스트 업데이트
        print(f"[DEBUG /MovePieces] capturedPieces: {player.capturedPieces}")

    # 보드판 업데이트
        # to_pos
    targetPiece.pieceType = PieceType(piece)
    targetPiece.stayedTurns = 0
    targetPiece.owner = player_id
        # from_pos
    boardState.board[from_pos[0]][from_pos[1]].pieceType = PieceType.EMPTY
    boardState.board[from_pos[0]][from_pos[1]].stayedTurns = 0
    boardState.board[from_pos[0]][from_pos[1]].owner = 0

    endTurn(session=session, position=position, player_id=player_id, movedPiece=piece)
    if (session.is_end == False): # 왕 잡은게 먼저면 이미 끝
        checkStayWin(session=session)

    result = True

    return {
        "result": result,
        "capture": capture,
        "is_end": session.is_end,
        "winner": session.winner
    }


# ✅ 드롭 처리
def DropPieces(session:SessionInfo, player:ShogiPlayer, player_id:int, piece:str, position:Dict, boardState:BoardState):
    result = False
    matching =(p for p in player.capturedPieces if p.pieceType == str_to_PT(piece))
    
    if (matching is None): # Drop 하려는 말이 CapturedPieces에 없을 때
        # print(f"[DEBUG /DropPieces] capturedPieces: {res}")
        raise ValueError(f"[ShogiService] Invalid Piece: There is no {PieceType(piece)} in your captured pieces list.")
    if (position["from"] is not None): # Drop 요청인데 from이 None이 아닐 때
        raise ValueError(f"[ShogiService] Invalid Position: Position['from'] should be None. Received position['from'] = {position["from"]}")

    to_x, to_y = position["to"]
    # 놓으려고 하는 위치가 잘못됐을 때
    if (player_id==1 and to_y==3) or (player_id==2 and to_y==0): # 상대 진영에 놓으려 하는 경우
        raise ValueError(f"[ShogiService] Invalid Position: You cannot drop a piece in the opponent's territory.")
    if (boardState.board[to_x][to_y].pieceType != PieceType.EMPTY): # 말이 있는 곳에 놓으려 하는 경우
        raise ValueError(f"[ShogiService] Invalid Position: That position is already occupied. Received position['to']: {position["to"]}")

    # 보드 업데이트
    targetPiece = boardState.board[to_x][to_y]
    targetPiece.pieceType = PieceType(piece)
    targetPiece.stayedTurns = 0
    targetPiece.owner = player_id

    # capturedPieces 업데이트
    for captured in player.capturedPieces:
        if captured.pieceType == PieceType(piece):
            player.capturedPieces.remove(captured)
            break  # ✅ 한 개만 제거하고 반복 종료

    endTurn(session=session, position=position, player_id=player_id, movedPiece=piece)
    if (session.is_end == False):
        checkStayWin(session=session)

    result = True
    return {
        "result": result,
        "is_end": session.is_end,
        "winner": session.winner
    }

    
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
    filtered = []
    for x, y in result:
        if(boardState.board[x][y].owner != player_id):
            filtered.append([x, y])
    return filtered

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
            if (player_id==1 and y==3) or (player_id==2 and y==0): # 상대 진영에는 못놓음
                continue

            targetPiece = boardState.board[x][y]
            if targetPiece.pieceType == PieceType.EMPTY: # 비어있는 칸에만 Drop 가능
                result.append([x, y])

    return result


# 승리조건1 (상대 왕 잡기)
def captureWang(session:SessionInfo, player_id:int, captured:PieceType):
    if (captured == PieceType.WANG):
        session.is_end = True
        session.winner = player_id  

# 승리조건2 (내 왕이 상대 진영에서 1턴 버티기) 확인
def checkStayWin(session:SessionInfo):
    result = False
    for x in range(3):  
        piece = session.boardState.board[x][3]
        if (piece.owner==1) and (piece.pieceType==PieceType.WANG) and (piece.stayedTurns == 1):
            session.is_end = True
            session.winner = 1

    for x in range(3): 
        piece = session.boardState.board[x][0]
        if (piece.owner==2) and (piece.pieceType==PieceType.WANG) and (piece.stayedTurns == 1):
            session.is_end = True
            session.winner = 2

    result = True

    return {
        "result": result,
        "is_end": session.is_end,
        "winner": session.winner
    }

            
# ✅ 턴 종료 처리 (last_move 업데이트 & currPlayer 변경)
def endTurn(session:SessionInfo, position:Dict, player_id:int, movedPiece:str):
    session.last_move = {
        "from": position["from"],
        "to": position["to"]
    }
    session.last_moved_piece = movedPiece

    # 상대 진영에 있는 왕의 stayedTurns 증가
    for x in range(3):
        for y in range(4):
            piece = session.boardState.board[x][y]
            if (piece.pieceType == PieceType.WANG) and (piece.owner != player_id):
                if (piece.owner == 1 and y == 3) or (piece.owner == 2 and y == 0):
                    piece.stayedTurns += 1
                else:
                    piece.stayedTurns = 0

    # 다음 플레이어로 턴 넘기기
    session.currPlayerId = 2 if session.currPlayerId==1 else 1


def str_to_PT(value) -> PieceType | None:
    if isinstance(value, PieceType):
        return value
    if isinstance(value, str):
        try:
            return PieceType(value)
        except ValueError:
            print(f"[ERROR] {value} is not a valid PieceType")
    return None
