from django.test import TestCase

from .models import Photo

class PhotoModelTests(TestCase):
    def test_if_url_starting_with_https(self):
        """
        attribute url of a photo has to start with https://
        """
        for photo in Photo.objects.all():
            # doesn't work
            self.assertTrue(photo.url[:8] == 'https://')
