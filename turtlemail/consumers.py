import json
from django.utils.html import escape
from django.template.loader import get_template
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import RouteStep, UserChatMessage

class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.step = None
        self.group_name = None

    def connect(self):
        self.step_id = self.scope['url_route']['kwargs']['step_id']
        self.group_name = f'chat_{self.room}'
        self.room = RouteStep.objects.get(id=self.step_id)
        self.user = self.scope["user"]

        # accept connection
        self.accept()

        # join the room/group
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
        content = escape(text_data_json["message"]).replace("\\r\\n", "<br />").replace("\\n", "<br />")
        step = RouteStep.objects.get(id=self.step_id)
        message = UserChatMessage.objects.create(author=self.user, route_step=step, content=content)

        html = get_template("_chat_message.jinja").render(context={'msg': message})
        self.send(text_data=html)
