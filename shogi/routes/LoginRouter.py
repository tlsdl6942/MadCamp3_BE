from flask import request, jsonify
from shogi import shogi_bp
from shogi.services.LoginService import make_user


@shogi_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user_name = data["userName"]

    result = make_user(user_name=user_name)

    if result["result"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 400

