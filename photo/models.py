from django.db import models
from django.contrib.auth.models import User

class Photo(models.Model):
    uuid = models.TextField()
    upload_time = models.DateTimeField()
    is_private = models.BooleanField()
    owner_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default="None"
    )

    def __str__(self):
        return 'Photo of id: ' + str(self.id)
