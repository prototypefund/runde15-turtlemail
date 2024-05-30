"""
URL configuration for turtlemail project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, reverse_lazy
from django.contrib.auth.views import LogoutView
from django.views.generic import RedirectView

from turtlemail import views

urlpatterns = [
    path("-/admin/", admin.site.urls),
    path(
        "",
        RedirectView.as_view(url=reverse_lazy("deliveries"), permanent=True),
        name="index",
    ),
    # TODO this route should be named "packets" to stay consistent with
    # the rest of the backend code.
    path("deliveries", views.DeliveriesView.as_view(), name="deliveries"),
    path("stays", views.StaysView.as_view(), name="stays"),
    path(
        "htmx/update-request/<int:pk>",
        views.HtmxUpdateRouteStepRequestView.as_view(),
        name="update_route_step_request",
    ),
    path("create_packet", views.CreatePacketView.as_view(), name="create_packet"),
    path(
        "deliveries/<slug:slug>",
        views.PacketDetailView.as_view(),
        name="packet_detail",
    ),
    path(
        "accept_invite/<str:token>",
        views.AcceptInviteView.as_view(),
        name="accept_invite",
    ),
    path(
        "htmx/invite-user", views.HtmxInviteUserView.as_view(), name="htmx_invite_user"
    ),
    path("profile", views.ProfileView.as_view(), name="profile"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login", views.LoginView.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path(
        "htmx/create-stay/", views.HtmxCreateStayView.as_view(), name="htmx-create-stay"
    ),
    path(
        "htmx/update-stay/<int:pk>",
        views.HtmxUpdateStayView.as_view(),
        name="htmx-update-stay",
    ),
    path(
        "htmx/delete-stay/<int:pk>",
        views.HtmxDeleteStayView.as_view(),
        name="htmx-delete-stay",
    ),
]
