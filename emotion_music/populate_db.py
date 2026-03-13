import os
import random
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emotion_music.settings')
django.setup()

from music.models import Song

EMOTIONS = ['Happy', 'Sad', 'Relax', 'Energetic', 'Heartbroken']

ARTISTS = [
    "The Night Owls", "Electric Dreamers", "Lunar Echo", "Neon Horizon", 
    "Velvet Sounds", "Midnight Rambers", "Solar Flare", "Crystal Waves",
    "Urban Legends", "Silent Whisper", "Echo Chamber", "Future Bass"
]

ADJECTIVES = ["Lost", "Broken", "Bright", "Dark", "Sweet", "Bitter", "Wild", "Calm", "Neon", "Golden", "Fading", "Rising"]
NOUNS = ["Dreams", "Hearts", "Skies", "City", "Lights", "Shadows", "Waves", "Fire", "Ice", "Stars", "Echoes", "Memories"]

def generate_title():
    return f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"

def create_dummy_songs(count=200):
    songs_created = 0
    # First clear existing to start fresh (optional, but good for demo)
    # Song.objects.all().delete()
    
    print(f"Generating {count} dummy songs...")
    for _ in range(count):
        title = generate_title()
        # Add a random number to title occasionally to prevent unique slug collisions on 200 items
        if random.random() > 0.7:
            title += f" Pt. {random.randint(1, 9)}"
            
        artist = random.choice(ARTISTS)
        emotion = random.choice(EMOTIONS)
        album = f"The {title} EP"
        
        # Minutes 2 to 5, seconds 00 to 59
        duration = f"{random.randint(2, 5)}:{str(random.randint(0, 59)).zfill(2)}"
        
        # Placeholder audio file path (doesn't need to actually exist for the DB record)
        # But we'll use a generic name
        dummy_audio = f"songs/dummy_{emotion.lower()}.mp3"
        
        # We can dynamically set the SEO tags
        seo_desc = f"Listen to {title} by {artist}. A perfect {emotion.lower()} track for your mood. Stream online or download for offline listening."
        
        try:
            Song.objects.create(
                title=title,
                artist=artist,
                album=album,
                emotion=emotion,
                duration=duration,
                audio_file=dummy_audio,
                seo_title=f"{title} - {artist} | {emotion} Music",
                seo_description=seo_desc
            )
            songs_created += 1
        except Exception as e:
            print(f"Skipped {title} due to error: {e}")
            
    print(f"Successfully created {songs_created} songs!")

if __name__ == "__main__":
    create_dummy_songs(150)
