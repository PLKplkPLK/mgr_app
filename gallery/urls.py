from django.urls import path

from . import views


app_name = 'gallery'

urlpatterns = [
    # views.IndexView.as_view()
    # https://docs.djangoproject.com/en/5.2/intro/tutorial04/
    path('', views.browse, name='browse'),
    path('my', views.browse_my, name='browse_my'),
    path('reviews', views.browse_reviews, name='browse_reviews'),
    path('popular', views.browse_popular, name='browse_popular')
]
