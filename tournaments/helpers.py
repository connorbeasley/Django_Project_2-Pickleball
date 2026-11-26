import random
import string
from .models import Tournament, Game


def is_admin(user, tournament):
    # The site's superuser can manage every tournament.
    if user.is_superuser:
        return True
    # Logged-out users are never admins.
    return user.is_authenticated and tournament.admins.filter(id=user.id).exists()


def is_member(user, tournament):
    # Logged-out users are never members.
    return user.is_authenticated and tournament.members.filter(id=user.id).exists()


def make_join_code():
    # Keep picking random codes until we find one no tournament uses yet.
    letters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choice(letters) for i in range(6))
        if not Tournament.objects.filter(join_code=code).exists():
            return code


def user_team_in_division(user, division):
    # Return the team this user is captain or partner of in this division, or None.
    for team in division.team_set.all():
        if team.captain == user or team.partner == user:
            return team
    return None


def registration_closed(division):
    # Registration closes once the schedule has games.
    return division.game_set.exists()


def round_robin_rounds(teams):
    # Copy the list so we don't change the caller's list.
    items = list(teams)
    # With an odd count, add None as a "bye". Whoever is paired with None sits out that round.
    if len(items) % 2 == 1:
        items.append(None)
    n = len(items)
    rounds = []
    for r in range(n - 1):
        # Pair the list from both ends: first with last, second with second-to-last, ...
        round_pairs = []
        for i in range(n // 2):
            pair = (items[i], items[n - 1 - i])
            # Skip the bye pair.
            if None not in pair:
                round_pairs.append(pair)
        rounds.append(round_pairs)
        # Rotate: keep the first item fixed, move the last item to position 1.
        items = [items[0]] + [items[-1]] + items[1:-1]
    return rounds


def build_schedule(teams, num_weeks, games_per_week):
    # Flatten the rounds into one long list of matchups, in order.
    matchups = []
    for round_pairs in round_robin_rounds(teams):
        matchups.extend(round_pairs)
    games = []
    index = 0
    for week in range(1, num_weeks + 1):
        for game_number in range(1, games_per_week + 1):
            # % wraps back to the start of the list when we run out of matchups.
            team1, team2 = matchups[index % len(matchups)]
            games.append((week, game_number, team1, team2))
            index += 1
    return games


def court_for(game_number, num_courts):
    # Games 1-4 get courts 1-4, then game 5 starts over at court 1.
    return ((game_number - 1) % num_courts) + 1


def minutes_of_day(t):
    # 6:15 PM -> 1095 minutes after midnight, so times are easy to compare.
    return t.hour * 60 + t.minute


def court_conflict(game, court, start_time):
    # Return another game in the same tournament and week whose time on this court overlaps, or None.
    new_start = minutes_of_day(start_time)
    new_end = new_start + game.division.game_length()
    # division__tournament follows the foreign keys Game -> Division -> Tournament.
    others = Game.objects.filter(division__tournament=game.division.tournament, week=game.week,
                                 court=court).exclude(id=game.id).exclude(start_time=None)
    for other in others:
        other_start = minutes_of_day(other.start_time)
        other_end = other_start + other.division.game_length()
        # Two games overlap when each one starts before the other one ends.
        if new_start < other_end and other_start < new_end:
            return other
    return None


def format_time(t):
    # 18:00 -> "6:00 PM" (lstrip removes the leading zero from "06").
    return t.strftime('%I:%M %p').lstrip('0')


def scores_entered(division):
    # True if any game in this division has a score.
    # team1_score__isnull=False means "team1_score is not empty".
    return division.game_set.filter(team1_score__isnull=False).exists()
