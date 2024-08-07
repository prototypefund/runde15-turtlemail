from __future__ import annotations
from typing import TYPE_CHECKING
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings
from django.core import serializers
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from turtlemail.models import RouteStep, SystemChatMessage, User

channel_layer = get_channel_layer()


class NotificationService:
    @classmethod
    def send_system_chat_message(
        cls, step: RouteStep, message_type: SystemChatMessage.SystemMessages
    ):
        from turtlemail.models import ChatMessage, SystemChatMessage

        system_message = SystemChatMessage()
        system_message.route_step = step
        system_message.message_type = message_type
        system_message.content = {
            "date": step.end,
            "location": str(step.stay.location),
        }
        system_message.status = ChatMessage.StatusChoices.RECEIVED
        system_message.save()

    @classmethod
    def notify_messages_read(cls, user: User, step: RouteStep):
        from turtlemail.models import ChatMessage, UserChatMessage

        now_read_messages = UserChatMessage.objects.filter(
            route_step=step,
            status__in=(
                ChatMessage.StatusChoices.NEW,
                ChatMessage.StatusChoices.NOTIFIED,
            ),
        ).exclude(author=user)
        messages_count = ChatMessage.objects.filter(route_step=step).count()
        now_read_messages_count = now_read_messages.count()
        for message in now_read_messages:
            now_read_messages_count -= 1
            message.status = ChatMessage.StatusChoices.RECEIVED
            async_to_sync(channel_layer.group_send)(
                f"chat_{str(step.pk)}",
                {
                    "type": "chat_message",
                    "message": serializers.serialize(
                        "json", [message, message.chatmessage_ptr]
                    ),
                    "index": messages_count - now_read_messages_count,
                    "update": True,
                },
            )
            message.save()

    @classmethod
    def send_email_notification_chat(cls, user: User):
        from turtlemail.views import ChatsView

        chat_list = ChatsView.get_chat_list_context(user)
        communication_url = settings.BASE_URL + reverse("chats")
        mail_text = render_to_string(
            "turtlemail/emails/notification_chat.jinja",
            {
                "user": user,
                "chat_list": chat_list,
                "communication_url": communication_url,
            },
        )
        send_mail(
            subject=_("You've new chat messages in your turtlemail account."),
            message=mail_text,
            from_email=None,
            recipient_list=[user.email],
        )
