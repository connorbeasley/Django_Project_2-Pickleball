from django.db import models
from django.contrib.auth.models import User


class Tournament(models.Model):
    RANKING_CHOICES = [('wins', 'Wins and losses'), ('points', 'Total points')]

    name = models.CharField(max_length=100)
    # First night of play
    start_date = models.DateField()
    # 1 means a one-day event
    num_weeks = models.PositiveIntegerField()
    num_courts = models.PositiveIntegerField(default=4)
    ranking_method = models.CharField(max_length=10, choices=RANKING_CHOICES, default='wins')
    players_enter_scores = models.BooleanField(default=False)
    # How long one game lasts, for every division (a division can override it)
    game_minutes = models.PositiveIntegerField(default=30)
    # Set by the view, not the form
    join_code = models.CharField(max_length=8, unique=True)
    admins = models.ManyToManyField(User, related_name='admin_tournaments')
    members = models.ManyToManyField(User, related_name='joined_tournaments', blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Division(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    FORMAT_CHOICES = [
        ('mixed', 'Mixed doubles'),
        ('mens', "Men's doubles"),
        ('womens', "Women's doubles"),
        ('scramble', 'Scramble'),
    ]
    MEETING_CHOICES = [(1, 'Once'), (2, 'Twice')]

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES)
    # For scramble this means max players
    max_teams = models.PositiveIntegerField()
    # Total games in this division each night
    games_per_week = models.PositiveIntegerField()
    max_meetings_per_night = models.PositiveIntegerField(choices=MEETING_CHOICES, default=1)
    # Blank means "use the tournament's game length"
    game_minutes = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        # For example: "Beginner Women's doubles"
        return f"{self.get_level_display()} {self.get_format_display()}"

    def game_length(self):
        # This division's own length if set, otherwise the tournament's.
        if self.game_minutes:
            return self.game_minutes
        return self.tournament.game_minutes


class Team(models.Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    captain = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='captain_teams')
    partner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='partner_teams')
    dropped = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Game(models.Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    week = models.PositiveIntegerField()
    # Position within the week: 1, 2, 3...
    game_number = models.PositiveIntegerField()
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team1_games')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team2_games')
    court = models.PositiveIntegerField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    team1_score = models.PositiveIntegerField(null=True, blank=True)
    team2_score = models.PositiveIntegerField(null=True, blank=True)
    forfeit = models.BooleanField(default=False)

    def __str__(self):
        return f"Week {self.week}: {self.team1} vs {self.team2}"

    def winner(self):
        # No winner until both scores are in.
        if self.team1_score is None or self.team2_score is None:
            return None
        if self.team1_score > self.team2_score:
            return self.team1
        if self.team2_score > self.team1_score:
            return self.team2
        # A tie has no winner. (Pickleball games can't end tied, but this avoids a wrong answer.)
        return None
