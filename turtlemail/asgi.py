"""
ASGI config for turtlemail project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# needs to be here -> startup race condition
django_asgi_app = get_asgi_application()  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.security.websocket import AllowedHostsOriginValidator  # noqa: E402
from channels.auth import AuthMiddlewareStack  # noqa: E402
from django.urls import re_path  # noqa: E402

from . import consumers  # noqa: E402

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "turtlemail.settings")


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    [
                        re_path(
                            r"ws/chat/(?P<step_id>\d+)/$",
                            consumers.ChatConsumer.as_asgi(),
                        ),
                    ]
                )
            )
        ),
    }
)
