import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Song, Favorite, Playlist, PlaylistSong, RecentlyPlayed


def _get_session_key(request):
    """Ensure session exists and return its key."""
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _get_favorite_ids(request):
    """Return set of song IDs favorited by current user or session."""
    if request.user.is_authenticated:
        return set(Favorite.objects.filter(user=request.user).values_list('song_id', flat=True))
    sk = _get_session_key(request)
    return set(Favorite.objects.filter(session_key=sk).values_list('song_id', flat=True))


# ─── Auth Views ─────────────────────────────────────────────────────────────

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            sk = _get_session_key(request)
            user = form.save()
            login(request, user)
            
            # Migrate data
            Favorite.objects.filter(session_key=sk).update(user=user)
            Playlist.objects.filter(session_key=sk).update(user=user)
            RecentlyPlayed.objects.filter(session_key=sk).update(user=user)
            
            messages.success(request, "Registration successful!")
            return redirect('home')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = UserCreationForm()
    return render(request, 'music/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                sk = _get_session_key(request)
                login(request, user)
                
                # Migrate data
                # We use a loop for Favorite to avoid unique constraint errors if user already favorited it
                for fav in Favorite.objects.filter(session_key=sk):
                    if not Favorite.objects.filter(user=user, song=fav.song).exists():
                        fav.user = user
                        fav.save()
                    else:
                        fav.delete()
                
                Playlist.objects.filter(session_key=sk).update(user=user)
                
                for rp in RecentlyPlayed.objects.filter(session_key=sk):
                    if not RecentlyPlayed.objects.filter(user=user, song=rp.song).exists():
                        rp.user = user
                        rp.save()
                    else:
                        rp.delete()
                
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request, 'music/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')


# ─── Pages ────────────────────────────────────────────────────────────────────

def home(request):
    emotions = [
        {'key': 'Happy',       'emoji': '😊', 'color': '#f9c74f'},
        {'key': 'Sad',         'emoji': '😢', 'color': '#4cc9f0'},
        {'key': 'Relax',       'emoji': '😌', 'color': '#80b918'},
        {'key': 'Energetic',   'emoji': '⚡', 'color': '#f77f00'},
        {'key': 'Heartbroken', 'emoji': '💔', 'color': '#e63946'},
    ]
    favorite_ids = _get_favorite_ids(request)
    return render(request, 'music/home.html', {
        'emotions': emotions,
        'favorite_ids': list(favorite_ids),
    })


def recommend(request):
    emotion = request.GET.get('emotion', '')
    songs = Song.objects.filter(emotion__iexact=emotion) if emotion else Song.objects.none()
    favorite_ids = _get_favorite_ids(request)
    if request.user.is_authenticated:
        playlists = Playlist.objects.filter(user=request.user)
    else:
        playlists = Playlist.objects.filter(session_key=_get_session_key(request))
    emotions = [
        {'key': 'Happy',       'emoji': '😊', 'color': '#f9c74f'},
        {'key': 'Sad',         'emoji': '😢', 'color': '#4cc9f0'},
        {'key': 'Relax',       'emoji': '😌', 'color': '#80b918'},
        {'key': 'Energetic',   'emoji': '⚡', 'color': '#f77f00'},
        {'key': 'Heartbroken', 'emoji': '💔', 'color': '#e63946'},
    ]
    return render(request, 'music/recommendations.html', {
        'emotion': emotion,
        'songs': songs,
        'favorite_ids': list(favorite_ids),
        'playlists': playlists,
        'emotions': emotions,
    })


def search(request):
    query = request.GET.get('q', '').strip()
    songs = Song.objects.none()
    if query:
        songs = Song.objects.filter(
            Q(title__icontains=query) | Q(artist__icontains=query) | Q(album__icontains=query)
        )
    favorite_ids = _get_favorite_ids(request)
    playlists = Playlist.objects.filter(session_key=_get_session_key(request))
    return render(request, 'music/search_results.html', {
        'query': query,
        'songs': songs,
        'favorite_ids': list(favorite_ids),
        'playlists': playlists,
    })


def favorites(request):
    if request.user.is_authenticated:
        fav_songs = Song.objects.filter(favorites__user=request.user).order_by('favorites__created_at')
        playlists = Playlist.objects.filter(user=request.user)
    else:
        sk = _get_session_key(request)
        fav_songs = Song.objects.filter(favorites__session_key=sk).order_by('favorites__created_at')
        playlists = Playlist.objects.filter(session_key=sk)
    favorite_ids = _get_favorite_ids(request)
    return render(request, 'music/favorites.html', {
        'songs': fav_songs,
        'favorite_ids': list(favorite_ids),
        'playlists': playlists,
    })


