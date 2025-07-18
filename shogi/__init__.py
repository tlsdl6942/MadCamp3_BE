from flask import Blueprint

shogi_bp = Blueprint("shogi", __name__, url_prefix="/Shogi")

from . import routes  # 반드시 import 해줘야 라우트 등록됨
