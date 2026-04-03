"""
Silicon Multiverse — Treasure Hunt Round 3
Flask Backend
"""

import jwt
import datetime as dt
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import psycopg2.errors
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

SECRET = "?^Ec}WTpFlYaGQ#|7_jba4mIN;NT%sI52-l-c]IALglv/-Bn%sJJ6qsy'`7@JF[)%sLnUo!+Q)_r#w3yBOvca_,"


# ─── DB ───────────────────────────────────────────────────────────
def cursorcall():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return conn, cursor


# ─── JWT ──────────────────────────────────────────────────────────
def jwtthing(user_info):
    payload = {
        "id":       str(user_info['id']),
        "username": str(user_info['username']),
        "teamName": str(user_info['teamName']),
        "role":     str(user_info['role']),
        "exp":      int((dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=2)).timestamp())
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")


def decode_token(token):
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


# ─── AUTH DECORATORS ──────────────────────────────────────────────
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"message": "Missing or malformed token."}), 401
        payload = decode_token(auth.split(" ", 1)[1])
        if payload is None:
            return jsonify({"message": "Token invalid or expired."}), 401
        return f(*args, current_user=payload, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if auth == "Bearer admin":
            return f(*args, **kwargs)
        if auth.startswith("Bearer "):
            payload = decode_token(auth.split(" ", 1)[1])
            if payload and payload.get("role") in ("leader", "admin"):
                return f(*args, **kwargs)
        return jsonify({"message": "Admin access required."}), 403
    return decorated


# ─── LOGIN ────────────────────────────────────────────────────────
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"success": False, "message": "Missing credentials."}), 400

    conn, cursor = cursorcall()
    try:
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password_hash = %s",
            (username, password)
        )
        row = cursor.fetchone()
        if row is None:
            return jsonify({"success": False, "message": "Invalid credentials."}), 401

        cursor.execute("SELECT team_name FROM teams WHERE id = %s", (row["team_id"],))
        team_row = cursor.fetchone()

        user_info = {
            "id":       row["id"],
            "username": row["username"],
            "teamName": team_row["team_name"] if team_row else None,
            "role":     row["role"]
        }
        token = jwtthing(user_info.copy())
        return jsonify({"success": True, "token": token, "user": user_info}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ─── HUNT COMPLETE ────────────────────────────────────────────────
@app.route("/api/hunt/complete", methods=["POST"])
@token_required
def hunt_complete(current_user):
    data = request.get_json(silent=True) or {}
    if not data.get("completed"):
        return jsonify({"message": "Nothing to record."}), 400

    conn, cursor = cursorcall()
    try:
        cursor.execute("SELECT id, team_id FROM users WHERE username = %s", (current_user["username"],))
        user = cursor.fetchone()
        if user is None:
            return jsonify({"message": "User not found."}), 404

        # Postgres version of INSERT OR IGNORE
        cursor.execute("""
            INSERT INTO hunt_scores (user_id, team_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (user["id"], user["team_id"]))
        conn.commit()
        return jsonify({"message": "Hunt completion recorded.", "status": "ok"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        conn.close()


# ─── ADMIN: HUNT PROGRESS ─────────────────────────────────────────
@app.route("/api/admin/hunt-progress", methods=["GET"])
@admin_required
def hunt_progress():
    conn, cursor = cursorcall()
    try:
        cursor.execute("""
            SELECT
                t.team_name     AS "teamName",
                hs.completed_at AS "completedAt"
            FROM teams t
            LEFT JOIN hunt_scores hs ON hs.team_id = t.id
            ORDER BY hs.completed_at ASC
        """)
        rows = cursor.fetchall()

        teams = []
        for r in rows:
            finished = r["completedAt"] is not None
            teams.append({
                "teamName":          r["teamName"],
                "completedSections": [1, 2, 3] if finished else [],
                "completedAt":       r["completedAt"],
                "finished":          finished,
            })

        return jsonify({"teams": teams}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        conn.close()


# ─── ADMIN: RESET TEAM ────────────────────────────────────────────
@app.route("/api/admin/reset/<team_name>", methods=["POST"])
@admin_required
def reset_team(team_name):
    conn, cursor = cursorcall()
    try:
        cursor.execute("SELECT id FROM teams WHERE team_name = %s", (team_name,))
        team = cursor.fetchone()
        if team is None:
            return jsonify({"message": "Team not found."}), 404

        cursor.execute("DELETE FROM hunt_scores WHERE team_id = %s", (team["id"],))
        conn.commit()
        return jsonify({"message": f"Team '{team_name}' reset."}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        conn.close()


# ─── HEALTH ───────────────────────────────────────────────────────
"""
@app.route("/api/health", methods=["GET"])
def health():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()  # plain cursor, no RealDictCursor
    try:
        cursor.execute("SELECT COUNT(*) FROM teams")
        count = cursor.fetchone()[0]
        return jsonify({"status": "online", "teams_registered": count}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()
"""

# ─── RUN ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)