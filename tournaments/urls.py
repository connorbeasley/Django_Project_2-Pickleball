from django.urls import path
from . import views

app_name = 'tournaments'
urlpatterns = [
    path('', views.index, name='index'),
    path('tournaments/new/', views.new_tournament, name='new_tournament'),
    path('tournaments/<int:tournament_id>/', views.tournament, name='tournament'),
    path('tournaments/<int:tournament_id>/admins/add/', views.add_admin, name='add_admin'),
    path('tournaments/<int:tournament_id>/divisions/new/', views.new_division, name='new_division'),
    path('divisions/<int:division_id>/', views.division, name='division'),
    path('join/', views.join_with_code, name='join_with_code'),
    path('join/<str:code>/', views.join_tournament, name='join_tournament'),
    path('divisions/<int:division_id>/teams/new/', views.new_team, name='new_team'),
    path('teams/<int:team_id>/join/', views.join_team, name='join_team'),
    path('divisions/<int:division_id>/max-teams/', views.edit_max_teams, name='edit_max_teams'),
]
