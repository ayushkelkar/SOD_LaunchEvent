from teams_creation import cursorcall

def set_quiz_status(enabled):
    conn, cursor = cursorcall()
    try:
        cursor.execute("SELECT id FROM quiz_config WHERE id = 1")
        row = cursor.fetchone()
        if row is None:
            cursor.execute("INSERT INTO quiz_config (id, enabled) VALUES (1, %s)", (1 if enabled else 0,))
        else:
            cursor.execute("UPDATE quiz_config SET enabled = %s WHERE id = 1", (1 if enabled else 0,))
        conn.commit()
        return {"message": "Quiz is now LIVE" if enabled else "Quiz is now OFFLINE"}
    except Exception as e:
        conn.rollback()
        return {"message": str(e)}
    finally:
        conn.close()

def get_status():
    conn, cursor = cursorcall()
    try:
        cursor.execute("SELECT enabled FROM quiz_config WHERE id = 1")
        row = cursor.fetchone()
        return {"enabled": bool(row["enabled"]) if row else False}
    except Exception as e:
        return {"enabled": False}
    finally:
        conn.close()

def get_users():
    conn, cursor = cursorcall()
    try:
        cursor.execute("""
            SELECT u.username, u.role, u.created_at as created_at, t.team_name as team_name
            FROM users u
            JOIN teams t ON u.team_id = t.id
            ORDER BY t.team_name, u.role DESC
            """)
        rows = cursor.fetchall()
        users = [
                    {"username": row["username"], "role": row["role"], "teamName": row["team_name"], "createdAt": row["created_at"]}
                    for row in rows
                ]
        return {"success": True, "users": users}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "users": [], "error": str(e)}
    finally:
        conn.close()