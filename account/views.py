from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.http import require_POST
from django.utils.http import urlsafe_base64_decode
from django.conf import settings

import os

from .forms import StyledAuthenticationForm, StyledUserCreationForm
from .models import Correction
from .utils import send_activation_email


def signup(request):
    """
    Create user or return sign up page
    """
    if request.user.is_authenticated:
        return redirect('/photo')
    
    if request.method == 'POST':
        form = StyledUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_activation_email(request, user)
            return render(request, 'account/activation_send.html')
    else:
        form = StyledUserCreationForm()
    
    return render(request, 'account/sign_up.html', {'form': form})


def activate_email(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('/photo')
    else:
        return render(request, 'account/activation_send.html')


def signin(request):
    """
    Authenticate user or return login page
    """
    if request.user.is_authenticated:
        return redirect('/photo')

    if request.method == 'POST':
        form = StyledAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/photo')
        else:
            # email is not activated
            username = request.POST.get('username')
            password = request.POST.get('password')
            User = get_user_model()
            try:
                user = User.objects.get(username=username)
                if user.check_password(password) and not user.is_active:
                    send_activation_email(request, user)
                    return render(request, 'account/activation_send.html')
            except:
                pass
    else:
        form = StyledAuthenticationForm()

    return render(request, 'account/login.html', {'form': form})


@login_required
def settings_page(request):
    """
    Render a settings page
    """
    return render(request, 'account/settings.html')


@login_required
def signout(request):
    """
    Logout user
    """
    logout(request)
    return redirect('account:signin')


@login_required
def select_avatar(request):
    """
    Render avatar selection or change avatar
    """
    avatars_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
    avatar_choices = [f'/media/avatars/{filename}' for filename in os.listdir(avatars_dir)]

    if request.method == 'POST':
        selected_avatar = request.POST.get('avatar')
        if selected_avatar in avatar_choices:
            request.user.avatar = selected_avatar
            request.user.save()
            return redirect('/account/settings')
    
    return render(request, 'account/select_avatar.html', {
        'avatar_choices': avatar_choices,
        'current_avatar': request.user.avatar
    })


@require_POST
@login_required
def send_correction(request):
    """
    Send user's correction proposal
    """
    message = request.POST.get('message')
    
    if len(message) < 401:
        correction = Correction(
            user=request.user,
            message=request.POST.get('message')
        )
        
        if correction.message:
            correction.save()

    return redirect('/account/settings')
