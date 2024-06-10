from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as _UserAdmin

from .forms import UserCreationForm
from .models import Invite, Location, Packet, Route, RouteStep, User, Stay


class UserAdmin(_UserAdmin):
    add_form = UserCreationForm
    model = User
    list_display = (
        "email",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "email",
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (
            None,
            {
                "fields": ("email", "password", "username"),
            },
        ),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "username",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


class RouteStepInline(admin.TabularInline):
    model = RouteStep

    exclude = ["previous_step", "next_step", "packet"]


class PacketAdmin(admin.ModelAdmin):
    list_display = ("human_id", "sender", "recipient")


class RouteAdmin(admin.ModelAdmin):
    list_display = ("id", "packet", "status")
    inlines = [RouteStepInline]


admin.site.register(User, UserAdmin)
admin.site.register(Packet, PacketAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(RouteStep)
admin.site.register(Location)
admin.site.register(Invite)
admin.site.register(Stay)
