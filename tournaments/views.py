from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404
from django.urls import reverse

from .models import *
from .forms import *
from .helpers import *


def index(request):
    # The home page lists every tournament, newest first.
    tournaments = Tournament.objects.order_by('-date_added')
    context = {'tournaments': tournaments}
    return render(request, 'tournaments/index.html', context)


@login_required
def new_tournament(request):
    # Only staff (the director and her helpers) can create tournaments.
    if not request.user.is_staff:
        raise Http404

    if request.method != 'POST':
        # GET: show an empty form
        form = TournamentForm()
    else:
        # POST: save what the user typed
        form = TournamentForm(data=request.POST)
        if form.is_valid():
            # commit=False lets us fill in the join code, which the user doesn't type
            new_tournament = form.save(commit=False)
            new_tournament.join_code = make_join_code()
            new_tournament.save()
            # Many-to-many fields can only be added to after the first save.
            new_tournament.admins.add(request.user)
            new_tournament.members.add(request.user)
            return redirect('tournaments:tournament', tournament_id=new_tournament.id)

    context = {'form': form}
    return render(request, 'tournaments/new_tournament.html', context)


def tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    divisions = tournament.division_set.all()
    admins = tournament.admins.order_by('username')
    # Only admins see the join code and the "Add an admin" link.
    user_is_admin = is_admin(request.user, tournament)
    # The full link (with http://...) that the director can text or email.
    join_link = request.build_absolute_uri(
        reverse('tournaments:join_tournament', args=[tournament.join_code]))
    context = {'tournament': tournament, 'divisions': divisions, 'admins': admins,
               'user_is_admin': user_is_admin, 'join_link': join_link}
    return render(request, 'tournaments/tournament.html', context)


