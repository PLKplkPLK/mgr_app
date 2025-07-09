from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms

class StyledUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "password1", "password2")

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

class StyledAuthenticationForm(AuthenticationForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "password")

    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nick'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input'}))

class AvatarForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['avatar']
