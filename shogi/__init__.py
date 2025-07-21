from flask import Blueprint

shogi_bp = Blueprint("shogi", __name__, url_prefix="/Shogi")

from . import routes  # 반드시 import 해줘야 라우트 등록됨
from shogi.routes import RoomRouter
from shogi.routes import ShogiRouter
from shogi.routes import DebugRouter
from shogi.routes import TurnRouter
from shogi.routes import LoginRouter