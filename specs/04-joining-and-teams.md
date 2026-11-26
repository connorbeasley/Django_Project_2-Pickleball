# 04 - Join codes and team sign-up

## Goal
The director shares a code or link. Players who join can create a team in a division or join a team as the partner. Admins can add teams by typing names.

## Pages

### Join with a code (`join/`, `join_with_code`) - login required
- Plain `forms.Form` named `JoinCodeForm` with one field, `code`.
- On POST: find the tournament with `join_code` equal to the code in uppercase. If none: error "That code doesn't match any tournament." If found: add the user to `members`, success message "You joined <name>.", redirect to the tournament page.
- Add the "Join with a code" link to the home page for logged-in users.

### Join link (`join/<str:code>/`, `join_tournament`) - login required
- This is the link the director texts or emails. Find the tournament by code with `get_object_or_404`, add the user to `members`, success message, redirect to the tournament page.
- Because of `@login_required` and `LOGIN_URL`, someone who isn't logged in gets sent to login first. Check that after login they come back to this link. If they don't, make the login template's hidden `next` field use `{{ request.GET.next }}` when it exists, and the home page otherwise.
- On the tournament detail page, admins now see the full join link (see spec 02).

### New team (`divisions/<int:division_id>/teams/new/`, `new_team`) - login required, member or admin
- `TeamForm` (ModelForm) with one field: `name`. Label: "Team name".
- Raise `Http404` if the user is neither a member nor an admin.
- Refuse with an error message and redirect to the division page if:
  - the division already has `max_teams` teams, or (for the site superuser, redirect instead to a page to raise max teams, then on to the new team form; see "Raise max teams" below)
  - the division already has games (registration is closed), or
  - the user is not an admin and is already the captain or partner of a team in this division.
- On a valid POST: `commit=False`, set `team.division`. If the user is an admin, leave `captain` empty (the admin is typing in someone else's team). Otherwise set `captain = request.user`. Save and redirect to the division page.

### Join a team (`teams/<int:team_id>/join/`, `join_team`) - login required, member only, POST button
- Only when the team has no `partner`, the user is a member, the user isn't already on a team in this division, and registration isn't closed. Otherwise show an error message.
- Set `team.partner = request.user`, save, success message, redirect to the division page.

### Raise max teams (`divisions/<int:division_id>/max-teams/`, `edit_max_teams`) - superuser only
- `@login_required`, then `raise Http404` if the user is not `is_superuser`.
- `MaxTeamsForm` (ModelForm) with one field, `max_teams`, loaded with `instance=division` (Pattern 3).
- Show "This division has X of Y teams." above the form.
- The new number must be higher than the current team count, otherwise show "Set it higher than the X teams already signed up."
- On save: success message "Max teams is now N.", redirect to the new team form.

### Division detail (update)
In the Teams section, show each team as: name, then captain and partner usernames (or "Added by admin" when both are empty, or "Looking for a partner" when only the captain is set).
- Show "Create a team" if the user is a member and registration is open. Show "Add a team" if the user is an admin.
- Show a "Join as partner" button next to teams looking for a partner, for members who aren't on a team here yet.
- If registration is closed, show "Registration is closed."
- Put the repeated checks ("is this user on a team in this division", "is registration closed") in small helpers in `helpers.py`: `user_team_in_division(user, division)` returns the team or None, and `registration_closed(division)` returns True if the division has any games.

## Acceptance tests
- As the admin, copy the join link. Log out, open the link, log in as user C. I land on the tournament page with "You joined" showing.
- As user D, use "Join with a code" with the code in lowercase. It works.
- As C, create team "Dink Masters". It shows "Looking for a partner".
- As D, click "Join as partner" on Dink Masters. It now shows both usernames.
- As D, try to create another team in the same division: error.
- As the admin, add team "Smith / Jones". It shows "Added by admin".
- Fill the division to `max_teams`. "Create a team" now gives an error.
- As user E who never joined, visit the new team URL directly: 404.
- As the superuser, "Add a team" on a full division goes to a page to raise max teams. Entering the current team count shows an error. Raising it saves and opens the add team form. The tournament page then shows the new count, like "3 of 3 teams".
- As a tournament admin who is not the superuser, a full division just says "This division is full.", and the raise max teams URL gives a 404.
