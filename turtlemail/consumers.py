import json
from django.utils.html import escape
from django.core import serializers
from django.template.loader import get_template
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from turtlemail.views import ChatsView
from .models import ChatMessage, RouteStep, UserChatMessage


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.step = None
        self.group_name = None

    def connect(self):
        self.step_id = self.scope["url_route"]["kwargs"]["step_id"]
        # the deeply nested data model is very slow to query.
        # For the request intensive messaging functionality we should at least prefetch (sql join).
        self.step = RouteStep.objects.select_related(
            "stay__user", "next_step__stay__user"
        ).get(id=self.step_id)
        self.group_name = f"chat_{str(self.step.pk)}"
        self.user = self.scope["user"]

        # accept connection if the user is involved in this route step
        if (
            self.step.stay.user == self.user
            or self.step.next_step.stay.user == self.user
        ):
            self.accept()

            # join the chat + channel group
            # group of both communicating parties
            async_to_sync(self.channel_layer.group_add)(
                self.group_name, self.channel_name
            )
            # another group for everybody to transmit updates in other chats
            async_to_sync(self.channel_layer.group_add)("all", self.channel_name)

        # # user joined notification
        # html = get_template("partial/join.html").render(context={"user":self.user})
        # self.send(text_data=html)

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )
        # html = get_template("partial/leave.html").render(context={"user":self.user})
        # self.send(
        #     text_data=html
        # )
        # self.room.online.remove(self.user)

    def receive(self, text_data=None, bytes_data=None):
        """
        client pushes message over ws
        """
        if not text_data:
            return
        # prepare data
        text_data_json = json.loads(text_data)
        content = (
            escape(text_data_json["message"])
            .replace("\\r\\n", "<br />")
            .replace("\\n", "<br />")
            .strip()
        )
        if not content:
            return
        # write message to db
        message = UserChatMessage.objects.create(
            author=self.user, route_step=self.step, content=content
        )
        # send message to sender and receiver (if sender has networking issues the message will not appear in the client)
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                "type": "chat_message",
                "message": serializers.serialize(
                    "json", [message, message.chatmessage_ptr]
                ),
                "index": ChatMessage.objects.filter(route_step=self.step).count(),
                "update": False,
            },
        )
        # inform everybody about update in room (we filter authorized recipients in called function)
        async_to_sync(self.channel_layer.group_send)(
            "all",
            {
                "type": "update_chat_list_item",
                "step": serializers.serialize(
                    "json",
                    [
                        self.step,
                    ],
                )[1:-1],
            },
        )

    def chat_message(self, event):
        """
        add or replace chat message to all involved parties
        """
        generator = serializers.deserialize("json", event["message"])
        message = next(generator).object
        message_parent = next(generator).object
        message.chatmessage_ptr = message_parent
        message.created_at = message_parent.created_at
        message.route_step = message_parent.route_step
        message.status = message_parent.status
        html = get_template("turtlemail/_chat_message.jinja").render(
            context={
                "msg": message,
                "new_msg": not event["update"],
                "update_msg": event["update"],
                "user": self.user,
                "index": event["index"],
            }
        )
        if not event["update"] or self.user == message.author:
            self.send(text_data=html)
        # message receipt
        if self.user != message.author and message.status in (
            UserChatMessage.StatusChoices.NEW,
            UserChatMessage.StatusChoices.NOTIFIED,
        ):
            index = ChatMessage.objects.filter(route_step=self.step).count()
            message.status = UserChatMessage.StatusChoices.RECEIVED
            message.save()
            async_to_sync(self.channel_layer.group_send)(
                self.group_name,
                {
                    "type": "chat_message",
                    "message": serializers.serialize(
                        "json", [message, message.chatmessage_ptr]
                    ),
                    "index": index,
                    "update": True,
                },
            )

    def update_chat_list_item(self, event):
        """
        inform clients about updates in chats, that they are not actively reading
        """
        step = next(serializers.deserialize("json", "[" + event["step"] + "]")).object
        # does this broadcast concern us?
        if (
            self.user != step.stay.user and self.user != step.next_step.stay.user
        ) or self.step == step:
            # no? do nothing
            return
        # let's swap the list item (even if swapped already) This is traffic vs db load here.
        chat = ChatsView.get_chat_context(step, self.user, updated=True)
        html = get_template("turtlemail/_chat_list_item.jinja").render(
            context={
                "chat": chat,
                "htmx": True,
            }
        )
        self.send(text_data=html)
