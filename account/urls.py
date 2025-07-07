from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

app_name = 'account'

urlpatterns = [
    path('signout/', views.signout, name='signout'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('settings/', views.settings, name='settings')
]
