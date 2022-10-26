from rest_framework import serializers
from .models import User, Profile, Chats_Chat, Conversation


class UserSerilizer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField('get_profile_url')

    class Meta:
        model = User
        exclude = ['password']

    def get_profile_url(self, user):
        profile = Profile.objects.filter(user=user).first()
        if profile:
            return profile.profile.url

        return None


class ChatsSerilizer(serializers.ModelSerializer):
    date_time = serializers.SerializerMethodField('get_timestamp')
    receiver = serializers.SerializerMethodField('get_receiver')
    transaction = serializers.SerializerMethodField('get_payment')
    payment_status = serializers.SerializerMethodField('get_payment_status')

    class Meta:
        model = Chats_Chat
        exclude = ['id']

    def get_timestamp(self, obj):
        timestamp = obj.date_time
        if timestamp:
            return timestamp.strftime("%d-%m")
        return ''

    def get_receiver(self, obj):
        timestamp = obj.receiver
        if timestamp:
            return timestamp.username
        return ''

    def get_payment(self, obj):
        temp = obj.transaction
        if temp:
            return temp.transaction_amount
        return ''

    def get_payment_status(self, obj):
        temp = obj.transaction
        if temp:
            return temp.transaction_status
        return ''


class TransactionHistorySerilizer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField('get_profile_url')
    user = serializers.SerializerMethodField('get_username')

    class Meta:
        model = Profile
        fields = ['profile', 'user']

    def get_profile_url(self, item):
        if item:
            return item.profile.url
        return None

    def get_username(self, item):
        if item:
            return item.user.username
        return None

class TransactionHistory2Serilizer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('get_username')
    profile = serializers.SerializerMethodField('get_profile_url')
    transaction = serializers.SerializerMethodField('get_transaction_amount')
    date_time = serializers.SerializerMethodField('get_timestamp')

    class Meta:
        model = Chats_Chat
        fields = ['transaction', 'date_time', 'user', 'profile']

    def get_profile_url(self, item):
        if item:
            profile = Profile.objects.filter(user=item.receiver).first()
            return profile.profile.url
        return None

    def get_username(self, item):
        if item:
            return item.receiver.username
        return None

    def get_transaction_amount(self, item):
        if item:
            return item.transaction.transaction_amount
        return None

    def get_timestamp(self, obj):
        timestamp = obj.date_time
        if timestamp:
            return timestamp.strftime("%d-%m-%Y")
        return ''
