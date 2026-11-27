from django import forms
from .models import *


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['name', 'start_date', 'num_weeks', 'num_courts', 'ranking_method',
                  'players_enter_scores', 'game_minutes']
        labels = {
            'num_weeks': 'Number of weeks (1 for a one-day event)',
            'num_courts': 'Number of courts',
            'game_minutes': 'Game length in minutes (for every division)',
            'ranking_method': 'Rank teams by',
            'players_enter_scores': 'Let players enter their own scores',
        }
        # type="date" makes the browser show a date picker
        widgets = {'start_date': forms.DateInput(attrs={'type': 'date'})}


# A plain Form because no model is saved from it.
class AddAdminForm(forms.Form):
    username = forms.CharField(max_length=150)


class DivisionForm(forms.ModelForm):
    class Meta:
        model = Division
        fields = ['level', 'format', 'max_teams', 'games_per_week', 'max_meetings_per_night',
                  'game_minutes']
        labels = {
            'max_teams': 'Max teams (or players for scramble)',
            'games_per_week': 'Games per night in this division',
            'max_meetings_per_night': 'How many times can two teams play each other in one night',
            'game_minutes': "Game length in minutes (leave blank to use the tournament's)",
        }


# A plain Form because typing a code doesn't save a model.
class JoinCodeForm(forms.Form):
    code = forms.CharField(max_length=8)


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name']
        labels = {'name': 'Team name'}


class MaxTeamsForm(forms.ModelForm):
    class Meta:
        model = Division
        fields = ['max_teams']
        labels = {'max_teams': 'Max teams'}


class GameScheduleForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['court', 'start_time']
        # type="time" makes the browser show a time picker
        widgets = {'start_time': forms.TimeInput(attrs={'type': 'time'})}


# A plain Form because the first game time isn't saved on any model.
class AutoTimesForm(forms.Form):
    first_time = forms.TimeField(label='First game starts at',
                                 widget=forms.TimeInput(attrs={'type': 'time'}))


class ScoreForm(forms.ModelForm):
    # Declared here so both are required on this form, even though the model allows blanks.
    team1_score = forms.IntegerField(min_value=0)
    team2_score = forms.IntegerField(min_value=0)

    class Meta:
        model = Game
        fields = ['team1_score', 'team2_score']
