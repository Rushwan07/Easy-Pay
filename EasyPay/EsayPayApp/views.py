import os
import uuid
from io import BytesIO

from PIL import Image
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.mail import send_mail

from .models import Profile, BANK, Security, Conversation

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.db.models import Q


# Create your views here.

def Home(request):
    if request.user.is_authenticated:
        obj = Profile.objects.filter(user=request.user).first()
        # p1 = Conversation.objects.filter(user_first=request.user)
        # # p2 = Conversation.objects.filter(user_second=request.user)
        #
        # result = p1.union(p2)
        if obj:
            pimg = obj.profile
            contex = {'objimg': pimg}
        else:
            contex = {}
        # lis = []
        # for conv in result:
        #     if conv.user_first != request.user:
        #         lis.append(conv.user_first)
        #     else:
        #         lis.append(conv.user_second)
        #
        # contex['conversation'] = lis
        # print(contex)
        return render(request, 'home.html', contex)

    return redirect('Epay:Login')


def profile(request):
    try:

        if request.user.is_authenticated:

            user = request.user.first_name
            account = BANK.objects.filter(b_user_id=request.user.id)
            if account:
                acbank = account.filter(is_active=True).get()
            else:
                acbank = None
            obj = Profile.objects.filter(user=request.user).get()

            pimg = obj.profile
            contex = {'phone': user, 'accounts': acbank, 'objimg': pimg}

            if len(account) == 0:
                messages.success(request, "You didn't Add The Bank Add The Bank First")
                return render(request, "profile.html")

            return render(request, 'profile.html', contex)
        return redirect('Epay:Login')
    except Exception as e:
        print(e)
    messages.error(request, 'Something went wrong')
    return redirect('Epay:Home')


def Create(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        print(password)

        try:
            if User.objects.filter(username=username).first():
                messages.success(request, 'Username is taken.')
                return redirect('Epay:Create')

            if User.objects.filter(email=email).first():
                messages.success(request, 'Email is taken.')
                return redirect('Epay:Create')

            user_obj = User(username=username, email=email)
            user_obj.set_password(password)
            user_obj.first_name = phone
            user_obj.save()
            auth_token = str(uuid.uuid4())
            profile_obj = Profile.objects.create(user=user_obj, auth_token=auth_token)

            profile_obj.save()
            path = "verify"
            send_mail_after_registration(email, auth_token, path)
            return redirect('Epay:Token')

        except Exception as e:
            print(e)

    return render(request, "signin.html")


def Login(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username=username).first()
        if user_obj is None:
            messages.success(request, 'User not found.')
            return redirect('Epay:Login')

        profile_obj = Profile.objects.filter(user=user_obj).first()

        if not profile_obj.is_verified:
            messages.success(request, 'Profile is not verified check your mail.')
            return redirect('Epay:Login')

        user = authenticate(username=username, password=password)
        if user is None:
            messages.success(request, 'Wrong password.')
            return redirect('Epay:Login')

        login(request, user)
        if Security.objects.filter(user=request.user).exists():
            return redirect('Epay:Home')
        else:
            return redirect('Epay:PIN')

    return render(request, 'login.html')


def send_mail_after_registration(email, token, path):
    subject = 'Your accounts need to be verified'
    message = f'Tab the link here : http://127.0.0.1:8000/{path}/{token}'

    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)


def token_send(request):
    return render(request, 'token.html')


def verify(request, auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token=auth_token).first()

        if profile_obj:
            if profile_obj.is_verified:
                messages.success(request, 'Your account is already verified.')
                return redirect('Epay:Success')
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, 'Your account has been verified.')
            return redirect('Epay:Success')
        else:
            return redirect('Epay:Error')
    except Exception as e:
        print(e)
        return redirect('Epay:Create')


def error_page(request):
    return render(request, 'error.html')


def success(request):
    return render(request, 'success.html')


def Logout(request):
    if request.method == 'GET':
        logout(request)
        messages.success(request, 'Logout successfully')
        return redirect('Epay:Login')

    return HttpResponse("Done")


def banks(request, data):
    # print(type(data))
    try:

        banks = BANK.objects.filter(b_name=data).all()

        if banks is None:
            messages.error(request, 'Banks not fount')
            return redirect('Epay:Home')
        user_account = banks.filter(user=request.user).first()
        if not user_account:
            messages.error(request, 'You have not account in that banks contact with bank')
            return redirect('Epay:Home')
        if user_account.b_user_id:
            messages.success(request, f'Your {data} Bank is already added!')
            return redirect("Epay:Home")
        if user_account.b_phone == request.user.first_name and user_account.b_user_email == request.user.email:

            user_account.b_user_id = request.user.id
            prbank = BANK.objects.filter(b_user_id=request.user.id).all()

            if prbank:
                prbank.is_active = False
                prbank.save()
            else:
                user_account.is_active = True
                user_account.save()
        else:
            messages.error(request, "Credential Doen't patch!")
            return redirect("Epay:Profile")
        messages.success(request, f'Your {data} Bank Has Added successfully')
        return redirect("Epay:PIN")

    except Exception as e:
        print(e)
    messages.error(request, 'Something went Wrong!')
    return redirect("Epay:Home")


def balance(request):
    verify = Profile.objects.filter(user=request.user).first()
    if not verify.verify:
        path = "balance"
        return redirect(f'../Pnc/{path}')

    account = BANK.objects.filter(b_user_id=request.user.id)
    if account:

        Acaccount = account.filter(is_active=True).first()
        type = Acaccount.b_type
        name = Acaccount.b_name
        bal = Acaccount.b_balance

        contex = {"type": type, "name": name, "bal": bal}
        verify.verify = False
        verify.save()
        return render(request, 'balnce.html', contex)

    else:
        verify.verify = False
        verify.save()
        messages.success(request, 'You have no accounts')
        return redirect("Epay:Home")


