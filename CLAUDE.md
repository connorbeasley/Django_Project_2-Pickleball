# Waco Regional Pickleball League App (Django Project Part 2)

## Context
I'm a college student building this for a class. It's a standalone Django app based on requirements from the Director of Pickleball at Waco Regional. It's due Thursday, Dec 3, 2026 at 11:59 PM, submitted as a live Render URL.

I learned Django in class by building a different project (a "Learning Log" journal app). That project is not in this repo, so don't look for it. The "Code patterns" section below shows exactly the style I learned. Match it. I have to understand and explain every line of this code, so simple and readable beats clever every time.

## How we work
- Specs live in `specs/` and are numbered. Do one spec at a time, in order.
- Before writing code for a spec, use plan mode: read the spec and the files it touches, then show me the plan.
- When a spec is done, list the manual test steps from its "Acceptance tests" section and stop. Do not start the next spec until I say so.
- If a spec is unclear or seems wrong, ask me. Don't guess, and don't add features the spec doesn't ask for.
- Don't change code that the current spec doesn't mention.

## Code rules
- Function-based views only. No class-based views.
- Every page follows the course pattern: a path in `urls.py`, a function in `views.py`, a template in `templates/<app>/`.
- Use ModelForms for anything that saves a model. Use a plain `forms.Form` only when there's no model behind it (for example, typing in a join code).
- Write views, forms, and templates the way the "Code patterns" section shows.
- Action buttons with no page of their own (generate schedule, copy week 1, join team) are small `<form method="post">` blocks with `{% csrf_token %}`. The view only does the action when `request.method == 'POST'`, then redirects back.
- For those action buttons, use `django.contrib.messages` to show success or error text. It's already enabled in default settings. `base.html` displays the messages.
- Templates use the Django template language only. No JavaScript, no AJAX, no front-end frameworks.
- No new pip packages. Use only what's in `requirements.txt` and the Python standard library.
- No signals, custom managers, custom template tags, mixins, REST APIs, or async code.
- Scheduling, standings, and forfeit logic go in `tournaments/helpers.py` as plain functions. Everything else stays in views.
- Keep functions short. Put a one-line comment above anything that isn't obvious.
- Model and field names must match `specs/01-models.md` exactly (and `specs/10-scramble.md` for the scramble model).
- No styling until spec 12. Plain HTML (h1, h2, p, ul, table, form).
- After any change to `models.py`, run `python manage.py makemigrations`, then `python manage.py migrate`.
- User-facing text should be short and plain. No em dashes.

## Permissions
- A "tournament admin" is any user in `tournament.admins`, plus the site superuser (who can manage every tournament). Use one helper, `is_admin(user, tournament)` in `helpers.py`, everywhere.
- A "staff user" is a user with `is_staff` checked in /admin (the director and her helpers). Only staff can create tournaments. Co-admins added with "Add an admin" do not need to be staff.
- A "member" is any user in `tournament.members` (they entered the join code). Use `is_member(user, tournament)` in `helpers.py`.
- Admin-only views: `@login_required`, then `raise Http404` if `is_admin` is False. See Pattern 2.
- Public views (spectator mode) have no decorator: home, tournament detail, division detail (teams, schedule, standings).

## Apps
- `users`: register, login, logout (copied in during spec 00, then lives in this repo).
- `tournaments`: everything else.

## Code patterns
These show the style I learned. New views should look like these.

### Pattern 1: a read-only page (URL -> view -> template)
```python
# tournaments/urls.py
from django.urls import path
from . import views

app_name = 'tournaments'
urlpatterns = [
    path('', views.index, name='index'),
    path('divisions/<int:division_id>/', views.division, name='division'),
]
```
```python
# tournaments/views.py
def division(request, division_id):
    # get_object_or_404 shows a "not found" page for a bad id instead of crashing.
    # (In class we used Division.objects.get(id=...). This is the one change from that.)
    division = get_object_or_404(Division, id=division_id)
    teams = division.team_set.order_by('name')
    context = {'division': division, 'teams': teams}
    return render(request, 'tournaments/division.html', context)
```
```html
<!-- tournaments/templates/tournaments/division.html -->
{% extends 'tournaments/base.html' %}
{% block content %}
  <h1>{{ division }}</h1>
  <p><a href="{% url 'tournaments:tournament' division.tournament.id %}">{{ division.tournament }}</a></p>
  <ul>
    {% for team in teams %}
      <li>{{ team.name }}</li>
    {% empty %}
      <li>No teams yet.</li>
    {% endfor %}
  </ul>
{% endblock content %}
```

