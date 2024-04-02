from django.http.request import HttpRequest
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse


def index(request: HttpRequest):
    return redirect(reverse("deliveries"), permanent=True)


def deliveries(request: HttpRequest):
    return TemplateResponse(request, "turtlemail/deliveries.jinja")


def trips(request: HttpRequest):
    return TemplateResponse(request, "turtlemail/trips.jinja")


def profile(request: HttpRequest):
    return TemplateResponse(request, "turtlemail/profile.jinja")
