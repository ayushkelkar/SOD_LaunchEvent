# This is deprecated. Putting it in legacy codebase for future reference.

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
# So teamname can be gotten from the userid. Which can be indexed from the scores table.

# So you can't sort and save tables in SQLite. You can print them sorted, but not save them.

# This gets the userids as a list. So, we can use them to find teamids in teams.
def get_userids(cursor):
    cursor.execute("SELECT user_id FROM scores")
    rows = cursor.fetchall()
    user_ids = [row[0] for row in rows]
    return user_ids

# This now gets teamids using userids
def get_teamids(cursor, userids):
    # Making placeholder because idk how many userids I'll have
    placeholders = ','.join('?' for _ in userids)
    query = f"SELECT team_id FROM users WHERE id IN ({placeholders})"
    cursor.execute(query, userids)
    rows = cursor.fetchall()
    teamids = [row[0] for row in rows]
    return teamids

# This now gets teamnames using teamids
def get_teamnames(cursor, teamids):
    # Again making placeholder
    placeholders = ','.join('?' for _ in teamids)
    query = f"SELECT team_name FROM teams WHERE id IN ({placeholders})"
    cursor.execute(query, teamids)
    rows = cursor.fetchall()
    teamnames = [row[0] for row in rows]
    return teamnames

# This gets scores using userids
def get_score(cursor, userids):
    # Again making placeholder
    placeholders = ','.join('?' for _ in userids)
    query = f"SELECT score FROM scores WHERE user_id IN ({placeholders})"
    cursor.execute(query, userids)
    rows = cursor.fetchall()
    scores = [row[0] for row in rows]
    return scores

# This makes the team names and scores into key-value paired dictionaries and then sorts them in decending order
def get_dict(teamname, score):
    combined_dict = dict(zip(teamname, score))
    sorted_dict = dict(sorted(combined_dict.items(), key=lambda x: x[1], reverse=True))
    return sorted_dict

# This seperates the teamname-score pairs and appends total score and game type to them by each teamname-score pair for the final list of dictionaries object
def get_payload(sorted_dict):
    #teams = list(sorted_dict.keys())
    #scores = list(sorted_dict.values())
    total = 10
    game = 'quiz'
    payload = [{'teamName': teams, 'score': scores, 'total': total, 'game': game} for teams, scores in sorted_dict.items()]
    return payload

# Main function basically
def leaderboards():
    conn, cursor = cursorcall()
    userids = get_userids(cursor)
    teamids = get_teamids(cursor, userids)
    teamnames = get_teamnames(cursor, teamids)
    scores = get_score(cursor, userids)
    sorted_dict = get_dict(teamnames, scores)
    payload = get_payload(sorted_dict)
    response = {"leaderboard": payload}
    return response