### Pattern 2: a form page that creates something, with a permission check
```python
@login_required
def new_division(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if not is_admin(request.user, tournament):
        raise Http404

    if request.method != 'POST':
        # GET: show an empty form
        form = DivisionForm()
    else:
        # POST: save what the user typed
        form = DivisionForm(data=request.POST)
        if form.is_valid():
            # commit=False lets us fill in fields the user doesn't type
            new_division = form.save(commit=False)
            new_division.tournament = tournament
            new_division.save()
            return redirect('tournaments:tournament', tournament_id=tournament.id)

    context = {'tournament': tournament, 'form': form}
    return render(request, 'tournaments/new_division.html', context)
```
```html
{% extends 'tournaments/base.html' %}
{% block content %}
  <p><a href="{% url 'tournaments:tournament' tournament.id %}">{{ tournament }}</a></p>
  <p>Add a division:</p>
  <form action="{% url 'tournaments:new_division' tournament.id %}" method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button name="submit">Add division</button>
  </form>
{% endblock content %}
```

### Pattern 3: a form page that edits something that already exists
Same as Pattern 2, but pass `instance=` so the form fills in the current values and saves over the same row:
```python
if request.method != 'POST':
    form = GameScheduleForm(instance=game)
else:
    form = GameScheduleForm(instance=game, data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('tournaments:division', division_id=game.division.id)
```

### Pattern 4: a ModelForm
```python
# tournaments/forms.py
from django import forms
from .models import *

class DivisionForm(forms.ModelForm):
    class Meta:
        model = Division
        fields = ['level', 'format', 'max_teams', 'games_per_week', 'max_meetings_per_night']
        labels = {'max_teams': 'Max teams (or players for scramble)'}
        # widgets change how a field looks in HTML, for example:
        # widgets = {'start_date': forms.DateInput(attrs={'type': 'date'})}
```

### Pattern 5: an action button (new, not taught in class)
For actions with no page of their own. The template has a tiny form:
```html
<form action="{% url 'tournaments:generate_schedule' division.id %}" method="post">
  {% csrf_token %}
  <button name="submit">Build schedule</button>
</form>
```
The view does the work only on POST, adds a message, and redirects:
```python
from django.contrib import messages

@login_required
def generate_schedule(request, division_id):
    division = get_object_or_404(Division, id=division_id)
    if not is_admin(request.user, division.tournament):
        raise Http404
    if request.method == 'POST':
        # ... do the work ...
        messages.success(request, 'Schedule created.')
    return redirect('tournaments:division', division_id=division.id)
```
`base.html` shows messages above the page content:
```html
{% for message in messages %}
  <p>{{ message }}</p>
{% endfor %}
```

## Working assumptions (until the director confirms)
1. A "league" is a tournament that runs for more than one week. One `Tournament` model handles both. A one-day event is a tournament with `num_weeks = 1`.
2. Each division schedules on its own. The app makes a round-robin order of matchups and keeps cycling through it until every week has `games_per_week` games. The cycle continues from week to week, so teams rotate opponents across the league.
3. `max_meetings_per_night` (1 or 2) caps how many times two teams can play each other in one week. The app refuses to build a schedule if `games_per_week` is more than that allows.
4. "Copy week 1" copies start times and courts from week 1 onto the same game numbers in every later week. It does not change matchups.
5. A forfeit is a win for the opponent and a loss for the team that dropped out. The score is recorded as the division's points to win to 0 (usually 11 to 0).
6. Spectator mode means anyone can see schedules, scores, and standings without logging in. Refreshing the page shows new scores.
7. Inviting people by text or email means the admin copies a join link and sends it themselves. The app does not send messages.
8. Registration in a division closes to players once its schedule is built. Admins can still add a late team until any score is entered, then rebuild the schedule to give it games.
9. When players are allowed to enter scores, the first score entered stands. Admins can always change it.
10. Teams an admin adds by name have no linked user accounts (the director said she's fine typing names).
11. A scramble is one night. Players sign up alone, every player partners every other player once, and a scramble needs a player count divisible by 4 (4, 8, 12, ...).

## Out of scope (don't build these)
- AI or natural-language league creation
- Sending emails or texts
- Live score updates without refreshing the page
- Playoff brackets
- Checking a player's gender for men's or women's doubles
- Editing tournament or division settings after creation (fix mistakes in /admin). One exception: the superuser can raise a full division's max teams (spec 04).
- Dropouts in scramble divisions
- Showing calendar dates for each week
