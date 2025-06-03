from django.db import models

class Photo(models.Model):
    url = models.URLField()
    upload_time = models.DateTimeField()
    is_private = models.BooleanField()
    owner_id = models.ForeignKey() # user_id
    animal = models.TextField(default='Not classified')

    def __str__(self):
        return 'Photo of id: ' + str(self.id)
