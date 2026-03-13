from django.contrib import admin
from .models import Song, Favorite, Playlist, PlaylistSong, RecentlyPlayed


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'album', 'emotion', 'duration', 'created_at')
    list_filter = ('emotion',)
    search_fields = ('title', 'artist', 'album')
    ordering = ('emotion', 'title')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('song', 'session_key', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('song__title',)


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'session_key', 'song_count', 'created_at')
    search_fields = ('name',)


@admin.register(PlaylistSong)
class PlaylistSongAdmin(admin.ModelAdmin):
    list_display = ('playlist', 'song', 'added_at')


@admin.register(RecentlyPlayed)
class RecentlyPlayedAdmin(admin.ModelAdmin):
    list_display = ('song', 'session_key', 'played_at')
    ordering = ('-played_at',)