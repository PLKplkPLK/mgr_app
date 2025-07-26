from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms


class StyledUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")

    username = forms.CharField(
        label='Nazwa użytkownika',
        widget=forms.TextInput(attrs={'placeholder': 'Nick'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'user@mail.com'})
    )
    password1 = forms.CharField(
        label='Hasło',
        widget=forms.PasswordInput(attrs={'placeholder': 'Hasło'})
    )
    password2 = forms.CharField(
        label='Powtórz hasło',
        widget=forms.PasswordInput(attrs={'placeholder': 'Powtórz hasło'})
    )


class StyledAuthenticationForm(AuthenticationForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "password")

    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Nick'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Hasło'}))

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(_("Aktywuj email"), code="inactive")


class AvatarForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['avatar']
