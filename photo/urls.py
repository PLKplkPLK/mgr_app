from django.urls import path, include

from . import views

app_name = 'photo'

urlpatterns = [
    path('', views.upload, name='upload'),
    path('classify_image/', views.classify_image, name='classify_image')
]
