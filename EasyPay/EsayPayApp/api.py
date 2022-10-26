from rest_framework.authentication import SessionAuthentication
from rest_framework.viewsets import ModelViewSet

from .models import User, Chats_Chat, Conversation, Profile
from .serializers import UserSerilizer, ChatsSerilizer, TransactionHistorySerilizer, TransactionHistory2Serilizer


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class UserSearchModelViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerilizer
    allowed_methods = ('GET', 'POST', 'HEAD', 'OPTIONS')
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def list(self, request, *args, **kwargs):
        query = request.GET['query']
        if len(query) > 78:
            self.queryset = {}
        else:
            user_search_username = User.objects.filter(username__icontains=query).exclude(
                username=request.user.username)
            user_search_phone = User.objects.filter(first_name__icontains=query).exclude(
                first_name=request.user.first_name)
            self.queryset = user_search_username.union(user_search_phone)
        return super(UserSearchModelViewSet, self).list(request, *args, **kwargs)


class ChatsModelViewSet(ModelViewSet):
    queryset = Chats_Chat.objects.all()
    serializer_class = ChatsSerilizer
    allowed_methods = ('GET', 'POST', 'HEAD', 'OPTIONS')
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def list(self, request, *args, **kwargs):
        username1 = request.GET['user1']
        username2 = request.GET['user2']
        user1 = User.objects.filter(username=username1).first()
        user2 = User.objects.filter(username=username2).first()
        if user1 and user2:
            room = Conversation.get(user1, user2)
            if room:
                self.queryset = Chats_Chat.objects.filter(room=room)
            else:
                self.queryset = {}
        else:
            self.queryset = {}
        return super(ChatsModelViewSet, self).list(request, *args, **kwargs)


class TransactionHistoryModelViewSet(ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = TransactionHistorySerilizer
    allowed_methods = ('GET', 'POST', 'HEAD', 'OPTIONS')
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def list(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            conv1 = Conversation.objects.filter(user_first=request.user)
            conv2 = Conversation.objects.filter(user_second=request.user)
            result = conv1.union(conv2)
            self.queryset = []
            users = []
            for res in result:
                if res.user_first != request.user and res.user_first not in users:
                    users.append(res.user_first)
                elif res.user_second != request.user and res.user_second not in users:
                    users.append(res.user_second)
            for user in users:
                self.queryset.append(Profile.objects.filter(user=user).first())
        else:
            self.queryset = {}
        return super(TransactionHistoryModelViewSet, self).list(request, *args, **kwargs)


class TransactionHistory2ModelViewSet(ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = TransactionHistory2Serilizer
    allowed_methods = ('GET', 'POST', 'HEAD', 'OPTIONS')
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def list(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            conv1 = Conversation.objects.filter(user_first=request.user)
            conv2 = Conversation.objects.filter(user_second=request.user)
            result = conv1.union(conv2)
            self.queryset = []
            for conv in result:
                all_chats = Chats_Chat.objects.filter(room=conv)
                for chat in all_chats:
                    if chat.transaction:
                        self.queryset.append(chat)
        else:
            self.queryset = {}
        return super(TransactionHistory2ModelViewSet, self).list(request, *args, **kwargs)
