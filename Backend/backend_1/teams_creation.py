# This is for creating a team for the event
# Endpoint Details:
"""
Type: POST
Endpoint: /api/auth/register

JSON Payload Example:
{
  "teamName":       "Quantum Wolves",
  "leaderUsername": "qwolf_lead",
  "password":       "plaintext123",   // backend hashes with bcrypt
  "members":        ["Alice", "Bob"]  // optional, can be empty array
}

"""

import psycopg2
import psycopg2.extras
import psycopg2.errors
import os
from dotenv import load_dotenv
load_dotenv()

def cursorcall():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return conn, cursor

def insert_teams(cursor, payload):
    cursor.execute("INSERT INTO teams (team_name) VALUES (%s) RETURNING id", (payload['teamName'],))
    teamid = cursor.fetchone()["id"]
    return teamid

def insert_users(cursor, payload, teamid):
    user_ids = []
    cursor.execute("INSERT INTO users (username, password_hash, team_id, role) VALUES (%s, %s, %s, %s) RETURNING id", (payload['leaderUsername'], payload['password'], teamid, 'leader'))
    user_ids.append(cursor.fetchone()["id"])
    for username in payload['members']:
        cursor.execute("INSERT INTO users (username, password_hash, team_id) VALUES (%s, %s, %s) RETURNING id", (username, None, teamid))
        user_ids.append(cursor.fetchone()["id"])
    return user_ids

def insert_members(cursor, all_team_members, teamid):
    member_ids = []
    for name in all_team_members:
        cursor.execute("INSERT INTO members (name, team_id) VALUES (%s, %s) RETURNING id", (name, teamid))
        member_ids.append(cursor.fetchone()["id"])
    return member_ids

def create_team(payload):
    conn, cursor = cursorcall()
    try:
        teamid = insert_teams(cursor, payload)
        user_ids = insert_users(cursor, payload, teamid)
        all_team_members = [payload['leaderUsername']] + payload['members']
        member_ids = insert_members(cursor, all_team_members, teamid)
        conn.commit()
        return {"success": True, "message": "Team created successfully", "team_id": teamid}
    except psycopg2.errors.UniqueViolation as e:
        conn.rollback()
        return {"success": False, "message": "Team name or username already exists"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": str(e)}
    finally:
        conn.close()