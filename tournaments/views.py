from django.shortcuts import render


def index(request):
    # The home page for the app.
    return render(request, 'tournaments/index.html')
