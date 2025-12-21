from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    avatar = models.CharField(max_length=50, null=True, default='/media/avatars/wrobel.png')
    score = models.PositiveIntegerField(default=0)
    protector = models.BooleanField(default=False)


class Correction(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    message = models.CharField(max_length=400)
