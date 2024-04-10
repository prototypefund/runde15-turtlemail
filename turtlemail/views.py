import secrets
from django.contrib.auth.views import LoginView as _LoginView
from django.http import HttpRequest
from django.shortcuts import redirect
from django.views.generic import CreateView, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy

from turtlemail.models import Packet, User

from .forms import UserCreationForm, AuthenticationForm, PacketForm


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


class CreatePacketView(LoginRequiredMixin, TemplateView):
    template_name = "turtlemail/create_packet_form.jinja"

    def get(self, request, *args, **kwargs):
        form = PacketForm()
        context = self.get_context_data(**kwargs)
        context["form"] = form
        return self.render_to_response(context)

    def post(self, request: HttpRequest, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = PacketForm(request.POST)
        context["form"] = form
        if not form.is_valid():
            return self.render_to_response(context)

        recipient_username = form.cleaned_data.get("recipient_username")
        if recipient_username is not None and len(recipient_username) > 0:
            context["search_results"] = User.objects.search_for_recipient(
                recipient_username, request.user.id
            )

        recipient_id = form.cleaned_data.get("recipient_id")
        if recipient_id is not None:
            context["recipient"] = User.objects.get(id=recipient_id)

        if not form.cleaned_data["confirm_recipient"]:
            return self.render_to_response(context)

        # TODO rename receiver to recipient
        human_id = secrets.token_hex(8)
        packet = Packet(
            sender=request.user,
            human_id=human_id,
            receiver=context["recipient"],
        )
        packet.save()
        return redirect(to=reverse("packet_detail", args=(packet.human_id,)))


class PacketDetailView(LoginRequiredMixin, DetailView):
    template_name = "turtlemail/packet_detail.jinja"
    model = Packet
    slug_field = "human_id"
