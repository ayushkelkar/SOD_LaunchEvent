# This is deprecated. Putting it in legacy codebase for future reference.

from flask_main import request
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
# SECRET_KEY = "I don't know what the hell to put here"
SECRET = os.environ.get("SECRET_KEY")
# The following function is a prototype for exception handling. I don't know try-except, so its commented out. I won't use this for now.
"""
def decodejwt(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
        print(decoded)
    except jwt.InvalidTokenError:
        decoded = None  # invalid token at all
        is_expired = True  # treat invalid as expired / not valid
    else:
        # check expiration manually
        exp = decoded.get("exp")
        if exp is None or exp < int(time.time()):
            is_expired = True
        else:
            is_expired = False
    return is_expired
"""

# WHY IS THIS SECRET GIVING PYLANCE ISSUES???
def decodejwt(token):
    decoded = jwt.decode(token, SECRET, algorithms=["HS256"]) # type: ignore <-- Keep this. Shuts up Pylance
    # So now we have the original payload that flask gets I guess.
    return decoded

# Will check if the username is present in the users table. Not exactly good compared to using jwt implementations, but it works, barely.
def is_in_db(cursor, username):
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if(user["username"] == username):
        return True
    else:
        return False

def getuserid(cursor, username):
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if row:
        userid = row["id"]
        print(userid)
        return userid

def team_score(payload):
    auth_header = request.headers.get("Authorization")
    print(auth_header)
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1].strip()  # this is the actual JWT
            print(token)
        else:
            token = None
    else:
        token = None
    userdetails = decodejwt(token)
    conn, cursor = cursorcall()
    username  = userdetails["username"]
    userid = getuserid(cursor, username)
    yesorno = is_in_db(cursor, username) # So this is the authentication part. True if user exists in the db, False otherwise.
    if yesorno is True:
        score = payload["score"]
        cursor.execute("INSERT INTO scores (user_id, score) VALUES (?, ?)", (userid, score))
        conn.commit()