import random
import string
from .models import Tournament


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
