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
]
