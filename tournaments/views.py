import datetime

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
    # A template can't call can_enter_score(user, game), so work it out here for each game.
    game_rows = []
    for game in division.game_set.order_by('week', 'game_number'):
        game_rows.append((game, can_enter_score(request.user, game)))
    context = {
        'division': division,
        'teams': teams,
        'user_is_admin': is_admin(request.user, tournament),
        'user_is_member': is_member(request.user, tournament),
        'user_team': user_team_in_division(request.user, division),
        'closed': registration_closed(division),
        'game_rows': game_rows,
        'standings_rows': standings(division),
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
    # Once the schedule is built, only admins can add teams, and only until scores are entered.
    if registration_closed(division) and not user_is_admin:
        messages.error(request, 'Registration is closed.')
        return redirect('tournaments:division', division_id=division.id)
    if scores_entered(division):
        messages.error(request, 'Scores have been entered, so no more teams can be added.')
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
            # A team added after the schedule was built has no games yet.
            if registration_closed(division):
                messages.info(request, 'Team added. Rebuild the schedule to give them games.')
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
        if scores_entered(division):
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


@login_required
def edit_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    tournament = game.division.tournament
    if not is_admin(request.user, tournament):
        raise Http404

    if request.method != 'POST':
        # GET: show the form filled in with the current court and time
        form = GameScheduleForm(instance=game)
    else:
        # POST: save the new court and time over the same game
        form = GameScheduleForm(instance=game, data=request.POST)
        if form.is_valid():
            court = form.cleaned_data['court']
            start_time = form.cleaned_data['start_time']
            if court is not None and (court < 1 or court > tournament.num_courts):
                form.add_error(None, f'This tournament only has {tournament.num_courts} courts.')
            # Only check for a clash when both a court and a time are filled in.
            elif court is not None and start_time is not None:
                other = court_conflict(game, court, start_time)
                if other:
                    form.add_error(None, f'Court {court} is already used by {other.division} '
                                         f'from {format_time(other.start_time)} in week {game.week} '
                                         f'({other.division.game_length()} minute games).')
            if not form.errors:
                form.save()
                return redirect('tournaments:division', division_id=game.division.id)

    context = {'game': game, 'form': form}
    return render(request, 'tournaments/edit_game.html', context)


@login_required
def auto_courts(request, division_id):
    division = get_object_or_404(Division, id=division_id)
    if not is_admin(request.user, division.tournament):
        raise Http404
    if request.method == 'POST':
        num_courts = division.tournament.num_courts
        for game in division.game_set.all():
            game.court = court_for(game.game_number, num_courts)
            game.save()
        messages.success(request, 'Courts assigned.')
    return redirect('tournaments:division', division_id=division.id)


@login_required
def copy_week_one(request, division_id):
    division = get_object_or_404(Division, id=division_id)
    if not is_admin(request.user, division.tournament):
        raise Http404
    if request.method == 'POST':
        # Look up week 1 games by their game number, like {1: game, 2: game, ...}
        week_one = {}
        for game in division.game_set.filter(week=1):
            week_one[game.game_number] = game
        # week__gt=1 means "week greater than 1".
        for game in division.game_set.filter(week__gt=1):
            source = week_one.get(game.game_number)
            if source:
                game.court = source.court
                game.start_time = source.start_time
                game.save()
        messages.success(request, 'Copied week 1 times and courts to every week.')
    return redirect('tournaments:division', division_id=division.id)


@login_required
def auto_times(request, division_id):
    division = get_object_or_404(Division, id=division_id)
    if not is_admin(request.user, division.tournament):
        raise Http404

    if request.method != 'POST':
        # GET: show an empty form
        form = AutoTimesForm()
    else:
        # POST: fill in a court and time for every game
        form = AutoTimesForm(data=request.POST)
        if form.is_valid():
            first_time = form.cleaned_data['first_time']
            # Space the waves by this division's game length.
            minutes = division.game_length()
            num_courts = division.tournament.num_courts
            games = division.game_set.all()
            for game in games:
                game.court = court_for(game.game_number, num_courts)
                # Games 1-4 are wave 0, games 5-8 are wave 1, and so on (with 4 courts).
                wave = (game.game_number - 1) // num_courts
                # Python can't add minutes to a plain time, so attach a date, add, then take the time back.
                start = datetime.datetime.combine(datetime.date.today(), first_time)
                game.start_time = (start + datetime.timedelta(minutes=wave * minutes)).time()
                game.save()

            # Warn about clashes with other divisions in the same tournament.
            clashes = 0
            for game in games:
                if court_conflict(game, game.court, game.start_time):
                    clashes += 1
            if clashes:
                messages.warning(request, f'Times filled in, but {clashes} games share a court and '
                                          f'time with another division. Edit those games to fix them.')
            else:
                messages.success(request, 'Times filled in.')
            return redirect('tournaments:division', division_id=division.id)

    context = {'division': division, 'form': form}
    return render(request, 'tournaments/auto_times.html', context)


@login_required
def enter_score(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    if not can_enter_score(request.user, game):
        raise Http404

    if request.method != 'POST':
        # GET: show the form (filled in if a score already exists)
        form = ScoreForm(instance=game)
    else:
        # POST: save the score over the same game
        form = ScoreForm(instance=game, data=request.POST)
    # Label each box with the team's name instead of "Team1 score".
    form.fields['team1_score'].label = game.team1.name
    form.fields['team2_score'].label = game.team2.name

    if request.method == 'POST' and form.is_valid():
        if form.cleaned_data['team1_score'] == form.cleaned_data['team2_score']:
            form.add_error(None, "Scores can't be tied.")
        else:
            form.save()
            return redirect('tournaments:division', division_id=game.division.id)

    context = {'game': game, 'form': form}
    return render(request, 'tournaments/enter_score.html', context)
