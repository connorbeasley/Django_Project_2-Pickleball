# 05 - Build the schedule

## Goal
An admin clicks one button and the app creates every game for every week of a doubles division. Anyone can see the schedule.

## helpers.py

### `round_robin_rounds(teams)`
Standard "circle method" round robin. Write it plainly with a comment on each step.
1. Copy the list. If the count is odd, append `None` (a bye).
2. Repeat `n - 1` times (n = list length):
   - Pair the list from both ends: `(items[i], items[n - 1 - i])` for `i` in `range(n // 2)`. Skip any pair that contains `None`. That's one round.
   - Rotate: keep the first item fixed, move the last item to position 1.
3. Return the list of rounds (each round is a list of pairs).

Every pair of teams appears exactly once, and no team appears twice in the same round.

### `build_schedule(teams, num_weeks, games_per_week)`
1. Flatten `round_robin_rounds(teams)` into one list of matchups, in order.
2. Walk through weeks 1..`num_weeks` and game numbers 1..`games_per_week`. Each game takes the next matchup, wrapping back to the start of the list when it runs out (use `index % len(matchups)`).
3. Return a list of tuples `(week, game_number, team1, team2)`. Don't touch the database here.

Example: 4 teams, 4 weeks, 3 games per night gives 12 games, and every pair plays twice over the league.

## Pages

### Generate schedule (`divisions/<int:division_id>/schedule/generate/`, `generate_schedule`) - admin only, POST button
Checks, in order. Each failure shows an error message and redirects to the division page:
1. Any game in this division already has a score: "Scores have been entered, so the schedule can't be rebuilt."
2. Fewer than 2 teams that aren't dropped: "Add at least 2 teams first."
3. `games_per_week` is more than (number of pairs x `max_meetings_per_night`), where pairs = `n * (n - 1) // 2`: "With N teams, each night can have at most M games." (fill in the numbers)

Then: delete this division's existing games, create a `Game` for each tuple from `build_schedule` (use teams ordered by `id`, excluding dropped teams), show "Schedule created: X games.", and redirect.

For scramble divisions, show "Scramble schedules come in a later update." and redirect. (Spec 10 handles scramble.)

### Division detail (update)
- Replace the "Schedule: Coming soon" placeholder.
- Admins see a "Build schedule" button (or "Rebuild schedule" if games exist).
- Show games in a table ordered by `week`, then `game_number`. Use the built-in `{% ifchanged game.week %}` tag to print a "Week N" heading before each new week.
- Columns: Game #, Time, Court, Team 1, Score, Team 2. Show "TBD" for an empty time or court and "-" for a missing score.
- If there are no games: "No schedule yet."

## Acceptance tests
- 4 teams, 4 weeks, 3 games per night, once: build gives 12 games, 3 under each week heading. Each pair of teams shows up twice in total.
- 4 teams, 7 games per night, once: error says at most 6 games.
- Same, but "twice": 7 games works.
- 5 teams (odd number): the schedule builds and no team plays itself.
- After building, "Create a team" shows "Registration is closed."
- Logged out: the schedule table still shows.
- In the shell: `round_robin_rounds([1, 2, 3, 4])` returns 3 rounds of 2 pairs, and all 6 pairs appear once.
