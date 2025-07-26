from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.conf import settings

import os

from .forms import StyledAuthenticationForm, StyledUserCreationForm
from .models import Correction

def signup(request):
    """
    Create user or return sign up page
    """
    if request.user.is_authenticated:
        return redirect('/photo')
    
    if request.method == 'POST':
        form = StyledUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/photo')
    else:
        form = StyledUserCreationForm()
    
    return render(request, 'account/sign_up.html', {'form': form})

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
