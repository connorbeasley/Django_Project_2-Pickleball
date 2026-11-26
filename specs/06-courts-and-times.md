# 06 - Courts and times

## Goal
The director has only four courts. She sets the time for each game, the app can fill in courts for her, it warns her when a court is double-booked, and she can copy week 1's setup to every other week.

## Pages

### Edit game (`games/<int:game_id>/edit/`, `edit_game`) - admin only
- `GameScheduleForm` (ModelForm) with fields `court` and `start_time`. Use `forms.TimeInput(attrs={'type': 'time'})` as the widget for `start_time`.
- Load the form with `instance=game` (Pattern 3 in `CLAUDE.md`).
- On a valid POST, before saving, check two things. If either fails, add the error with `form.add_error(None, '...')` and show the form again:
  1. The court is between 1 and the tournament's `num_courts`: "This tournament only has 4 courts." (use the real number)
  2. No other game in the same tournament, same week, same court, and same start time exists. Query: `Game.objects.filter(division__tournament=tournament, week=game.week, court=..., start_time=...).exclude(id=game.id)`. The double underscore follows the foreign key from Game to Division to Tournament. Error: "Court 2 is already used at 6:00 PM in week 1 by <that game's division>."
- Then save and redirect to the division page.
- Show the game (week, teams) at the top of the page.

### Auto-assign courts (`divisions/<int:division_id>/courts/auto/`, `auto_courts`) - admin only, POST button
- Helper `court_for(game_number, num_courts)` in `helpers.py` returns `((game_number - 1) % num_courts) + 1`. So games 1-4 get courts 1-4 and game 5 starts over at court 1.
- Set `court` on every game in the division with that helper. Don't change times. Success message, redirect.

### Copy week 1 (`divisions/<int:division_id>/copy-week-one/`, `copy_week_one`) - admin only, POST button
- For every game in week 2 and later, find the week 1 game in the same division with the same `game_number`, and copy its `court` and `start_time`. Success message "Copied week 1 times and courts to every week.", redirect.

### Division detail (update)
- Admins see an "Edit" link on each game row, plus "Auto-assign courts" and "Copy week 1 to all weeks" buttons above the schedule (only when games exist).

## Acceptance tests
- Build a 4-team schedule with 3 games per night. Click "Auto-assign courts": week 1 shows courts 1, 2, 3.
- Set week 1 game 1 to court 1 at 6:00 PM. Set game 2 to court 1 at 6:00 PM: double-booked error.
- Set game 2 to court 5 in a 4-court tournament: court error.
- Set week 1 times to 6:00, 6:00, 6:30. Click "Copy week 1": every week now matches week 1.
- Make a second division in the same tournament. Try to put one of its week 1 games on a court and time already used by the first division: double-booked error names the first division.
- Logged out: times and courts show on the schedule, no Edit links.