@login_required
def add_admin(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if not is_admin(request.user, tournament):
        raise Http404

    if request.method != 'POST':
        # GET: show an empty form
        form = AddAdminForm()
    else:
        # POST: look up the username they typed
        form = AddAdminForm(data=request.POST)
        if form.is_valid():
            # .first() gives None instead of crashing when no user matches
            user = User.objects.filter(username=form.cleaned_data['username']).first()
            if user is None:
                form.add_error('username', 'No user with that username.')
            else:
                tournament.admins.add(user)
                tournament.members.add(user)
                messages.success(request, f'{user.username} is now an admin.')
                return redirect('tournaments:tournament', tournament_id=tournament.id)

    context = {'tournament': tournament, 'form': form}
    return render(request, 'tournaments/add_admin.html', context)


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


def division(request, division_id):
    # get_object_or_404 shows a "not found" page for a bad id instead of crashing.
    division = get_object_or_404(Division, id=division_id)
    teams = division.team_set.order_by('name')
    tournament = division.tournament
    context = {
        'division': division,
        'teams': teams,
        'user_is_admin': is_admin(request.user, tournament),
        'user_is_member': is_member(request.user, tournament),
        'user_team': user_team_in_division(request.user, division),
        'closed': registration_closed(division),
        'games': division.game_set.order_by('week', 'game_number'),
    }
    return render(request, 'tournaments/division.html', context)


@login_required
def join_with_code(request):
    if request.method != 'POST':
        # GET: show an empty form
        form = JoinCodeForm()
    else:
        # POST: look up the code they typed
        form = JoinCodeForm(data=request.POST)
        if form.is_valid():
            # Codes are stored in uppercase, so "abc123" still works.
            code = form.cleaned_data['code'].upper()
            tournament = Tournament.objects.filter(join_code=code).first()
            if tournament is None:
                form.add_error('code', "That code doesn't match any tournament.")
            else:
                tournament.members.add(request.user)
                messages.success(request, f'You joined {tournament.name}.')
                return redirect('tournaments:tournament', tournament_id=tournament.id)

    context = {'form': form}
    return render(request, 'tournaments/join_with_code.html', context)


@login_required
def join_tournament(request, code):
    # This is the link the director texts or emails.
    tournament = get_object_or_404(Tournament, join_code=code.upper())
    tournament.members.add(request.user)
    messages.success(request, f'You joined {tournament.name}.')
    return redirect('tournaments:tournament', tournament_id=tournament.id)


@login_required
def new_team(request, division_id):
    division = get_object_or_404(Division, id=division_id)
    user_is_admin = is_admin(request.user, division.tournament)
    if not user_is_admin and not is_member(request.user, division.tournament):
        raise Http404

    # Refuse when the team can't be added, and explain why.
    if registration_closed(division):
        messages.error(request, 'Registration is closed.')
        return redirect('tournaments:division', division_id=division.id)
    if division.team_set.count() >= division.max_teams:
        # The superuser gets a chance to raise the limit instead of a dead end.
        if request.user.is_superuser:
            messages.info(request, 'This division is full. Raise max teams to add another team.')
            return redirect('tournaments:edit_max_teams', division_id=division.id)
        messages.error(request, 'This division is full.')
        return redirect('tournaments:division', division_id=division.id)
    if not user_is_admin and user_team_in_division(request.user, division):
        messages.error(request, "You're already on a team in this division.")
        return redirect('tournaments:division', division_id=division.id)

    if request.method != 'POST':
        # GET: show an empty form
        form = TeamForm()
    else:
        # POST: save what the user typed
        form = TeamForm(data=request.POST)
        if form.is_valid():
            new_team = form.save(commit=False)
            new_team.division = division
            # An admin is typing in someone else's team, so only players become captain.
            if not user_is_admin:
                new_team.captain = request.user
            new_team.save()
            return redirect('tournaments:division', division_id=division.id)

    context = {'division': division, 'form': form}
    return render(request, 'tournaments/new_team.html', context)


@login_required
def join_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    division = team.division
    if request.method == 'POST':
        if not is_member(request.user, division.tournament):
            messages.error(request, 'Join the tournament first.')
        elif registration_closed(division):
            messages.error(request, 'Registration is closed.')
        elif user_team_in_division(request.user, division):
            messages.error(request, "You're already on a team in this division.")
        # Only a team with a captain and no partner is looking for a partner.
        elif team.captain is None or team.partner is not None:
            messages.error(request, "This team isn't looking for a partner.")
        else:
            team.partner = request.user
            team.save()
            messages.success(request, f'You joined {team.name}.')
    return redirect('tournaments:division', division_id=division.id)


@login_required
def edit_max_teams(request, division_id):
    division = get_object_or_404(Division, id=division_id)
    # Only the site superuser can raise a division's team limit.
    if not request.user.is_superuser:
        raise Http404
    team_count = division.team_set.count()

    if request.method != 'POST':
        # GET: show the form filled in with the current max
        form = MaxTeamsForm(instance=division)
    else:
        # POST: save the new max over the same division
        form = MaxTeamsForm(instance=division, data=request.POST)
        if form.is_valid():
            if form.cleaned_data['max_teams'] <= team_count:
                form.add_error('max_teams',
                               f'Set it higher than the {team_count} teams already signed up.')
            else:
                form.save()
                messages.success(request, f'Max teams is now {division.max_teams}.')
                # Go straight to adding the team they wanted to add.
                return redirect('tournaments:new_team', division_id=division.id)

    context = {'division': division, 'form': form, 'team_count': team_count}
    return render(request, 'tournaments/edit_max_teams.html', context)


@login_required
def generate_schedule(request, division_id):
    division = get_object_or_404(Division, id=division_id)
    if not is_admin(request.user, division.tournament):
        raise Http404
    if request.method == 'POST':
        if division.format == 'scramble':
            messages.error(request, 'Scramble schedules come in a later update.')
            return redirect('tournaments:division', division_id=division.id)
        # team1_score__isnull=False means "this game has a score".
        if division.game_set.filter(team1_score__isnull=False).exists():
            messages.error(request, "Scores have been entered, so the schedule can't be rebuilt.")
            return redirect('tournaments:division', division_id=division.id)
        teams = division.team_set.filter(dropped=False).order_by('id')
        n = teams.count()
        if n < 2:
            messages.error(request, 'Add at least 2 teams first.')
            return redirect('tournaments:division', division_id=division.id)
        # Each pair can meet at most max_meetings_per_night times in one night.
        pairs = n * (n - 1) // 2
        max_games = pairs * division.max_meetings_per_night
        if division.games_per_week > max_games:
            messages.error(request, f'With {n} teams, each night can have at most {max_games} games.')
            return redirect('tournaments:division', division_id=division.id)

        # Start fresh, then save one Game for each scheduled matchup.
        division.game_set.all().delete()
        schedule = build_schedule(teams, division.tournament.num_weeks, division.games_per_week)
        for week, game_number, team1, team2 in schedule:
            Game.objects.create(division=division, week=week, game_number=game_number,
                                team1=team1, team2=team2)
        messages.success(request, f'Schedule created: {len(schedule)} games.')
    return redirect('tournaments:division', division_id=division.id)
