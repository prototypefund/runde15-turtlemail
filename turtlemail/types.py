from django.http import HttpRequest

from turtlemail.models import User


class AuthedHttpRequest(HttpRequest):
    """Used for views that use LoginRequiredMixin. These classes will always receive a user that is authenticated."""

    user: User
