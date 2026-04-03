# Silicon Multiverse — Round 3 Backend

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Server runs on `http://localhost:5000`.

---

## API Endpoints

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| POST | `/api/auth/login` | None | Login with username + password |
| POST | `/api/hunt/complete` | Bearer JWT | Mark entire hunt as complete |
| POST | `/api/hunt/section/<id>/complete` | Bearer JWT | Mark a single section complete |
| GET | `/api/admin/hunt-progress` | Admin | Get all team progress |
| POST | `/api/admin/seed` | Admin | Add a new team at runtime |
| POST | `/api/admin/reset/<username>` | Admin | Reset a team's progress |
| GET | `/api/health` | None | Health check |

---

## Admin Access

The frontend uses a hardcoded admin token `"admin"` for the admin session.  
The backend accepts `Authorization: Bearer admin` on all `/api/admin/*` routes.

---

## Adding Teams

### Option 1 — Edit `SEED_TEAMS` in `app.py` before starting:
```python
SEED_TEAMS = [
    {"username": "team-delta", "password": "delta999", "teamName": "Team Delta"},
    ...
]
```

### Option 2 — POST to `/api/admin/seed` at runtime:
```bash
curl -X POST http://localhost:5000/api/admin/seed \
  -H "Authorization: Bearer admin" \
  -H "Content-Type: application/json" \
  -d '{"username":"team-delta","password":"delta999","teamName":"Team Delta"}'
```

---

## Production Notes

- Set `JWT_SECRET` env var to something strong and secret.
- Replace the in-memory `TEAMS` dict with SQLite or Postgres for persistence across restarts.
- Put a reverse proxy (nginx) in front and serve the React build as static files from there.
- Flip `debug=False` in `app.run()`.
