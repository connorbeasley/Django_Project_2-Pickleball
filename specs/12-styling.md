# 12 - Styling

Only start this after spec 11 passes on the live site. Commit first so styling can be undone.

## Goal
Make the app look clean and work well on a phone, since players and spectators will mostly check it from their phones. No behavior changes.

## Rules
- Use `django-bootstrap4`, which is already in `requirements.txt`. Make sure `'bootstrap4'` is in `INSTALLED_APPS`.
- In `base.html`: `{% load bootstrap4 %}` at the top, then `{% bootstrap_css %}` and `{% bootstrap_javascript jquery='full' %}` inside `<head>`.
- In each form template: `{% load bootstrap4 %}`, then replace `{{ form.as_p }}` with `{% bootstrap_form form %}` and give the submit button `class="btn btn-primary"`.
- The copied `users` templates may already do this. Match their style.
- `base.html`: a Bootstrap navbar with Home, Join with a code, and the login/logout/register links. Messages show as Bootstrap alerts (`alert-success`, `alert-danger`).
- Tables: `table table-sm table-striped`, wrapped in `table-responsive` so wide schedules scroll on phones.
- Buttons: `btn btn-primary` for main actions, `btn btn-outline-secondary` for small ones like Edit, `btn btn-danger` for Drop.
- Division page: put Teams, Schedule, and Standings in clear sections with headings.
- Don't change any view, URL, model, or form logic. Templates and widget `attrs` only.

## Acceptance tests
- Every acceptance test from specs 02-09 (and 10 if built) still passes.
- On a phone-width browser window, the schedule table scrolls sideways instead of breaking the page.
