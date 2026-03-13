import os

templates_dir = r"D:\music project\emotional_music_recommendation-\emotion_music\music\templates\music"

audio_replace = "{% if song.audio_url %}{{ song.audio_url }}{% else %}{{ song.audio_file.url }}{% endif %}"
cover_replace = "{% if song.cover_url %}{{ song.cover_url }}{% elif song.cover_image %}{{ song.cover_image.url }}{% else %}/static/music/img/default_cover.png{% endif %}"

for filename in os.listdir(templates_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(templates_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        modified = False
        if "{{ song.audio_file.url }}" in content:
            content = content.replace("{{ song.audio_file.url }}", audio_replace)
            modified = True
            
        if "{{ song.cover_image.url }}" in content:
            content = content.replace("{{ song.cover_image.url }}", cover_replace)
            modified = True
            
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {filename}")

print("Template updates complete.")
