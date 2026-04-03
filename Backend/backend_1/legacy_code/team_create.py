# This is deprecated. Putting it in legacy codebase for future reference.

import sqlite3
import os
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

def create_team(payload):
    # Path to DB
    db_path = os.path.join(os.path.dirname(__file__), 'master.db')
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON") # Makes SQLite to have foreign keys on every connection
    cursor = conn.cursor()

    # Defining environment variables
    team_name = payload['teamName']
    leader = payload['leaderUsername']
    password = payload['password']
    members = payload['members']


    # Check if team exists
    cursor.execute("SELECT team_id FROM teams WHERE team_name = ?", (team_name,))
    result = cursor.fetchone()
    if result:
        conn.close()
        return { "message": "Team name already taken" }, 409 # HTTP 409 team name exists

    # Insert team
    cursor.execute("INSERT INTO teams (team_name) VALUES (?)", (team_name,))
    team_id = cursor.lastrowid

# The following block might be removed. Commenting it for now.
    """
    # Insert users and link to team
    for username in members:
        cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            conn.close()
            return { "message": "Username already taken" }, 409 # HTTP 409 username already taken
        else:
            cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
            user_id = cursor.lastrowid
        cursor.execute("INSERT INTO team_members (team_id, user_id) VALUES (?, ?)", (team_id, user_id))
    """
    # Adding the Leader
    cursor.execute("SELECT user_id FROM users WHERE username = ?", (payload["leaderUsername"],))
    leader = cursor.fetchone()
    if leader:
        leader_id = leader[0]
        conn.close()
        return { "message": "Username already taken" }, 409 # HTTP 409 username already taken. Same logic for users as well.
    else:
        cursor.execute("INSERT INTO users (username, role) VALUES (?, ?)", (payload["leaderUsername"], "leader"))
        leader_id = cursor.lastrowid
    cursor.execute("INSERT INTO team_members (team_id, user_id, role) VALUES (?, ?, ?)",(team_id, leader_id, "leader"))
    
    # Insert users in users
    for username in members:
        cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            conn.close()
            return { "message": "Username already taken" }, 409 # HTTP 409 username already taken
        else:
            cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
            user_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return { "message": "Team registered successfully" }, 201 # HTTP 201 Success