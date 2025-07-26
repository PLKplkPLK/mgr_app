from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

app_name = 'account'

urlpatterns = [
    path('signout/', views.signout, name='signout'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('settings/', views.settings_page, name='settings'),
    path('change.avatar/', views.select_avatar, name='select_avatar'),
    path('send_correction/', views.send_correction, name='send_correction')
]
