# Waco Regional Pickleball League App

This is a Django web app I built for my class, based on what the Director of Pickleball at Waco Regional asked for. It lets her set up leagues and one-day tournaments, build schedules, assign courts and times, and record scores, and it lets anyone check schedules and standings without logging in.

## Live site

**URL:** https://django-project-2-pickleball.onrender.com/

The live site starts from the data in this repo every time Render restarts, so anything you change there goes away on the next restart.

## Demo logins

All demo accounts use the same password: `a;sldkfj`

| Username | What it is | What to try |
|---|---|---|
| `director` | The director. A staff user, so she can create tournaments, and the admin of both demo events. | Create a tournament, add a division, build a schedule, set times, enter scores, drop a team. |
| `coadmin` | A second admin of the demo league (not staff). | Manage the demo league. Can't create new tournaments. |
| `player1` | On the team "Dink Dynasty" in the league, and signed up as "Pat (player1)" in the scramble. | See schedules and standings. In the scramble, enter the score for one of Pat's unplayed games. No admin links, no "Create a tournament". |
| `player2` | player1's partner on "Dink Dynasty", and "Sam (player2)" in the scramble. | Same as player1, for Sam's scramble games. |
| Spectator | No login needed. | Open the home page, click an event, then its division. |

There are two demo events:

- **Waco Regional Tuesday League**: 4 weeks, 4 courts, one division (Beginner Women's doubles) with 4 teams. Weeks 1 and 2 are scored, and "Lob Stars" dropped out, so their later games show as forfeits. Players can't enter scores here, only admins.
- **Waco Regional Friday Scramble**: a one-night scramble with 8 players. Every player partners every other player once over 7 rounds (14 games), starting at 6:00 PM with a new round every 30 minutes. Rounds 1 to 3 are scored, plus one round 4 game that player1 entered. Players can enter their own scores here, and the app checks them (games to 11, win by 2).

## What the director asked for

| What she asked for | What the app does |
|---|---|
| Run multi-week leagues and one-day tournaments | One "tournament" covers both. A one-day event is just a tournament with 1 week. |
| Different divisions (skill levels, mixed, men's, women's) | Each tournament has divisions, like "Beginner Women's doubles", each with its own teams, schedule, and standings. |
| Let players sign up | Players join with a code or a join link, then create a team or join one as the partner. |
| Let her type in teams herself | Admins can add teams by name, no player accounts needed. |
| Build the schedule for her | One button builds a round robin for every week, so teams rotate opponents. |
| Limit how often two teams meet in one night | Each division sets "once" or "twice" a night, and the app refuses a schedule that breaks it. |
| She only has 4 courts | Courts and times can be set per game. The app refuses a court that doesn't exist or a game that overlaps another game on the same court. |
| Don't make her set every week by hand | "Copy week 1 to all weeks", "Auto-assign courts", and "Auto-fill times" (games start in waves, spaced by the game length). |
| Record scores | Admins can always enter or fix scores. For big events she can let players enter their own game's score. |
| Standings | Each division ranks teams by wins or by total points (her choice per tournament), with point differential as the last tie-breaker. |
| Handle teams that drop out | Dropping a team turns its unplayed games into forfeits. Games already played stay as they were. |
| People who just want to watch | Schedules, scores, and standings are public. No login needed. |
| Scrambles | A scramble division where players sign up alone and every player partners every other player once. |

### Things I added while building it

- Only staff users (set in /admin) can create tournaments, so random accounts can't fill the home page.
- The site superuser can manage every tournament. When a division is full, the superuser can raise its max teams and then add the team.
- Game length is saved per tournament, and a division can override it. The court check uses it, so a 6:15 game can't overlap a 6:00 game on the same court.
- "Points to win" (usually 11) and "win by 2" are set per tournament, and a division can override them. When players enter their own scores, impossible scores like 8 - 5 or 11 - 10 are refused. Admins can enter anything, for example a game stopped early.
- Ties are refused everywhere, since pickleball games can't end tied.
- After the schedule is built, admins can still add a late team until scores are entered, then rebuild.

## Assumptions I made

I made these choices where the requirements didn't say. Each one can change if the director wants something different.

1. A league and a one-day tournament are the same thing in the app. A one-day event has 1 week.
2. Each division is scheduled on its own. The app makes a round robin list of matchups and keeps cycling through it until every week is full, so opponents rotate across the league.
3. "Once" or "twice" a night limits how many times the same two teams can play each other in one night.
4. "Copy week 1" copies courts and start times to the same game numbers in later weeks. It never changes who plays whom.
5. A forfeit counts as a win for the opponent and a loss for the team that dropped out, recorded as the division's points to win to 0 (usually 11 to 0).
6. Spectators see new scores when they refresh the page.
7. To invite people, the admin copies the join link and sends it herself by text or email.
8. Once a division's schedule is built, players can't sign up anymore. Admins can still add a late team until scores are entered.
9. When players enter their own scores, the first score entered stands. Admins can always change it.
10. Teams an admin types in don't need player accounts.
11. A scramble is one night, and it needs a player count that divides by 4 (4, 8, 12, ...).

## Not built, and why

| Not built | Why |
|---|---|
| AI or typing a league description in plain English | Out of scope for this class project. The forms are quick to fill in. |
| Sending emails or texts | Needs an outside service. The admin copies the join link and sends it herself. |
| Live score updates without refreshing | Needs JavaScript, and the class rules for this project are Django templates only. Refreshing shows new scores. |
| Playoff brackets | The director asked for league play. Standings already give the seeds. |
| Checking a player's gender for men's or women's doubles | Not something the app should judge. The director handles it in person. |
| Editing tournament or division settings after creation | Keeps the app simple. Mistakes can be fixed in /admin. (The one exception is raising a full division's max teams.) |
| Dropouts in scramble | Every player partners everyone, so one dropout breaks the whole night's pairings. |
| Calendar dates for each week | The start date is shown. Weeks are numbered, which is how the league is run. |

## How to run it locally

You need Python 3.12 (3.11 should also work).

```
python -m venv djangovenv
djangovenv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then open http://127.0.0.1:8000/ and log in with one of the demo accounts above. On Mac or Linux, activate with `source djangovenv/bin/activate` instead.

To make your own admin account for /admin, run `python manage.py createsuperuser`.
