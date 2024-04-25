import datetime
from typing import ClassVar

from django.contrib.gis.db.models import PointField
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """

        if not email:
            raise ValueError(_("The email must be set."))

        user = self.model(email=self.normalize_email(email), **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self._create_user(email, password, **extra_fields)

    def search_for_recipient(self, username: str, searching_users_id: int):
        return self.filter(
            username__icontains=username,
        ).exclude(id__exact=searching_users_id)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name=_("email address"),
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=100, unique=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects: ClassVar[UserManager] = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def __str__(self):
        return self.email


class Location(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    is_home = models.BooleanField(verbose_name=_("Home"))
    # Order: longitude, latitude (!)
    point = PointField(verbose_name=_("Location"), geography=True)
    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")

    def __str__(self):
        return self.name


class Stay(models.Model):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    SOMETIMES = "SOMETIMES"
    ONCE = "ONCE"

    FREQUENCY_CHOICES = [
        (DAILY, "Daily"),
        (WEEKLY, "Weekly"),
        (SOMETIMES, "Sometimes"),
        (ONCE, "Once"),
    ]

    location = models.ForeignKey(
        Location, verbose_name=_("Location"), on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE)
    frequency = models.CharField(
        verbose_name=_("Frequency"), max_length=10, choices=FREQUENCY_CHOICES
    )
    start = models.DateField(
        verbose_name=_("Start"),
        validators=[MinValueValidator(limit_value=datetime.date.today)],
        null=True,
        blank=True,
    )
    end = models.DateField(
        verbose_name=_("End"),
        validators=[MinValueValidator(limit_value=datetime.date.today)],
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Stay")
        verbose_name_plural = _("Stays")


class Packet(models.Model):
    # Users with packets can't be deleted right now.
    # What if the packet is still being delivered?
    sender = models.ForeignKey(
        User,
        verbose_name=_("Sender"),
        on_delete=models.RESTRICT,
        related_name="sent_packets",
    )
    recipient = models.ForeignKey(
        User,
        verbose_name=_("Recipient"),
        on_delete=models.RESTRICT,
        related_name="received_packets",
    )
    created_at = models.DateTimeField(verbose_name=_("Created at"), auto_now_add=True)
    human_id = models.TextField(verbose_name=_("Code"), unique=True)

    class Meta:
        indexes = [
            models.Index(fields=["human_id"]),
            models.Index(fields=["sender_id"]),
            models.Index(fields=["recipient_id"]),
        ]

        verbose_name = _("Delivery")
        verbose_name_plural = _("Deliveries")

    def __str__(self):
        return f'Packet "{self.human_id}"'


class Route(models.Model):
    CURRENT = "CURRENT"
    CANCELLED = "CANCELLED"

    STATUS_CHOICES = [(CURRENT, "Current"), (CANCELLED, "Cancelled")]

    status = models.TextField(verbose_name=_("Status"), choices=STATUS_CHOICES)
    packet = models.ForeignKey(
        Packet,
        verbose_name=_("Delivery"),
        on_delete=models.CASCADE,
        related_name="all_routes",
    )

    class Meta:
        verbose_name = _("Route")
        verbose_name_plural = _("Routes")

    def __str__(self):
        return f"{self.status} Route"


class RouteStep(models.Model):
    SUGGESTED = "SUGGESTED"
    ACCEPTED = "ACCEPTED"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (SUGGESTED, "Suggested"),
        (ACCEPTED, "Accepted"),
        (ONGOING, "Ongoing"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]

    stay = models.ForeignKey(
        Stay,
        verbose_name=_("Stay"),
        related_name="route_steps",
        on_delete=models.RESTRICT,
    )
    start = models.DateField(
        verbose_name=_("Start"),
        validators=[MinValueValidator(limit_value=datetime.date.today)],
        null=True,
        blank=True,
    )
    end = models.DateField(
        verbose_name=_("End"),
        validators=[MinValueValidator(limit_value=datetime.date.today)],
        null=True,
        blank=True,
    )
    previous_step = models.OneToOneField(
        "self",
        verbose_name=_("Previous Step"),
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
    )
    next_step = models.OneToOneField(
        "self",
        verbose_name=_("Next Step"),
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
    )
    packet = models.ForeignKey(
        Packet, verbose_name=_("Delivery"), on_delete=models.CASCADE
    )
    status = models.TextField(verbose_name=_("Status"), choices=STATUS_CHOICES)
    route = models.ForeignKey(
        Route, verbose_name=_("Route"), on_delete=models.CASCADE, related_name="steps"
    )

    class Meta:
        verbose_name = _("Route Step")
        verbose_name_plural = _("Route Steps")


class DeliveryLog(models.Model):
    ROUTE_STEP_CHANGE = "ROUTE_STEP_CHANGE"
    NEW_ROUTE = "NEW_ROUTE"

    ACTION_CHOICES = (
        (ROUTE_STEP_CHANGE, "Route Step Changed"),
        (NEW_ROUTE, "New Route"),
    )

    created_at = models.DateTimeField(verbose_name=_("Datetime"))
    route_step = models.ForeignKey(
        RouteStep,
        verbose_name=_("Route Step"),
        on_delete=models.CASCADE,
        related_name="delivery_logs",
    )
    packet = models.ForeignKey(
        Packet, verbose_name=_("Delivery"), on_delete=models.CASCADE, unique=False
    )
    route = models.ForeignKey(Route, verbose_name=_("Route"), on_delete=models.CASCADE)
    action = models.TextField(choices=ACTION_CHOICES, verbose_name=_("Action Choices"))
    new_step_status = models.TextField(
        choices=RouteStep.STATUS_CHOICES,
        verbose_name=_("New Route Step Status"),
        null=True,
    )

    class Meta:
        verbose_name = _("Delivery Log Entry")
        verbose_name_plural = _("Delivery Log Entries")
