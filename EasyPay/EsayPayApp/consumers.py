import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Conversation, Chats_Chat, Chats_Transactions


class Chats(AsyncWebsocketConsumer):
    async def connect(self):
        self.self_username = self.scope['url_route']['kwargs']['self_username']
        self.other_one_username = self.scope['url_route']['kwargs']['other_one_username']
        self.room = await self.get_room(self.self_username, self.other_one_username)
        self.channel_group_name = f'chat_room_{self.room.user_first}_{self.room.user_second}'

        await self.channel_layer.group_add(
            self.channel_group_name,
            self.channel_name
        )
        self.groups.append(
            "custom.channelname.UNIQUE")  # important otherwise some cleanup does not happened on disconnect.
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.channel_group_name,
            self.channel_name
        )

    # receive messages from websocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        payment = text_data_json["payment"]
        username = text_data_json["username"]
        receiver = await self.get_user(self.other_one_username)
        if int(payment) != -1:
            amount = int(payment)
            obj = Chats_Transactions.objects.create(transaction_amount=int(payment), transaction_status=True)
            Chats_Chat.objects.create(room=self.room, message=message, transaction=obj,
                                      receiver=receiver)
        else:
            amount = ""
            Chats_Chat.objects.create(room=self.room, message=message, receiver=receiver)
        await self.channel_layer.group_send(
            f'chat_room_{self.room.user_first}_{self.room.user_second}',
            {
                'type': 'message_send',
                'data': {'user': username, 'message': message, 'transaction': amount, 'receiver': receiver.username},
                'room_id': "room_id"
            }
        )

    # Receive message from room group
    async def message_send(self, event):
        await self.send(text_data=json.dumps([event['data']]))

    @database_sync_to_async
    def get_room(self, username1, username2):
        user1 = User.objects.filter(username=username1).first()
        user2 = User.objects.filter(username=username2).first()
        conv = Conversation.get(user1, user2)
        if conv:
            return conv
        return Conversation.objects.create(user_first=user1, user_second=user2)

    @database_sync_to_async
    def get_user(self, username):
        user = User.objects.filter(username=username).first()
        if user:
            return user
        return None