def playlists_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            if request.user.is_authenticated:
                Playlist.objects.create(user=request.user, name=name)
            else:
                sk = _get_session_key(request)
                Playlist.objects.create(session_key=sk, name=name)
        return redirect('playlists')
    
    if request.user.is_authenticated:
        user_playlists = Playlist.objects.filter(user=request.user)
    else:
        sk = _get_session_key(request)
        user_playlists = Playlist.objects.filter(session_key=sk)
    return render(request, 'music/playlists.html', {'playlists': user_playlists})


def playlist_detail(request, pk):
    if request.user.is_authenticated:
        playlist = get_object_or_404(Playlist, pk=pk, user=request.user)
        all_playlists = Playlist.objects.filter(user=request.user)
    else:
        sk = _get_session_key(request)
        playlist = get_object_or_404(Playlist, pk=pk, session_key=sk)
        all_playlists = Playlist.objects.filter(session_key=sk)
    
    playlist_songs = PlaylistSong.objects.filter(playlist=playlist).select_related('song')
    songs = [ps.song for ps in playlist_songs]
    favorite_ids = _get_favorite_ids(request)
    return render(request, 'music/playlist_detail.html', {
        'playlist': playlist,
        'songs': songs,
        'favorite_ids': list(favorite_ids),
        'playlists': all_playlists,
    })


def recently_played_view(request):
    if request.user.is_authenticated:
        recent = RecentlyPlayed.objects.filter(user=request.user).select_related('song')[:30]
        playlists = Playlist.objects.filter(user=request.user)
    else:
        sk = _get_session_key(request)
        recent = RecentlyPlayed.objects.filter(session_key=sk).select_related('song')[:30]
        playlists = Playlist.objects.filter(session_key=sk)
    
    songs = [r.song for r in recent]
    favorite_ids = _get_favorite_ids(request)
    return render(request, 'music/recently_played.html', {
        'songs': songs,
        'favorite_ids': list(favorite_ids),
        'playlists': playlists,
    })


# ─── AJAX Actions ─────────────────────────────────────────────────────────────

@require_POST
def toggle_favorite(request, pk):
    song = get_object_or_404(Song, pk=pk)
    if request.user.is_authenticated:
        fav, created = Favorite.objects.get_or_create(user=request.user, song=song)
    else:
        sk = _get_session_key(request)
        fav, created = Favorite.objects.get_or_create(session_key=sk, song=song)
    
    if not created:
        fav.delete()
        is_fav = False
    else:
        is_fav = True
    return JsonResponse({'is_favorite': is_fav, 'song_id': pk})


@require_POST
def add_to_playlist(request):
    song_id = request.POST.get('song_id')
    playlist_id = request.POST.get('playlist_id')
    try:
        song = Song.objects.get(pk=song_id)
        if request.user.is_authenticated:
            playlist = Playlist.objects.get(pk=playlist_id, user=request.user)
        else:
            sk = _get_session_key(request)
            playlist = Playlist.objects.get(pk=playlist_id, session_key=sk)
            
        PlaylistSong.objects.get_or_create(playlist=playlist, song=song)
        return JsonResponse({'success': True, 'message': f'Added to "{playlist.name}"'})
    except (Song.DoesNotExist, Playlist.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Not found'}, status=404)


@require_POST
def mark_played(request, pk):
    song = get_object_or_404(Song, pk=pk)
    if request.user.is_authenticated:
        RecentlyPlayed.objects.update_or_create(
            user=request.user, song=song,
            defaults={}
        )
    else:
        sk = _get_session_key(request)
        RecentlyPlayed.objects.update_or_create(
            session_key=sk, song=song,
            defaults={}
        )
    return JsonResponse({'success': True})


def download_song(request, pk):
    song = get_object_or_404(Song, pk=pk)
    
    # If the song uses an external URL (like Jamendo), redirect to it for download/streaming
    if song.audio_url:
        from django.shortcuts import redirect
        return redirect(song.audio_url)
        
    if not song.audio_file:
        raise Http404("Audio file not found.")
        
    file_path = song.audio_file.path
    response = FileResponse(open(file_path, 'rb'), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="{song.title}.mp3"'
    return response