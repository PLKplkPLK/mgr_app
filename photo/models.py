from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

import uuid

def upload_to_uuid(instance, filename):
    extension = filename.split('.')[-1]
    return f'photos/{instance.uuid}.{extension}'

class Photo(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    upload_time = models.DateTimeField(auto_now_add=True, null=True)
    is_private = models.BooleanField(default=True)
    owner_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True
    )
    image = models.ImageField(upload_to = upload_to_uuid, null=True)
    prediction = models.TextField(null=True)
    prediction_pl = models.TextField(null=True)

    def __str__(self):
        return 'Photo of id: ' + str(self.id)

    def get_absolute_url(self):
        return reverse("photo:photo_detail", kwargs={"uuid": self.uuid})
