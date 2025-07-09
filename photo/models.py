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
    prediction_1 = models.TextField(null=True)
    prediction_1_probability = models.FloatField(null=True)
    prediction_2 = models.TextField(null=True)
    prediction_2_probability = models.FloatField(null=True)
    prediction_pl = models.TextField(null=True)
    review_status = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return 'Photo of id: ' + str(self.id)

    def get_absolute_url(self):
        return reverse("photo:photo_detail", kwargs={"uuid": self.uuid})

class Review(models.Model):
    upload_time = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    review = models.TextField()
    helpful = models.BooleanField(default=0)
