# 11 - Full test pass, demo data, deploy, README

## Goal
Prove everything works on the live site, load demo data the grader can look at, and document it.

## Steps
1. Run `python manage.py check` and fix anything it reports.
2. Walk through this scenario locally. It matches the director's real league (4 weeks, 4 teams, max 12 games). Report anything that breaks, and fix it only after I agree.
   - A staff user (Staff status checked in /admin) creates "Waco Regional Tuesday League": 4 weeks, 4 courts, ranked by wins, players can't enter scores. They become its admin.
   - Adds a second admin (a regular, non-staff user).
   - A regular player sees no "Create a tournament" link.
   - Adds "Beginner Women's doubles": 4 teams max, 3 games per night, once.
   - Two players join with the code and make one team together. The admin adds three teams by name.
   - Build schedule (12 games), auto-assign courts, set week 1 times, copy week 1.
   - Enter scores for weeks 1 and 2. Drop one team. Check standings by hand.
   - Logged out, every page in the division still shows.
3. Leave that data in `db.sqlite3` as the demo. Every demo account uses a throwaway password. I'll list the logins in the README.
4. Commit, push, and check the live Render site with the same scenario (read-only checks are fine, since the disk resets).

## README.md
Write it in plain language, as me (a college student). Sections:
- What this is (two sentences).
- Live URL (I'll paste it).
- Demo logins: admin (a staff user, so it can create tournaments), player, spectator (no login needed).
- "What the director asked for" table: her request in one column, what the app does in the other. Use her requests from `CLAUDE.md` and the specs.
- Assumptions I made (copy from `CLAUDE.md`, reworded for a reader).
- Not built and why (copy the out-of-scope list, with one short reason each).
- How to run it locally.

No em dashes. No buzzwords.

## Acceptance tests
- Every step above works on the live URL.
- A logged-out visitor can reach the demo division from the home page in two clicks.
- On the live site, the demo player login has no "Create a tournament" link, and the demo admin login does.
