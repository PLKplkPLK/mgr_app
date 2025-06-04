from django.urls import path, include

from . import views

app_name = 'photo'

urlpatterns = [
    path('', views.upload, name='upload')
]
