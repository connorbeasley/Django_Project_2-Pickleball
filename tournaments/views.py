from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404

from .models import *
from .forms import *
from .helpers import is_admin, make_join_code


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
    # join link added in spec 04
    context = {'tournament': tournament, 'divisions': divisions, 'admins': admins,
               'user_is_admin': user_is_admin}
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
    context = {'division': division, 'teams': teams}
    return render(request, 'tournaments/division.html', context)
