from flask import Flask, jsonify, send_from_directory
from livekit.api import AccessToken, VideoGrants
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/token")
def get_token():
    token = AccessToken(
        os.getenv("LIVEKIT_API_KEY"),
        os.getenv("LIVEKIT_API_SECRET")
    ).with_grants(VideoGrants(
        room_join=True,
        room="urdu-assistant"
    )).with_identity("user").to_jwt()

    return jsonify({"token": token})

if __name__ == "__main__":
    app.run(port=5000)