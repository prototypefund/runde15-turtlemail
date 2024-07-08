import json
from django.utils.html import escape
from django.template.loader import get_template
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import ChatMessage, RouteStep, UserChatMessage

class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.step = None
        self.group_name = None

    def connect(self):
        self.step_id = self.scope['url_route']['kwargs']['step_id']
        self.step = RouteStep.objects.get(id=self.step_id)
        self.group_name = f'chat_{str(self.step.pk)}'
        self.user = self.scope["user"]

        # accept connection if the user is involved in this route step
        if self.step.stay.user == self.user or self.step.next_step.stay.user == self.user:
            self.accept()

            # join the chat + channel group
            async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)

        # # user joined notification
        # html = get_template("partial/join.html").render(context={"user":self.user})
        # self.send(text_data=html)

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name,self.channel_name)
        # html = get_template("partial/leave.html").render(context={"user":self.user})
        # self.send(
        #     text_data=html
        # )
        # self.room.online.remove(self.user)

    def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        text_data_json = json.loads(text_data)
        content = escape(text_data_json["message"]).replace("\\r\\n", "<br />").replace("\\n", "<br />").strip()
        if not content:
            return
        message = UserChatMessage.objects.create(author=self.user, route_step=self.step, content=content)

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
             "type": "chat_message",
             "message": message,
             "index": ChatMessage.objects.filter(route_step=self.step).count(),
             "update": False
             }
        )

    def chat_message(self, event):
        message = event["message"]
        # message receipt
        if self.user != message.author and message.status == UserChatMessage.StatusChoices.NEW:
            index = ChatMessage.objects.filter(route_step=self.step).count()
            message.status = UserChatMessage.StatusChoices.RECEIVED
            message.save()
            async_to_sync(self.channel_layer.group_send)(
                self.group_name,
                {
                 "type": "chat_message",
                 "message": message,
                 "index": index,
                 "update": True,
                 }
            )
        html = get_template("turtlemail/_chat_message.jinja").render(context={
            'msg': event["message"],
            "new_msg": not event["update"],
            "update_msg": event["update"],
            "user": self.user,
            "index": event["index"],
            })
        self.send(text_data=html)
