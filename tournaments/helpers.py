import random
import string
from .models import Tournament


def is_admin(user, tournament):
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
