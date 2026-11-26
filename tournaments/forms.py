from django import forms
from .models import *


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['name', 'start_date', 'num_weeks', 'num_courts', 'ranking_method',
                  'players_enter_scores']
        labels = {
            'num_weeks': 'Number of weeks (1 for a one-day event)',
            'num_courts': 'Number of courts',
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
        fields = ['level', 'format', 'max_teams', 'games_per_week', 'max_meetings_per_night']
        labels = {
            'max_teams': 'Max teams (or players for scramble)',
            'games_per_week': 'Games per night in this division',
            'max_meetings_per_night': 'How many times can two teams play each other in one night',
        }
