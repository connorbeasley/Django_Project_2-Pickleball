# 08 - Standings and seeding

## Goal
Each division shows a leaderboard, ranked by wins and losses or by total points, depending on the tournament's `ranking_method`.

## helpers.py
`standings(division)`:
1. Start a row for every team in the division (including dropped teams): `{'team': team, 'played': 0, 'wins': 0, 'losses': 0, 'points': 0, 'allowed': 0}`. Keep the rows in a dictionary keyed by team id while counting.
2. Loop over the division's games that have both scores. For each, add 1 to `played` for both teams, add each team's score to its own `points` and the other team's score to its `allowed`, and add a win to the winner and a loss to the other team (use `game.winner()`).
3. Work out each row's point differential: `diff = points - allowed`. (Added after testing: without it, teams tied on wins and points were ordered by when they were added.)
4. Sort the rows:
   - `'wins'`: most wins first, then most points, then best +/-.
   - `'points'`: most points first, then most wins, then best +/-.
   Use `sorted(rows, key=lambda row: (row['wins'], row['points'], row['diff']), reverse=True)` and swap the first two for points. Put a comment on the lambda.
5. Return the sorted list.

## Division detail (update)
- Replace the "Standings: Coming soon" placeholder with a table: Seed, Team, Played, W, L, Points, +/- (shown like +6 or -3). Seed is `forloop.counter`.
- Above the table: "Ranked by wins and losses" or "Ranked by total points" using `get_ranking_method_display`.
- Add "(dropped)" after a dropped team's name.

## Acceptance tests
- Enter scores for a few games by hand and check the table against my own count on paper.
- Change `ranking_method` to points in /admin. A team with fewer wins but more points moves up.
- A division with no scores shows every team with zeros.
- Logged out: the table shows.
- Two teams with the same wins and the same points: the one with the better +/- is seeded higher.
