# 06 - Courts and times

## Goal
The director has only four courts. She sets the time for each game, the app can fill in courts for her, it warns her when a court is double-booked, and she can copy week 1's setup to every other week.

## Pages

### Edit game (`games/<int:game_id>/edit/`, `edit_game`) - admin only
- `GameScheduleForm` (ModelForm) with fields `court` and `start_time`. Use `forms.TimeInput(attrs={'type': 'time'})` as the widget for `start_time`.
- Load the form with `instance=game` (Pattern 3 in `CLAUDE.md`).
- On a valid POST, before saving, check two things. If either fails, add the error with `form.add_error(None, '...')` and show the form again:
  1. The court is between 1 and the tournament's `num_courts`: "This tournament only has 4 courts." (use the real number)
  2. No other game in the same tournament, same week, and same court overlaps this game's time. Each game runs from its start time for its division's `game_length()` minutes, and two games overlap when each starts before the other ends (back-to-back is fine). Put this in a helper `court_conflict(game, court, start_time)` that returns the clashing game or None. Error: "Court 1 is already used by <that game's division> from 6:00 PM in week 1 (30 minute games)."
- Then save and redirect to the division page.
- Show the game (week, teams) at the top of the page.

### Auto-assign courts (`divisions/<int:division_id>/courts/auto/`, `auto_courts`) - admin only, POST button
- Helper `court_for(game_number, num_courts)` in `helpers.py` returns `((game_number - 1) % num_courts) + 1`. So games 1-4 get courts 1-4 and game 5 starts over at court 1.
- Set `court` on every game in the division with that helper. Don't change times. Success message, redirect.

### Copy week 1 (`divisions/<int:division_id>/copy-week-one/`, `copy_week_one`) - admin only, POST button
- For every game in week 2 and later, find the week 1 game in the same division with the same `game_number`, and copy its `court` and `start_time`. Success message "Copied week 1 times and courts to every week.", redirect.

### Auto-fill times (`divisions/<int:division_id>/times/auto/`, `auto_times`) - admin only
Added at my request so admins can choose between typing custom times (Edit page) and filling them all in at once. Single games can still be edited afterward.
- Plain `forms.Form` named `AutoTimesForm` with one field: `first_time` (TimeField, time picker, label "First game starts at"). Waves are spaced by the division's `game_length()`.
- On a valid POST, for every game in every week of the division:
  - `court = court_for(game_number, num_courts)`
  - `wave = (game_number - 1) // num_courts`, so with 4 courts games 1-4 are wave 0, games 5-8 are wave 1
  - `start_time = first_time + wave * division.game_length()`
- Then check each game with `court_conflict` (helper shared with the Edit page). If any overlap a game from another division on the same court, show a warning with the count: "Times filled in, but 3 games share a court and time with another division. Edit those games to fix them." Otherwise "Times filled in." Redirect to the division page.

### Division detail (update)
- Admins see an "Edit" link on each game row, plus "Auto-assign courts" and "Copy week 1 to all weeks" buttons and an "Auto-fill times" link above the schedule (only when games exist).
- Times show like "6:00 PM".

## Acceptance tests
- Build a 4-team schedule with 3 games per night. Click "Auto-assign courts": week 1 shows courts 1, 2, 3.
- Set week 1 game 1 to court 1 at 6:00 PM. Set game 2 to court 1 at 6:00 PM: double-booked error.
- Set game 2 to court 5 in a 4-court tournament: court error.
- Set week 1 times to 6:00, 6:00, 6:30. Click "Copy week 1": every week now matches week 1.
- Make a second division in the same tournament. Try to put one of its week 1 games on a court and time already used by the first division: double-booked error names the first division.
- Logged out: times and courts show on the schedule, no Edit links.
- With 30 minute games, a game at 6:00 PM on court 1, then another game on court 1 at 6:15 PM: double-booked error. At 6:30 PM: allowed. At 5:45 PM: error.
- In a 4-court tournament with 20 minute games, a division with 6 games per night: "Auto-fill times" at 6:00 PM puts games 1-4 at 6:00 PM on courts 1-4 and games 5-6 at 6:20 PM on courts 1-2, the same in every week.
- After auto-filling, "Edit" on a game still lets me set a custom time.
- Auto-fill a second division in the same tournament with the same start time: the warning shows how many games clash.
- A division with its own 20 minute game length (tournament is 30): auto-fill spaces its waves 20 minutes apart.
