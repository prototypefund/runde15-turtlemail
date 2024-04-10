from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm as _AuthenticationForm,
)
from django.contrib.auth.forms import (
    BaseUserCreationForm,
    UsernameField,
)
from django.utils.translation import gettext_lazy as _

from turtlemail import widgets

from .models import Stay, User


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
        self.action = "Sign Up"


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
        self.action = "Log In"


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


class StayForm(forms.ModelForm):
    class Meta:
        model = Stay
        fields = ("location", "frequency", "start", "end")
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
