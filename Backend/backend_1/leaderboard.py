from teams_creation import cursorcall
# So this is the module for the leaderboards thing.
# Endpoint: /api/leaderboard
# Type: GET
# The JSON Payload looks like this: It is a list of dictionaries
# {
#   "leaderboard": [
#     { "teamName": "Quantum Wolves", "score": 9, "total": 10, "game": "quiz" },
#     { "teamName": "Photon Force",   "score": 7, "total": 10, "game": "quiz" }
#   ]
# }
# Basically its a list of dictionaries of: {teamname, score, total (default 10), game}
# The old module had 4 functions lmfao XD
# Learnt some JOIN queries and figured out we could do this shit instead.
# Go figure, this is absolute cinema T_T
# So moving this shit to a different file, refer legacy for old shit or details
def leaderboards():
    conn, cursor = cursorcall()
    try:
        cursor.execute("""
            SELECT t.team_name, s.score, s.total
            FROM scores s
            JOIN users u ON s.user_id = u.id
            JOIN teams t ON u.team_id = t.id
            ORDER BY s.score DESC, s.created_at ASC
        """)
        rows = cursor.fetchall()
        payload = [
            {"teamName": row["team_name"], "score": row["score"], "total": row["total"], "game": "quiz"}
            for row in rows
        ]
        return {"leaderboard": payload}
    except Exception as e:
        return {"leaderboard": [], "error": str(e)}
    finally:
        conn.close()