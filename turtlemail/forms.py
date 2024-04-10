from django import forms
from django.contrib.auth.forms import (
    BaseUserCreationForm,
    AuthenticationForm as _AuthenticationForm,
    UsernameField,
)
from django.utils.translation import gettext_lazy as _

from turtlemail import widgets

from .models import User


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
        label=_("Who would you like to send your packet to?"),
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
