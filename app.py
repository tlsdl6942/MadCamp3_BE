from flask import Flask, request, jsonify
from flask_cors import CORS
from shogi import shogi_bp


app = Flask(__name__)
CORS(app)  # 모든 도메인 허용 (개발용)

app.register_blueprint(shogi_bp)

if __name__ == "__main__":
    app.run(port=5000)
