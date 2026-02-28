from django.db import models

class Song(models.Model):
    title = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    emotion = models.CharField(max_length=50)

    def __str__(self):
        return self.title