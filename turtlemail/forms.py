import datetime
from typing import Any

from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.forms import (
    AuthenticationForm as _AuthenticationForm,
)
from django.contrib.auth.forms import (
    BaseUserCreationForm,
    UsernameField,
)
from django.forms import ValidationError
from django.forms.renderers import Jinja2
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from turtlemail import widgets

from .models import Invite, Location, Route, RouteStep, Stay, User, UserSettings


class UserCreationForm(BaseUserCreationForm):
    username = UsernameField(
        label=_("Username"),
        widget=forms.TextInput(
            attrs={"autofocus": True, "class": "input input-bordered"}
        ),
    )
    email = forms.CharField(
        label=_("E-mail"),
        widget=forms.EmailInput(
            attrs={"autofocus": True, "class": "input input-bordered"}
        ),
    )
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "class": "input input-bordered",
            }
        ),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "class": "input input-bordered",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ["username", "password1", "password2"]:
            self.fields[fieldname].help_text = None
        self.action = _("Sign Up")
        self.other_form_url = reverse("login")
        self.other_form_link_text = _("Log into an existing account")


class AuthenticationForm(_AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(
            attrs={"autofocus": True, "class": "input input-bordered"}
        ),
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "class": "input input-bordered",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action = _("Log In")
        self.other_form_url = reverse("signup")
        self.other_form_link_text = _("Create a new account")
        if (email := self.request.GET.get("email")) is not None:
            self.initial["username"] = email


class PacketForm(forms.Form):
    recipient_username = forms.CharField(
        widget=widgets.TextInput(),
        label=_("Who would you like to send your delivery to?"),
        required=False,
    )
    recipient_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    clear_recipient_id = forms.BooleanField(
        required=False, label=_("Clear selected recipient")
    )
    confirm_recipient = forms.BooleanField(
        required=False, label=_("Proceed with this recipient")
    )

    def clean(self):
        if self.cleaned_data["clear_recipient_id"]:
            self.cleaned_data["recipient_id"] = None


class InviteUserForm(forms.ModelForm):
    class Meta:
        model = Invite
        fields = ("email",)
        labels = {
            "email": _("Please enter the email of the person you'd like to invite:")
        }


class UserSettingFormRenderer(Jinja2):
    form_template_name = "_form_div.jinja"


class UserSettingsForm(forms.ModelForm):
    default_renderer = UserSettingFormRenderer

    class Meta:
        model = UserSettings
        fields = (
            "wants_email_notifications_chat",
            "wants_email_notifications_requests",
        )
        labels = {
            "wants_email_notifications_chat": _(
                "I want to be notified by email, if somebody messages me in a chat."
            ),
            "wants_email_notifications_requests": _(
                "I want to be notified by email, if turtlemail systems requests feedback for new routing requests."
            ),
        }


class StayForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["location"].queryset = Location.objects.filter(
            user=user, deleted=False
        )

    class Meta:
        model = Stay
        fields = ("location", "frequency", "start", "end", "inactive_until")
        widgets = {
            "start": forms.DateInput(attrs={"type": "date"}),
            "end": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        stay_start = cleaned_data["start"]
        stay_end = cleaned_data["end"]
        frequency = cleaned_data.get("frequency", None)
        needs_dates = frequency == Stay.ONCE
        if (stay_start and stay_end) and (stay_end < stay_start):
            self.add_error(
                "start", _("The start date must be at or before the end date.")
            )
        if needs_dates and not stay_end:
            self.add_error("end", _("The end date is required."))
        if needs_dates and not stay_start:
            self.add_error("start", _("The start date is required."))


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ("name", "point")


class RouteStepRequestForm(forms.Form):
    YES = "YES"
    NO = "NO"
    ASK_LATER = "ASK_LATER"
    AT_OTHER_DATES = "AT_OTHER_DATES"
    CHOICES = [
        (YES, "Yes"),
        (NO, "No"),
        (ASK_LATER, "Ask later"),
        (AT_OTHER_DATES, "At other dates"),
    ]
    choice = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.RadioSelect,
    )
    new_stay_start = forms.DateField(label=_("From"), required=False)
    new_stay_end = forms.DateField(label=_("Until"), required=False)

    def __init__(self, instance: RouteStep, *args, **kwargs) -> None:
        self.step = instance
        self.prefix = f"request-{instance.id}"
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.step.status != RouteStep.SUGGESTED:
            raise ValidationError(
                _("This request is already %(status)s."),
                params={"status": self.step.get_status_display()},
            )

        if self.step.route.status != Route.CURRENT:
            raise ValidationError(
                _("The travel plans for this step have been cancelled.")
            )

        new_stay_start = cleaned_data["new_stay_start"]
        new_stay_end = cleaned_data["new_stay_end"]
        choice = cleaned_data.get("choice")
        if choice is None:
            return
        needs_dates = choice == self.AT_OTHER_DATES
        if (new_stay_start and new_stay_end) and (new_stay_end < new_stay_start):
            self.add_error(
                "new_stay_start", _("This date must be at or before the end date.")
            )
        if needs_dates and not new_stay_end:
            self.add_error("new_stay_end", _("This date is required."))
        if needs_dates and not new_stay_start:
            self.add_error("new_stay_start", _("This date is required."))

    def save(self):
        match self.cleaned_data["choice"]:
            case self.YES:
                self.step.set_status(RouteStep.ACCEPTED)
            case self.NO:
                self.step.stay.inactive_until = (
                    datetime.date.today() + datetime.timedelta(days=90)
                )
                self.step.set_status(RouteStep.REJECTED)
            case self.ASK_LATER:
                self.step.stay.inactive_until = (
                    datetime.date.today() + datetime.timedelta(days=7)
                )
                self.step.set_status(RouteStep.REJECTED)
            case self.AT_OTHER_DATES:
                new_stay_start = self.cleaned_data["new_stay_start"]
                new_stay_end = self.cleaned_data["new_stay_end"]
                Stay.objects.create(
                    location=self.step.stay.location,
                    user=self.step.stay.user,
                    frequency=Stay.ONCE,
                    start=new_stay_start,
                    end=new_stay_end,
                )
                self.step.stay.inactive_until = new_stay_end
                self.step.set_status(RouteStep.REJECTED)

        self.step.save()
        self.step.stay.save()


class RouteStepCancelForm(forms.Form):
    def __init__(self, instance: RouteStep, *args, **kwargs) -> None:
        self.step = instance
        self.prefix = f"request-cancel-{instance.id}"
        super().__init__(*args, **kwargs)

    def clean(self):
        if self.step.status not in [RouteStep.ACCEPTED, RouteStep.ONGOING]:
            raise ValidationError(_("This handover cannot be changed anymore."))

    def save(self):
        self.step.set_status(RouteStep.CANCELLED)
        self.step.save()


class RouteStepRoutingForm(forms.Form):
    class Choices(models.TextChoices):
        YES = "YES", "Yes"
        REPORT_PROBLEM = "REPORT_PROBLEM", "No"
        # TODO add a way to just cancel the step here as well

    choice = forms.ChoiceField(
        choices=Choices.choices,
        widget=forms.RadioSelect,
    )
    problem_description = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label=_(
            "If there has been a problem, please describe what went wrong and our support team will try to resolve it."
        ),
    )

    def __init__(
        self, instance: RouteStep, request: HttpRequest, *args, **kwargs
    ) -> None:
        self.step = instance
        self.request = request
        self.prefix = f"request-{instance.id}"
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        if self.step.status not in [
            RouteStep.ACCEPTED,
            RouteStep.ONGOING,
        ]:
            raise ValidationError(_("This handover cannot be changed anymore."))

        return super().clean()

    def save(self):
        match self.cleaned_data["choice"]:
            case self.Choices.YES:
                self.step.set_status(RouteStep.ONGOING)
                self.step.previous_step.set_status(RouteStep.COMPLETED)
                self.step.previous_step.save()
                # edge cases:
                # are we the recipient?
                if self.step.stay.user == self.step.packet.recipient:
                    self.step.set_status(RouteStep.COMPLETED)
                # are we responsible for two sequent route steps?
                elif self.step.stay.user == self.step.next_step.stay.user:
                    self.step.set_status(RouteStep.COMPLETED)
                    self.step.next_step.set_status(RouteStep.ONGOING)
                    self.step.next_step.save()
            case self.Choices.REPORT_PROBLEM:
                mail_text = render_to_string(
                    "turtlemail/emails/report_problem.jinja",
                    {
                        "packet_url": self.request.build_absolute_uri(
                            reverse("packet_detail", args=[self.step.packet.human_id])
                        ),
                        "problem_description": self.cleaned_data["problem_description"],
                    },
                )
                send_mail(
                    subject="User reported a problem with a turtlemail devliery",
                    message=mail_text,
                    from_email=None,
                    recipient_list=[settings.SUPPORT_EMAIL],
                )

                self.step.set_status(RouteStep.PROBLEM_REPORTED)
                self.step.save()

        self.step.save()
