# 03 - Divisions

## Goal
Admins add divisions (for example "Beginner Women's doubles") to a tournament. Anyone can view a division page.

## Pages

### New division (`tournaments/<int:tournament_id>/divisions/new/`, `new_division`) - admin only
- `DivisionForm` (ModelForm) with fields: `level`, `format`, `max_teams`, `games_per_week`, `max_meetings_per_night`, `game_minutes`, `points_to_win`, `win_by_two`.
- Labels: "Max teams (or players for scramble)", "Games per night in this division", "How many times can two teams play each other in one night", "Game length in minutes (leave blank to use the tournament's)", "Games are played to (leave blank to use the tournament's)", "Must win by 2".
- On a valid POST: `commit=False`, set `division.tournament`, save, redirect to the tournament detail page.
- Show the tournament name at the top of the page, linked back to the tournament page. This is exactly Pattern 2 in `CLAUDE.md`.

### Tournament detail (update)
- List each division as a link to its page, with the team count, like "Beginner Women's doubles (3 of 8 teams)".
- Admins see an "Add a division" link.

### Division detail (`divisions/<int:division_id>/`, `division`) - public
For now show:
- Division name, linked back to the tournament.
- Settings: max teams, games per night, max meetings per night.
- A "Teams" section that lists team names, or "No teams yet." (Spec 04 adds sign-up buttons here.)
- Empty "Schedule" and "Standings" headings with "Coming soon." under each. Later specs replace these.

## Acceptance tests
- As an admin, add "Beginner / Women's doubles", max 8 teams, 3 games per night, once. It shows on the tournament page as "Beginner Women's doubles (0 of 8 teams)".
- Click it: the division page loads with the right settings.
- Logged out: the division page still loads. There's no "Add a division" link on the tournament page.
- As a non-admin, visiting the new division URL directly gives a 404.
