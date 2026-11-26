# 00 - Project setup and first deploy

## Goal
A fresh Django project with working accounts, live on Render before any features exist.

The old Learning Log project is at: `"C:\Users\conno\Documents\LearningLogProject"`

## Steps
1. In this folder (the new, empty `PickleballProject` repo), create a virtual environment with Python 3.11 and install the packages from the old project's `requirements.txt`. Copy `requirements.txt` over too.
2. Run `django-admin startproject pickleball .` (keep the period).
3. Run `python manage.py startapp tournaments`.
4. Copy the `users` app folder from the old project. Search it for `MainApp` and replace each reference with `tournaments` (for example, redirects to `MainApp:index` become `tournaments:index`).
5. In `pickleball/settings.py`:
   - Put `'users'` and `'tournaments'` at the top of `INSTALLED_APPS`, before the `django.contrib` apps. (Learning Log lesson: otherwise Django's default logged-out page shows instead of ours.)
   - If the copied `users` templates use `{% load bootstrap4 %}`, also add `'bootstrap4'` to `INSTALLED_APPS`.
   - Add `LOGIN_URL = 'users:login'`.
   - Set `ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.onrender.com']` and `CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']` so forms work on Render.
   - Compare against the old project's `settings.py` and copy any other deployment settings it had (DEBUG handling, static files). Tell me exactly what you copied.
6. In `pickleball/urls.py`: include `users.urls` at `'users/'` and `tournaments.urls` at `''`.
7. In the `tournaments` app:
   - `urls.py` with `app_name = 'tournaments'` and one path: `''` -> `views.index`, name `index`.
   - `templates/tournaments/base.html`: links to Home. If logged in: "Hello, username" and Log out. If not: Register and Log in. Show any `messages`. Then `{% block content %}{% endblock content %}`.
   - `templates/tournaments/index.html`: extends base, heading "Waco Regional Pickleball" and one sentence about the app.
8. Copy `start.sh` from the old project and change `learning_log.wsgi` to `pickleball.wsgi`.
9. `.gitignore`: the venv folder, `.vscode/`, and `__pycache__/`. Do NOT ignore `db.sqlite3`. We commit it on purpose so the live demo has data.
10. Run `migrate`. I'll run `createsuperuser` myself.

## Acceptance tests
- `runserver`, open the home page, see the heading.
- Register a new user -> logged in, redirected home, see "Hello, <name>".
- Log out -> our custom logged-out page shows (not Django's default).
- Log in with a wrong password -> error message. Right password -> works.
- `/admin` works with the superuser.

## Deploy (I do this part by hand)
- Commit and push to GitHub.
- On Render, create a new Web Service from the `PickleballProject` repo with the same build and start commands as the Learning Log service.
- Open the live URL. Home page loads, register and login work.

## Note
Render's disk resets on every deploy or restart, so the live site always starts from the committed `db.sqlite3`. Use throwaway passwords for every account in it (not your Baylor password). The password hashes are public in the repo.
