from django.shortcuts import render
from .models import Song

def home(request):
    return render(request, 'music/home.html')

def recommend(request):
    emotion = request.GET.get('emotion')
    songs = Song.objects.filter(emotion__iexact=emotion)
    return render(request, 'music/recommendations.html', {
        'emotion': emotion,
        'songs': songs
    })