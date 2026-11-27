# 09 - Team dropouts and forfeits

## Goal
When a team drops out, every game it hasn't played yet becomes a forfeit: a loss for that team and an automatic win for the opponent. Games already played stay as they are.

## helpers.py
`forfeit_remaining_games(team)`:
1. Find every game in `team.division` where `team1` or `team2` is this team and `team1_score` is empty. Use two queries (one for team1, one for team2) to keep it readable.
2. For each one, give the other team the division's `target_points()` (usually 11) and this team 0, and set `forfeit = True`. Save.
3. Return how many games were changed.

## Pages

### Drop team (`teams/<int:team_id>/drop/`, `drop_team`) - admin only
- GET shows a confirm page: "Drop <team>? Their remaining games become forfeits. This can't be undone here." with a "Drop team" button and a "Cancel" link back to the division.
- POST: set `team.dropped = True`, save, call `forfeit_remaining_games(team)`, success message "<team> dropped. N games marked as forfeits.", redirect to the division page.
- If the team is already dropped, show an error message and redirect.
- Scramble divisions: error "Dropouts aren't supported in scramble." and redirect.

### Division detail (update)
- Admins see a "Drop" link next to each team that isn't dropped (doubles divisions only).
- In the schedule, show "(forfeit)" next to the score of forfeit games.
- In the Teams list, show "(dropped)" after dropped teams.

### Other specs this touches
- Spec 04: dropped teams still count toward `max_teams`. No change needed.
- Spec 05: "Build schedule" already skips dropped teams.
- Spec 07: forfeit games already have a score, so players can't enter one. Admins can still edit it.

## Acceptance tests
- 4 teams, schedule built, week 1 scored. Drop team 2: every later game with team 2 shows 11 - 0 for the opponent and "(forfeit)". Week 1 scores don't change.
- In a division played to 15, forfeits show 15 - 0.
- Standings: team 2 picks up a loss for every forfeit, and their opponents pick up wins.
- Drop the same team again: error.
- As a non-admin, the drop URL gives 404.
