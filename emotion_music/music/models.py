from django.db import models
from django.contrib.auth.models import User
from autoslug import AutoSlugField

class Song(models.Model):
    EMOTION_CHOICES = [
        ('Happy', 'Happy'),
        ('Sad', 'Sad'),
        ('Relax', 'Relax'),
        ('Energetic', 'Energetic'),
        ('Heartbroken', 'Heartbroken'),
    ]

    title = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='title', unique=True, always_update=False, null=True, blank=True)
    artist = models.CharField(max_length=200)
    album = models.CharField(max_length=200, blank=True, default='')
    emotion = models.CharField(max_length=50, choices=EMOTION_CHOICES)
    audio_file = models.FileField(upload_to='songs/', blank=True, null=True)
    audio_url = models.URLField(max_length=500, blank=True, null=True)
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    cover_url = models.URLField(max_length=500, blank=True, null=True)
    duration = models.CharField(max_length=10, blank=True, default='')  # e.g. "3:45"
    
    # SEO Fields
    seo_title = models.CharField(max_length=255, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} - {self.artist}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'song')

    def __str__(self):
        return f"Fav: {self.song.title} (session {self.session_key[:8]})"


class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists', null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def song_count(self):
        return self.playlist_songs.count()


class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='playlist_songs')
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('playlist', 'song')

    def __str__(self):
        return f"{self.song.title} in {self.playlist.name}"


class RecentlyPlayed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recently_played', null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='recently_played')
    played_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-played_at']
        unique_together = ('user', 'song')

    def __str__(self):
        return f"Played: {self.song.title}"