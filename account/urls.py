from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

app_name = 'account'

urlpatterns = [
    path('signup/', views.signup_page, name='signup_page'),
    path('signout/', views.signout, name='signout'),
    path('create/', views.create, name='create'),
    path('login/', views.login_page, name='login_page'),
    path('signin/', views.signin, name='signin'),
    path('settings/', views.settings, name='settings')
]
