import datetime

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm as _AuthenticationForm,
)
from django.contrib.auth.forms import (
    BaseUserCreationForm,
    UsernameField,
)
from django.forms import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from turtlemail import widgets

from .models import Invite, Location, Route, RouteStep, Stay, User


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


class StayForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["location"].queryset = Location.objects.filter(user=user)

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
        frequency = cleaned_data["frequency"]
        needs_dates = frequency == Stay.ONCE
        if (stay_start and stay_end) and (stay_end < stay_start):
            self.add_error(
                "start", _("The start date must be at or before the end date.")
            )
        if needs_dates and not stay_end:
            self.add_error("end", _("The end date is required."))
        if needs_dates and not stay_start:
            self.add_error("start", _("The start date is required."))


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
