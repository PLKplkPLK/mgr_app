from django.urls import path

from . import views

app_name = 'photo'

urlpatterns = [
    path('', views.upload, name='upload'),
    path('<uuid:uuid>/toggle_privacy/', views.toggle_photo_privacy, name='toggle_photo_privacy'),
    path('<uuid:uuid>/toggle_review/', views.toggle_review, name='toggle_review'),
    path('<uuid:uuid>/post_review/', views.post_review, name='post_review'),
    path('<uuid:uuid>/delete', views.delete_photo, name="delete_photo"),
    path('<uuid:uuid>/rename', views.rename_photo, name="rename_photo"),
    path('<uuid:uuid>/location', views.set_location, name="set_location"),
    path('<int:review_id>/helpful/', views.toggle_helpful, name='toggle_helpful'),
    path('<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('<uuid:uuid>/', views.photo_detail, name="photo_detail")
]
