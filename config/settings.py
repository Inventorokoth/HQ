import os
from pathlib import Path

class Settings:
    # Audio quality settings
    AUDIO_QUALITY = 'best'
    DEFAULT_FORMAT = 'bestaudio/best'
    
    # Cache settings
    CACHE_DIR = Path.home() / '.cache' / 'music_player'
    DOWNLOAD_DIR = CACHE_DIR / 'downloads'
    
    # Player settings
    DEFAULT_VOLUME = 80
    MAX_VOLUME = 100
    
    # Search settings
    MAX_SEARCH_RESULTS = 10
    
    def __init__(self):
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()