# 01 - Models

## Goal
Create all the database tables for doubles leagues in `tournaments/models.py`, plus the first helpers. No pages yet.

## Models
Import `User` from `django.contrib.auth.models`. Every model gets a `__str__` method.

### Tournament
| Field | Type | Notes |
|---|---|---|
| `name` | CharField(max_length=100) | |
| `start_date` | DateField | First night of play |
| `num_weeks` | PositiveIntegerField | 1 means a one-day event |
| `num_courts` | PositiveIntegerField | default 4 |
| `ranking_method` | CharField(max_length=10) | choices: `('wins', 'Wins and losses')`, `('points', 'Total points')`. Default `'wins'` |
| `players_enter_scores` | BooleanField | default False. Turn on for big tournaments |
| `game_minutes` | PositiveIntegerField | default 30. How long one game lasts, for every division (added during spec 06) |
| `join_code` | CharField(max_length=8, unique=True) | Set by the view, not the form |
| `admins` | ManyToManyField(User) | `related_name='admin_tournaments'` |
| `members` | ManyToManyField(User) | `related_name='joined_tournaments'`, `blank=True` |
| `date_added` | DateTimeField | `auto_now_add=True` |

`__str__` returns `self.name`.

### Division
| Field | Type | Notes |
|---|---|---|
| `tournament` | ForeignKey(Tournament) | `on_delete=models.CASCADE` |
| `level` | CharField(max_length=20) | choices: beginner, intermediate, advanced (labels capitalized) |
| `format` | CharField(max_length=20) | choices: `('mixed', 'Mixed doubles')`, `('mens', "Men's doubles")`, `('womens', "Women's doubles")`, `('scramble', 'Scramble')` |
| `max_teams` | PositiveIntegerField | For scramble this means max players |
| `games_per_week` | PositiveIntegerField | Total games in this division each night |
| `max_meetings_per_night` | PositiveIntegerField | choices: `(1, 'Once')`, `(2, 'Twice')`. Default 1 |
| `game_minutes` | PositiveIntegerField | `null=True, blank=True`. Blank means use the tournament's length (added during spec 06) |

`__str__` returns something like `"Beginner Women's doubles"` using `get_level_display()` and `get_format_display()`.

Add a method `game_length(self)` that returns `game_minutes` if set, otherwise `self.tournament.game_minutes`.

### Team
| Field | Type | Notes |
|---|---|---|
| `division` | ForeignKey(Division) | `on_delete=models.CASCADE` |
| `name` | CharField(max_length=100) | |
| `captain` | ForeignKey(User) | `null=True, blank=True, on_delete=models.SET_NULL, related_name='captain_teams'` |
| `partner` | ForeignKey(User) | same options, `related_name='partner_teams'` |
| `dropped` | BooleanField | default False |

`__str__` returns `self.name`.

### Game
| Field | Type | Notes |
|---|---|---|
| `division` | ForeignKey(Division) | `on_delete=models.CASCADE` |
| `week` | PositiveIntegerField | 1, 2, 3... |
| `game_number` | PositiveIntegerField | Position within the week: 1, 2, 3... |
| `team1` | ForeignKey(Team) | `on_delete=models.CASCADE, related_name='team1_games'` |
| `team2` | ForeignKey(Team) | `on_delete=models.CASCADE, related_name='team2_games'` |
| `court` | PositiveIntegerField | `null=True, blank=True` |
| `start_time` | TimeField | `null=True, blank=True` |
| `team1_score` | PositiveIntegerField | `null=True, blank=True` |
| `team2_score` | PositiveIntegerField | `null=True, blank=True` |
| `forfeit` | BooleanField | default False |

`__str__` returns `f"Week {self.week}: {self.team1} vs {self.team2}"`.

Add a method `winner(self)` that returns `team1` or `team2` based on the higher score, or `None` if either score is missing.

## Admin
Register all four models in `tournaments/admin.py` so I can fix data in /admin.

## helpers.py
Create `tournaments/helpers.py` with:
- `is_admin(user, tournament)`: True if the user is logged in and in `tournament.admins`.
- `is_member(user, tournament)`: True if the user is logged in and in `tournament.members`.
- `make_join_code()`: returns a random 6-character code of uppercase letters and digits (use `random` and `string`). Loop until no Tournament already has that code.

## Acceptance tests
- `makemigrations` and `migrate` run with no errors.
- In /admin, I can create a Tournament, a Division, two Teams, and a Game, and each shows a readable name in the list.
- In the shell (`python manage.py shell`), `make_join_code()` returns a 6-character code.