def PIN(request):
    if request.user.is_authenticated:
        user = User.objects.filter(username=request.user.username).first()
        contex = {'name': user.username, 'phone': user.first_name[-4:]}
        print(user.first_name[-4:])
        if Security.objects.filter(user=request.user).exists():
            messages.success(request, 'Your upi already created')
            return redirect('Epay:Profile')
        if request.method == 'POST':

            password = request.POST.get('PIN')

            if 6 < len(password) < 4:
                messages.error(request, "Your PIN should contain atleast 4 and 6 digits")
                return redirect('Epay:PIN')

            Pin = Security(user=request.user, password=password)
            Pin.save()

            messages.success(request, 'Account and PIN created successfully')
            return redirect('Epay:Home')

        return render(request, 'pass.html', contex)
    else:
        return redirect('Epay:Login')


def Pnc(request, data):
    account = BANK.objects.filter(b_user_id=request.user.id)
    Acaccount = account.filter(is_active=True).first()

    contex = {'accounts': Acaccount, "path": data}
    if request.method == 'POST':
        pin = request.POST.get('PIN')

        try:
            obj = Security.objects.filter(user=request.user).first()
            t = obj.password

            if t == int(pin):
                verify = Profile.objects.filter(user=request.user).first()
                verify.verify = True
                verify.save()
                return JsonResponse(
                    {
                        'status': True,
                        'path': data,
                    }
                )


            else:
                return JsonResponse(
                    {
                        'status': False,
                    }
                )
        except Exception as e:
            print(e)

    return render(request, 'Pinchecker.html', contex)


def accounts(request):
    verify = Profile.objects.filter(user=request.user).first()
    if not verify.verify:
        path = "accounts"
        return redirect(f'../Pnc/{path}')

    Accounts = BANK.objects.filter(b_user_id=request.user.id).all()
    contex = {"accounts": Accounts}
    verify.verify = False
    verify.save()
    return render(request, 'accounts.html', contex)


def ImgChange(request):
    try:

        if request.method == 'POST':
            obj = Profile.objects.filter(user=request.user)[0]
            primg = obj.profile
            image = request.FILES['img']
            new_img = imgProcess(image, request.user, primg)

            profileImg = Profile.objects.filter(user=request.user)[0]
            if new_img:
                profileImg.profile = new_img
                profileImg.save()
            return redirect('Epay:Profile')
    except Exception as e:
        print(e)
    return render(request, 'profile.html')


def imgProcess(file, user, before_img):
    try:
        img = Image.open(file)
        image_format = ['JPEG', 'PNG', 'TIFF', 'EPS', 'RAW']
        if img.format in image_format:
            img.thumbnail((480, 480), Image.ANTIALIAS)
            thumbnailString = BytesIO()
            if file.size > 5242880:
                img.save(thumbnailString, 'JPEG', quality=50)
            else:
                img.save(thumbnailString, 'JPEG', quality=100)
            if before_img != 'avatar.png' and before_img != '':
                os.remove(before_img.path)
            newFile = InMemoryUploadedFile(thumbnailString, None, f'{user}.jpg', 'image/jpeg',
                                           thumbnailString,
                                           None)
            return newFile
        else:
            return None
    except:
        return None


def switch(request, data):
    """
        request made for switch the user bank account
    :param request:
        user.is_authenticated
    :return:
        redirect to account page
    """
    accounts = BANK.objects.filter(b_user_id=request.user.id)
    for a in accounts:
        a.is_active = False
        a.save()
    swi = accounts.filter(b_name=data).first()
    swi.is_active = True
    swi.save()
    return redirect('Epay:accounts')


def room(request, slug):
    requested_user = User.objects.filter(username=slug).first()
    requested_user_img = Profile.objects.filter(user=requested_user).first()
    userimage = requested_user_img.profile
    contex = {"user": requested_user, "userimage": userimage}
    return render(request, 'usertrans.html', contex)


def forgotpass(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            user = User.objects.filter(username=username).first()
            if user:
                ptoken = str(uuid.uuid4())
                SP = Profile.objects.filter(user=user).first()
                SP.forget_passtoken = ptoken
                SP.save()
                path = "changepass"
                send_mail_after_registration(user.email, ptoken, path)
                return redirect('Epay:Token')
            else:
                messages.success(request, 'User not fount!')
                return redirect('Epay:forgotpass')

    except Exception as e:
        print(e)
    return render(request, "forgetpass.html")


def changepass(request, auth_token):
    context = {}
    try:
        user = Profile.objects.filter(forget_passtoken=auth_token).first()
        if request.method == 'POST':
            newpass = request.POST['newpass']
            renewpass = request.POST['renewpass']
            id = request.POST['id']
            if id is None:
                messages.error(request, 'Something went wrong')
                return redirect(f"../changepass/{auth_token}")
            if newpass != renewpass:
                messages.error(request, "Password isn't same")
                return redirect(f"../changepass/{auth_token}")

            requester = User.objects.filter(id=id).first()
            requester.set_password(newpass)
            requester.save()
            messages.success(request, 'Login with new password')
            return redirect('Epay:Login')
        context = {"obj_id": user.user.id}
    except Exception as e:
        print(e)
    return render(request, 'changepass.html', context)


def settingspage(request):
    return render(request, 'setting.html')


def personalinfo(request):
    account = Profile.objects.filter(user=request.user).first()

    objimg = account.profile
    contex = {"objimg": objimg, "phone": request.user.first_name, "email": request.user.email}
    return render(request, 'personalinfo.html', contex)

def history(requeest):
    return render(requeest, 'history.html')