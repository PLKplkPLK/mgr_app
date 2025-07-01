from django.urls import path

from . import views

app_name = 'photo'

urlpatterns = [
    path('', views.upload, name='upload'),
    path('photo/<uuid:uuid>/', views.photo_detail, name="photo_detail")
]
