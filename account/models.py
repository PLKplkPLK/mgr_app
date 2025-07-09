from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    avatar = models.CharField(max_length=50, null=True, default='/media/avatars/wrobel.png')
    score = models.PositiveIntegerField(default=0)
