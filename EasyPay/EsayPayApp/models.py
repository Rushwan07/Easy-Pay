import uuid

from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User


class Security(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    password = models.IntegerField(blank=True)

    def __str__(self):
        return self.user.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=100)
    forget_passtoken = models.CharField(max_length=100, default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    profile = models.ImageField(upload_to='images/', blank=True, null=True)
    verify = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


# Banks
# username = User.username


class BANK(models.Model):
    b_key = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    b_name = models.CharField(max_length=100)
    b_user_name = models.CharField(max_length=100)
    b_user_email = models.EmailField(max_length=100)
    b_account = models.IntegerField()
    b_ifsc = models.IntegerField()
    b_img = models.CharField(max_length=500, default=False)
    b_type = models.CharField(max_length=100, default=False)
    b_phone = models.CharField(max_length=11)
    b_balance = models.IntegerField(blank=True)
    b_user_id = models.IntegerField(blank=True, default=None, null=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.b_name


class Chats_Transactions(models.Model):
    transaction_amount = models.IntegerField(blank=True, null=True)
    transaction_status = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Conversation(models.Model):
    user_first = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=False, null=False, related_name="user_first")
    user_second = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=False, null=False, related_name="user_second")

    def __str__(self):
        return str(self.user_first.username+"_"+self.user_second.username)

    def clean(self):
        # Ensure that user_one's id is always less than user_two's
        if self.user_first and self.user_second and self.user_first.id > self.user_second.id:
            (self.user_first, self.user_second) = (self.user_second, self.user_first)

    @classmethod
    def get(self, userA, userB):
        """ Gets all conversations between userA and userB
        """
        if userA.id > userB.id:
            (userA, userB) = (userB, userA)

        return self.objects.filter(user_first=userA, user_second=userB).first()

class Chats_Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Conversation, on_delete=models.CASCADE, blank=False, null=False)
    message = models.TextField(blank=True, null=True)
    transaction = models.OneToOneField(Chats_Transactions, on_delete=models.CASCADE, blank=True, null=True)
    date_time = models.DateTimeField(auto_now_add=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kw):
        if self.transaction or self.message:
            return super(Chats_Chat, self).save(*args, **kw)
        raise ValueError("Model should not empty!...")

