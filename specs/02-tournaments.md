# 02 - Create and view tournaments, add admins

## Goal
A staff user (`is_staff`, set in /admin) can create a tournament and becomes its admin. Anyone can browse tournaments. Admins can add other admins.

## Pages

### Home (`''`, `index`) - public
- Update the existing home page to list every tournament, newest first, each linking to its detail page. If none: "No tournaments yet."
- If the user is staff, show a "Create a tournament" link. If logged in, also show "Join with a code" (the join page comes in spec 04, so add that link in spec 04, not now).

### New tournament (`tournaments/new/`, `new_tournament`) - staff only
- `@login_required`, then `raise Http404` if `request.user.is_staff` is False.
- `TournamentForm` (ModelForm) with fields: `name`, `start_date`, `num_weeks`, `num_courts`, `ranking_method`, `players_enter_scores`, `game_minutes`.
- In the form's `Meta`, set `widgets = {'start_date': forms.DateInput(attrs={'type': 'date'})}` so the browser shows a date picker (see Pattern 4 in `CLAUDE.md`).
- Labels: "Number of weeks (1 for a one-day event)", "Number of courts", "Rank teams by", "Let players enter their own scores", "Game length in minutes (for every division)".
- On a valid POST: `form.save(commit=False)`, set `join_code = make_join_code()`, save, then add `request.user` to both `admins` and `members`. (Many-to-many fields can only be added to after the first save.) Redirect to the tournament detail page.

### Tournament detail (`tournaments/<int:tournament_id>/`, `tournament`) - public
Show:
- Name, start date, number of weeks, number of courts, ranking method (use `get_ranking_method_display`), and whether players enter scores.
- List of divisions (empty for now: "No divisions yet.").
- List of admin usernames.

If `is_admin(request.user, tournament)`, also show:
- The join code and the full join link. Build the link in the view with `request.build_absolute_uri(reverse('tournaments:join_tournament', args=[tournament.join_code]))`. Since that URL doesn't exist until spec 04, show only the code for now and leave a comment `# join link added in spec 04`.
- A link to "Add an admin".

### Add admin (`tournaments/<int:tournament_id>/admins/add/`, `add_admin`) - admin only
- Plain `forms.Form` named `AddAdminForm` with one field, `username`.
- On POST: look up the user with `User.objects.filter(username=...).first()`. If not found, show the form again with the error "No user with that username." If found, add them to `admins` and `members`, show a success message, and redirect to the tournament detail page.

## Acceptance tests
- Logged out: home lists tournaments, no "Create" link. Visiting `/tournaments/new/` sends me to login.
- Logged in as user A (staff): create "Tuesday Night League", 4 weeks, 4 courts, ranked by wins. I land on its page and see the join code and "Add an admin".
- Log out: the tournament page still loads (spectator), but no join code or admin link shows.
- Register user B. As A, add B as an admin. B now sees the join code on that page.
- As A, try adding username "nobody": error shows.
- As user C (not an admin), go to `/tournaments/1/admins/add/` directly: 404.
- As a non-staff user: no "Create a tournament" link, and `/tournaments/new/` gives a 404.
