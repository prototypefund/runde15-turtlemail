from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as _LoginView
from django.shortcuts import redirect
from django.views.generic import View, CreateView, TemplateView
from django.urls import reverse_lazy, reverse

from .forms import UserCreationForm, AuthenticationForm


class IndexView(View):
    def post(self, request):
        return redirect(reverse("deliveries"), permanent=True)


class DeliveriesView(LoginRequiredMixin, TemplateView):
    template_name = "turtlemail/deliveries.jinja"


class StaysView(LoginRequiredMixin, TemplateView):
    template_name = "turtlemail/stays.jinja"


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "turtlemail/profile.jinja"


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup_and_login.jinja"


class LoginView(_LoginView):
    authentication_form = AuthenticationForm
    template_name = "registration/signup_and_login.jinja"
