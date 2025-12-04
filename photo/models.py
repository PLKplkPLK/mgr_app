from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

import uuid

def upload_to_uuid(instance, filename):
    extension = filename.split('.')[-1]
    return f'photos/{instance.uuid}.{extension}'

class Photo(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    upload_time = models.DateTimeField(auto_now_add=True, null=True)
    is_private = models.BooleanField(default=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to = upload_to_uuid, null=True)
    prediction = models.TextField()
    prediction_confidence = models.FloatField()
    bbox = models.TextField(null=True)
    review_status = models.PositiveSmallIntegerField(default=0)
    custom_name = models.TextField(null=True)
    localization_latitude = models.FloatField(null=True)
    localization_longitude = models.FloatField(null=True)

    def __str__(self):
        return 'Photo of id: ' + str(self.uuid)

    def get_absolute_url(self):
        return reverse("photo:photo_detail", kwargs={"uuid": self.uuid})

class Review(models.Model):
    upload_time = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    review = models.TextField()
    helpful = models.BooleanField(default=False)
