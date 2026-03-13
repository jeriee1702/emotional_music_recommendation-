import os
import requests
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emotion_music.settings')
django.setup()

from music.models import Song

# Jamendo API endpoint
JAMENDO_URL = "https://api.jamendo.com/v3.0/tracks/"
CLIENT_ID = "b6747d04"  # Default test client id, widely used

# Map Jamendo tags to our Emotions
TAG_EMOTION_MAP = {
    'pop': 'Happy',
    'ambient': 'Relax',
    'jazz': 'Relax',
    'rock': 'Energetic',
    'electronic': 'Energetic',
    'indie': 'Sad',
    'sad': 'Heartbroken',
    'blues': 'Heartbroken'
}

def fetch_and_save_songs():
    print("Clearing old dummy songs...")
    # Optional: Delete existing songs before importing new real ones
    # Song.objects.all().delete()
    
    total_added = 0
    
    for tag, emotion in TAG_EMOTION_MAP.items():
        print(f"Fetching '{tag}' songs for emotion '{emotion}'...")
        params = {
            'client_id': CLIENT_ID,
            'format': 'json',
            'limit': 20, # 20 songs per tag map = ~160 songs
            'tags': tag,
            'include': 'musicinfo',
            'audioformat': 'mp32', 
        }
        
        try:
            response = requests.get(JAMENDO_URL, params=params)
            data = response.json()
            
            if data['headers']['status'] == 'success':
                tracks = data.get('results', [])
                for t in tracks:
                    title = t.get('name', 'Unknown')
                    artist = t.get('artist_name', 'Unknown')
                    audio_url = t.get('audio')
                    cover_url = t.get('image')
                    
                    if not audio_url:
                        continue
                        
                    # Calculate duration from seconds
                    dur_seconds = t.get('duration', 0)
                    mins = dur_seconds // 60
                    secs = dur_seconds % 60
                    duration_str = f"{mins}:{str(secs).zfill(2)}"
                    
                    seo_desc = f"Listen to {title} by {artist}. A perfect {emotion.lower()} track for your mood. Stream online or download for offline listening."
                    
                    # Create the song record
                    # Using get_or_create to avoid duplicates if run multiple times
                    song, created = Song.objects.get_or_create(
                        title=title,
                        artist=artist,
                        defaults={
                            'album': t.get('album_name', ''),
                            'emotion': emotion,
                            'audio_url': audio_url,
                            'cover_url': cover_url,
                            'duration': duration_str,
                            'seo_title': f"{title} - {artist} | {emotion} Music",
                            'seo_description': seo_desc
                        }
                    )
                    
                    if created:
                        total_added += 1
                        
            else:
                print(f"Failed to fetch {tag}: {data['headers'].get('error_message')}")
                
        except Exception as e:
            print(f"Error fetching {tag}: {e}")
            
    print(f"Successfully added {total_added} real songs from Jamendo to the database!")

if __name__ == "__main__":
    fetch_and_save_songs()
