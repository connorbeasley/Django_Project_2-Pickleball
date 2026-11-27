# 07 - Entering scores

## Goal
Admins can always enter scores. In big tournaments where the admin turned on `players_enter_scores`, players on either team can enter their own game's score. Everyone else just watches.

## helpers.py
`can_enter_score(user, game)`:
- True if `is_admin(user, tournament)`.
- Otherwise True only if `tournament.players_enter_scores` is on, the game has no score yet, and the user is the captain or partner of `game.team1` or `game.team2`.
- False for anyone not logged in.

## Pages

### Enter score (`games/<int:game_id>/score/`, `enter_score`) - login required
- Raise `Http404` if `can_enter_score` is False.
- `ScoreForm` (ModelForm) with fields `team1_score` and `team2_score`. Declare both fields in the form class as `forms.IntegerField(min_value=0)` so they're required here even though the model allows blanks.
- Use the team names as the labels. Set them in the view after making the form: `form.fields['team1_score'].label = game.team1.name` (same for team 2).
- Load with `instance=game`. On a valid POST, if the two scores are equal, `form.add_error(None, "Scores can't be tied.")` and show the form again. Otherwise save and redirect to the division page.
- Players (not admins) must also enter a score that fits the division's rules, checked by `score_problem(division, score1, score2)` in `helpers.py`: the winner reaches at least `target_points()`; with win by 2, the winner leads by at least 2, and past the target the lead is exactly 2. Without win by 2, the winner has exactly `target_points()`. Admins can enter any score. Show the rule ("Games are played to 11, win by 2.") above the form. (Added after spec 10.)
- Show the week and game number at the top.

### Division detail (update)
- Show the score in the Score column as "11 - 7" when both scores exist.
- Show an "Enter score" link (or "Edit score" for admins when a score exists) on rows where `can_enter_score` is True. A template can't call a function with arguments, so in the view build a list of `(game, can_score)` pairs and loop over that list in the template.

## Acceptance tests
- As an admin, enter 11 - 7 for a game. It shows on the schedule.
- Enter 9 - 9: "Scores can't be tied."
- Leave one score blank: required error.
- With `players_enter_scores` off (change it in /admin): log in as a player on that game. No "Enter score" link, and the URL directly gives 404.
- Turn it on. The player sees "Enter score" only on their own team's unscored games. After they enter a score, the link goes away for them but the admin can still edit it.
- Logged out: scores show, no links.
- As a player in a game-to-11, win-by-2 division: 8 - 5, 11 - 10 and 15 - 8 are refused; 11 - 9 and 12 - 10 are accepted. As an admin, 8 - 5 saves.
- A division set to 15: a player's 11 - 9 is refused, 15 - 13 is accepted. A division with win by 2 set to No: 11 - 10 is accepted, 12 - 10 is refused.
