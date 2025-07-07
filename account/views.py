from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def signup_page(request):
    """
    Render a site to create user
    """
    if request.user.is_authenticated:
        return redirect('/photo')
    else:
        return render(request, 'account/sign_up.html')

def create(request):
    """
    Create a user
    """
    user = User.objects.create_user(
        request.POST['username'], request.POST['email'], request.POST['password']
    )
    
    return redirect('/photo')

def login_page(request):
    """
    Render a login page
    """
    if request.user.is_authenticated:
        return redirect('/photo')
    
    return render(request, 'account/login.html')

def signin(request):
    """
    Authenticate user
    """
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return redirect('/photo')
    else:
        # to be changed
        return redirect('account:login_page')

@login_required
def settings(request):
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
    return redirect('account:login_page')
