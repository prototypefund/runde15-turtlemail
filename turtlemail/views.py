from django.http.request import HttpRequest
from django.contrib.auth.views import LoginView as _LoginView
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.generic import CreateView
from django.urls import reverse_lazy, reverse

from .forms import UserCreationForm, AuthenticationForm


def index(request: HttpRequest):
    return redirect(reverse("deliveries"), permanent=True)


def deliveries(request: HttpRequest):
    return TemplateResponse(request, "turtlemail/deliveries.jinja")


def trips(request: HttpRequest):
    return TemplateResponse(request, "turtlemail/trips.jinja")


def profile(request: HttpRequest):
    return TemplateResponse(request, "turtlemail/profile.jinja")


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup_and_login.jinja"


class LoginView(_LoginView):
    authentication_form = AuthenticationForm
    template_name = "registration/signup_and_login.jinja"
