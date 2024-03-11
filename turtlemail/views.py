from django.http.request import HttpRequest
from django.template.response import TemplateResponse


def index(request: HttpRequest):
    return TemplateResponse(request, "turtlemail/index.jinja")
