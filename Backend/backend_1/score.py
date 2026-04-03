from flask import request
from teams_creation import cursorcall
import jwt
import os
# This is for saving team scores and shit after quiz completion
# Endpoint: /api/quiz/score
# Type: POST
# Auth: JWT (Handled by login module)
# Request JSON Payload:
# {
#   "score": 8,   // integer — number of correct answers
#   "total": 10   // integer — always 10
# }
# Output/Sent JSON Payload:
# { "message": "Score saved" }
# Authorization: Bearer <token> to be used.
# Let the secret key also be here. I'll implement it as it should be once this shit actually works.
SECRET = "?^Ec}WTpFlYaGQ#|7_jba4mIN;NT%sI52-l-c]IALglv/-Bn%sJJ6qsy'`7@JF[)%sLnUo!+Q)_r#w3yBOvca_,"
#SECRET = os.environ.get("SECRET_KEY")

# Yeah so implemented the try-except thing and just shited this to a new file altogether, fuck the old one. Too many changes to be done, it gets convoluted real fucking fast.
def decodejwt(token):
    try:
        decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# return user was potentially gonna return "None" which breaks SQLite in a nutshell and would've caused a fucking catastrophe. Fixed that.
def is_in_db(cursor, username):
    cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    return user is not None

def getuserid(cursor, username):
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    row = cursor.fetchone()
    if row:
        return row["id"]
    return None

# This also returned nothing so fixed that as well, or else frontend would bitch about it.
# Also teams can't post their scores more than once so added a check for that
def team_score(payload):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return {"success": False, "message": "No token provided"}
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return {"success": False, "message": "Invalid token format"}
    
    token = parts[1].strip()
    userdetails = decodejwt(token)
    
    if userdetails is None:
        return {"success": False, "message": "Invalid or expired token"}
    
    conn, cursor = cursorcall()
    try:
        username = userdetails["username"]
        if not is_in_db(cursor, username):
            return {"success": False, "message": "User not found"}
        userid = getuserid(cursor, username)
        score = payload["score"]
        cursor.execute("SELECT id FROM scores WHERE user_id = %s", (userid,))
        existing = cursor.fetchone()
        if existing:
            return {"success": False, "message": "Score already submitted"}
        cursor.execute("INSERT INTO scores (user_id, score) VALUES (%s, %s)", (userid, score))
        conn.commit()
        return {"success": True, "message": "Score saved"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": str(e)}
    finally:
        conn.close()