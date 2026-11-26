# 10 - Scramble (nice-to-have)

Only start this after specs 00-09 pass their tests and the site is deployed.

## Goal
In a scramble, players sign up alone. Each round, players get a new partner. With 8 players there are 7 rounds, and every player partners every other player once.

## Reuse what exists
- A scramble sign-up is a `Team` with only a `captain`. The team name is the player's name. No partners join.
- Admins can still add players by typing a name (same as spec 04).
- Pairing reuses `round_robin_rounds` from spec 05: run it on the list of players. Each "pair" it returns is two partners, and each round gives every player one partner.

## New model (add to models.py)
### ScrambleGame
| Field | Type | Notes |
|---|---|---|
| `division` | ForeignKey(Division) | `on_delete=models.CASCADE` |
| `round_number` | PositiveIntegerField | |
| `game_number` | PositiveIntegerField | Position within the round |
| `a1`, `a2` | ForeignKey(Team) | Side A partners. `on_delete=models.CASCADE`, related names `scramble_a1`, `scramble_a2` |
| `b1`, `b2` | ForeignKey(Team) | Side B partners. Related names `scramble_b1`, `scramble_b2` |
| `court` | PositiveIntegerField | `null=True, blank=True` |
| `start_time` | TimeField | `null=True, blank=True` |
| `a_score`, `b_score` | PositiveIntegerField | `null=True, blank=True` |

Register it in /admin.

## helpers.py
`build_scramble(players)`:
1. `rounds = round_robin_rounds(players)`.
2. In each round, take the partner pairs two at a time: pair 1 plays pair 2, pair 3 plays pair 4, and so on.
3. Return tuples `(round_number, game_number, a1, a2, b1, b2)`.

`scramble_standings(division)`: one row per player: played, wins, losses, points. A player on the winning side gets the win and that side's score as points. Sort the same way as `standings`.

## Page changes
- Division page for scramble: Teams section is titled "Players". Button text "Sign up". No "Join as partner" buttons. No "Drop" links.
- `new_team` in a scramble division: the form label is "Your name" (or "Player name" for admins).
- `generate_schedule` in a scramble division: require at least 4 players and a count divisible by 4 ("Scramble needs 4, 8, 12... players."). Delete old `ScrambleGame` rows, create new ones from `build_scramble`, redirect.
- Schedule table for scramble: "Round N" headings, columns Game #, Time, Court, Side A ("Amy and Ben"), Score, Side B.
- Scores: add `enter_scramble_score` and `edit_scramble_game` views that work like specs 06 and 07, with the same tie and court checks. Players may enter a score if they're one of the four players and `players_enter_scores` is on.
- `auto_courts` and `copy_week_one` don't apply to scramble. Hide those buttons. Auto-assign courts can use `court_for` on `game_number` if it's quick.
- Standings use `scramble_standings`.

## Acceptance tests
- 8 players: build gives 7 rounds with 2 games each (14 games). Checking by hand, each player has every other player as a partner exactly once.
- 6 players: error about the player count.
- Enter scores: the scramble standings table updates per player.
- Doubles divisions in the same tournament still work exactly as before.
