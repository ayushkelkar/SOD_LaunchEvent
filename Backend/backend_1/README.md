# SOD - Logo Launch Event Backend

## `master.db`:
- Stores 3 main databases: `teams`, `users`, and `team_members`. 
- Details for the databases are given later.

## `team_create.py`:
- Module for team creation.
- Frontend sends a JSON payload regarding team creation from a user, received by `flask_main` which hands it over to `team_create` which then hands it over to `db_mgmt` then `flask_main` again.
- `flask_main` then sends an output JSON payload regarding success or failure.

## Database Schema
### `teams`:
- Tuples are each team's unique ID and name.
- Attributes:
1. `team_id` - Primary Key and auto-incremented. Gives a unique identifier for a team.
2. `team_name` - User entered team name. Received from Frontend.

### `users`:
- Master table for storage of usernames and passwords for the event.
- Just note: Username and Password for the event will be different from the main website's login.
- Tuples are the user's unique userid and username.
- [WIP] Later, this will also store the team leader's password hash using bcrypt.
- Attributes:
1. `user_id`: Primary Key and auto-incremented. Gives a unique identifier for a user.
2. `username`: User-entered username.

### `team_members`:
- Table relating `team_id` and `user_id`.