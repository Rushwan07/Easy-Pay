from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import api
from .views import *

app_name = 'Epay'


router = DefaultRouter()
router.register(r'query', api.UserSearchModelViewSet, basename='user-search')
router.register(r'conversations', api.ChatsModelViewSet, basename='room-chats')
router.register(r'TransactionHistory', api.TransactionHistoryModelViewSet, basename='Transaction-History')
router.register(r'TransactionHistory2', api.TransactionHistory2ModelViewSet, basename='Transaction-History2')

urlpatterns = [

    path('', Home, name='Home'),
    path('login/', Login, name='Login'),
    path('Create/', Create, name='Create'),
    path('logout/', Logout, name='Logout'),
    path('token/', token_send, name="Token"),
    path('success', success, name='Success'),
    path('verify/<auth_token>', verify, name="verify"),
    path('error/', error_page, name="Error"),
    path('profile/', profile, name="Profile"),
    path('banks/<str:data>', banks, name="banks"),
    path('balance/', balance, name="balance"),
    path('PIN/', PIN, name="PIN"),
    path('Pnc/<str:data>', Pnc, name="Pnc"),
    path('accounts/', accounts, name="accounts"),
    path('ImgChange/', ImgChange, name="ImgChange"),
    path('switch/<str:data>', switch, name="switch"),
    path('api/', include(router.urls)),
    path('room/<str:slug>', room, name="room"),
    path('forgotpass/', forgotpass, name="forgotpass"),
    path('changepass/<auth_token>', changepass, name="changepass"),
    path('settings/', settingspage, name="settings"),
    path('personalinfo/', personalinfo, name="personalinfo"),
    path('history/', history, name="history"),
]
