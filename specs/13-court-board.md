# 13 - Court board and court-style theme

Only start this after spec 12 is committed, so this can be undone.

## Goal
Make the app look like it belongs to a pickleball club instead of a generic website, and show each night's games the way the director thinks about them: as courts filling up over the evening.

## Part 1: the court board

### helpers.py
`court_board(games, num_courts)` lays out one night's games as a grid. No database changes.
1. Make one row per start time and one column per court (1 to `num_courts`). Each cell is a game or `None` (open court).
2. A game goes in the cell for its `start_time` and `court`.
3. A game with no time, no court, or a court outside 1 to `num_courts` goes in an `unplaced` list instead. If two games land in the same cell, the second one also goes in `unplaced`, so nothing is ever hidden.
4. Return `{'courts': [1, 2, ...], 'rows': [{'time': ..., 'cells': [...]}, ...], 'unplaced': [...]}` with rows sorted by time.

It works for both `Game` and `ScrambleGame`, since both have `start_time` and `court`.

### Division view (update)
- Replace `game_rows` and `scramble_rows` with a list of boards:
  - Doubles: one board per week, titled "Week N", made from that week's games.
  - Scramble: one board for the night, titled "Tonight", made from all the scramble games.
- Instead of `(game, can_score)` pairs, set `game.can_score = can_enter_score(...)` (or `can_enter_scramble_score`) on each game before building the boards. It's just an extra attribute on the object for the template to read.
- Pass `has_games` (True if the division has any games) for the Build/Rebuild label and the admin buttons.

### Division template (update)
- The Schedule section shows each board: a "Week N" heading, then a table with a time column and one column per court. Empty cells say "Open".
- Each game is drawn by a small template included with `{% include %}`: `doubles_match.html` or `scramble_match.html`. It shows the game number, both sides, and the score. The winning side is bold, the losing side is muted, and forfeits are labeled. Admins see Edit, and anyone allowed sees Enter score / Edit score, same rules as before.
- Under each board, games in `unplaced` show under "Needs a court and time", drawn the same way.
- The board sits in `table-responsive` so it scrolls sideways on phones.

## Part 2: court-style theme

All in one `<style>` block in `base.html` (Render doesn't serve static files, so no separate CSS file). Keep it short and comment each group.
- Colors from a court: court green, kitchen blue, white lines, and pickleball yellow as the one accent. Flat colors, no gradients, no glow, no heavy shadows.
- Headings in a condensed athletic font (one Google Fonts link, "Barlow Condensed"). Scores use fixed-width digits so columns line up like a scoreboard.
- Sections are separated by thin lines like court markings, not floating cards.
- Navbar in court green with a yellow line under it.
- Bootstrap 4 and `{% bootstrap_form %}` stay. This only restyles on top.
- Don't: emoji, purple/blue gradients, big centered hero, everything in rounded shadow cards.

## Not changed
Models, URLs, forms, and every other view. The standings, teams list, and all form pages keep working the same; they just pick up the new colors and fonts.

## Acceptance tests
- Demo league, week 1: the board shows 6:00 PM with games on courts 1 and 2, 6:30 PM with a game on court 3, and court 4 "Open". Same layout in weeks 2 to 4.
- Scored games show the winner bold and the loser muted. Lob Stars' forfeits are labeled.
- Build a new schedule with no times: there's no grid yet, and every game shows under "Needs a court and time". After "Auto-fill times", every game moves onto the board.
- Demo scramble: one board from 6:00 PM to 9:00 PM, games on courts 1 and 2, courts 3 and 4 open.
- Edit, Enter score, and Edit score links in the cells work for the same people as before. Logged out: the board shows with no links.
- Phone width: the board scrolls sideways and the page doesn't break.
- Every acceptance test from specs 02 to 12 still passes.
