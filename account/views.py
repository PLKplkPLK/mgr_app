from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms

class StyledUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label='Nazwa użytkownika',
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nick'})
    )
    password1 = forms.CharField(
        label='Hasło',
        widget=forms.PasswordInput(attrs={'class': 'input'})
    )
    password2 = forms.CharField(
        label='Powtórz hasło',
        widget=forms.PasswordInput(attrs={'class': 'input'})
    )

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

class StyledAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nick'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input'}))

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
    return redirect('account:signin')
