from django.urls import path, include

from . import views

urlpatterns = [
    # views.IndexView.as_view()
    # https://docs.djangoproject.com/en/5.2/intro/tutorial04/
    path('', views.browse, name='browse')
]
