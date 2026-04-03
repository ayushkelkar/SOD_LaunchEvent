# This is the main module for everything in this server.
# This handles all master I/O for the event backend.
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from teams_creation import create_team
from login import team_login
from score import team_score
from leaderboard import leaderboards
from admin import get_users, set_quiz_status, get_status

app = Flask(__name__)
CORS(app)

@app.route('/api/auth/register', methods=['POST'])
def teams_create():
    payload = request.get_json()
    result = create_team(payload)
    return jsonify(result)

@app.route('/api/auth/login', methods=['POST'])
def login():
    payload = request.get_json()
    result = team_login(payload)
    status_code = 200 if result.get("success") else 401
    return jsonify(result), status_code

@app.route('/api/admin/quiz-status', methods=['POST'])
def toggle():
    payload = request.get_json()
    enabled = payload.get("enabled", False)
    result = set_quiz_status(enabled)
    return jsonify(result)

@app.route('/api/quiz/score', methods=['POST'])
def score():
    payload = request.get_json()
    result = team_score(payload)
    return jsonify(result)

@app.route('/api/leaderboard', methods=['GET'])
def leaderboard_main():
    result = leaderboards()
    return jsonify(result)

@app.route('/api/admin/users', methods=['GET'])
def admin_users():
    result = get_users()
    return jsonify(result)

@app.route('/api/quiz/status', methods=['GET'])
def status():
    return jsonify(get_status())

# Gunicorn imports the `app` object directly, so no app.run() needed.
# This block is only kept for optional local dev use.
if __name__ == '__main__':
    app.run(debug=True)