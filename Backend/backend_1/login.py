from teams_creation import cursorcall
import jwt
import datetime
import os
# This module will handle the team login.
# Endpoint: /api/auth/login
# Type: POST
# JSON Payload Example:
# {
#   "username": "qwolf_lead",
#   "password": "plaintext123"
# }

# If Successful, should send the following payload:
# {
#   "token": "eyJhbGciOiJIUzI1NiJ9...",
#   "user": {
#   "id": 1,
#   "username": "qwolf_lead",
#   "teamName": "Quantum Wolves",   // camelCase — not team_name
#   "role":     "leader"
#           }
# }

# So login works with valid credentials. However, login with invalid credentials is messy, doesn't work right, and kind of weird. Will see later.

# 30-03-2026 21:10 - Trying try-except for invalid login thing. Will see if it works.

SECRET = "?^Ec}WTpFlYaGQ#|7_jba4mIN;NT%sI52-l-c]IALglv/-Bn%sJJ6qsy'`7@JF[)%sLnUo!+Q)_r#w3yBOvca_,"

#SECRET = os.environ.get("SECRET_KEY")

def teams_check(cursor, username, password):
    print(f"Checking: username='{username}' password='{password}'")
    cursor.execute("SELECT * FROM users WHERE username = %s AND password_hash = %s", (username, password))
    row = cursor.fetchone()
    print(f"Row found: {row}")
    if row == None:
        return None
    teamid = row["team_id"]
    cursor.execute("SELECT team_name FROM teams WHERE id = %s", (teamid,))
    teamsrow = cursor.fetchone()
    user_info = {
        "id": row["id"],
        "username": row["username"],
        "teamName": teamsrow["team_name"] if teamsrow else None,
        "role": row["role"]
        }
    return user_info

def jwtthing(payload):
    import datetime as dt
    d1 = {
        "id": str(payload['id']),
        "username": str(payload['username']),
        "teamName": str(payload['teamName']),
        "role": str(payload['role']),
        "exp": int((dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=2)).timestamp())
    }
    print(f"JWT payload: {d1}")
    token = jwt.encode(d1, SECRET, algorithm="HS256")
    return token

# Yeah so why login was working with invalid creds was that jwtthing was called before checking if the user existed.
# Also, using payload for building the JWT is quite dangerous, so applied a different shit, user_info for that instead.
def team_login(payload):
    username = payload.get('username')
    password = payload.get('password')
    
    if not username or not password:
        return {"success": False, "message": "Missing credentials"}
    
    conn, cursor = cursorcall()
    try:
        user_info = teams_check(cursor, username, password)
        print(f"user_info: {user_info}")
        if user_info is None:
            return {"success": False, "message": "Invalid credentials"}
        token = jwtthing(user_info.copy())  # Pass user_info, NOT raw payload. Never put passwords in a JWT.
        return {
            "success": True,
            "token": token,
            "user": user_info
        }
    except Exception as e:
        print(f"Exception: {e}")
        return {"success": False, "message": str(e)}
    finally:
        conn.close()