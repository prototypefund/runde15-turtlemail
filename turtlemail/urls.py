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
from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.flatpages import views as flatpages_views

from turtlemail import views

urlpatterns = [
    path("-/admin/", admin.site.urls),
    path(
        "",
        views.IndexView.as_view(),
        name="index",
    ),
    # TODO this route should be named "packets" to stay consistent with
    # the rest of the backend code.
    path("deliveries", views.DeliveriesView.as_view(), name="deliveries"),
    # path("stays", views.StaysView.as_view(), name="stays"),
    path("communication", views.ChatsView.as_view(), name="chats"),
    path("htmx/chat/<int:pk>", views.HtmxChatView.as_view(), name="chat"),
    path(
        "htmx/update-request/<int:pk>",
        views.HtmxUpdateRouteStepRequestView.as_view(),
        name="update_route_step_request",
    ),
    path(
        "htmx/cancel-route-step/<int:pk>",
        views.HtmxRouteStepCancelView.as_view(),
        name="route_step_cancel",
    ),
    path(
        "htmx/update-routing/<int:pk>",
        views.HtmxUpdateRouteStepRoutingView.as_view(),
        name="update_route_step_routing",
    ),
    path("create_packet", views.CreatePacketView.as_view(), name="create_packet"),
    path(
        "deliveries/<slug:slug>",
        views.PacketDetailView.as_view(),
        name="packet_detail",
    ),
    path(
        "htmx/deliveries/<slug:slug>/expand_logs/",
        views.HtmxExpandActivitiesView.as_view(),
        name="expand_packet_logs",
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
    path(
        "htmx/create-location",
        views.HtmxCreateLocationView.as_view(),
        name="htmx-create-location",
    ),
    path(
        "htmx/update-location/<int:pk>",
        views.HtmxUpdateLocationView.as_view(),
        name="htmx-update-location",
    ),
    path(
        "htmx/delete-location/<int:pk>",
        views.HtmxDeleteLocationView.as_view(),
        name="htmx-delete-location",
    ),
    path(
        "htmx/location-detail/<int:pk>",
        views.HtmxLocationDetailView.as_view(),
        name="htmx-location-detail",
    ),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login", views.LoginView.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path(
        "htmx/create-stay/", views.HtmxCreateStayView.as_view(), name="htmx-create-stay"
    ),
    path(
        "htmx/stay-detail/<int:pk>",
        views.HtmxStayDetailView.as_view(),
        name="htmx-stay-detail",
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
    path(
        "pages/legal/", flatpages_views.flatpage, {"url": "/pages/legal/"}, name="legal"
    ),
    path(
        "pages/privacy/",
        flatpages_views.flatpage,
        {"url": "/pages/privacy/"},
        name="privacy",
    ),
    path(
        "pages/experiment/",
        flatpages_views.flatpage,
        {"url": "/pages/experiment/"},
        name="experiment",
    ),
]
