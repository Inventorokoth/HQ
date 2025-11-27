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
    
    # Voice & NLU settings
    VOICE_ENABLED = True
    NLU_ENABLED = True  # Natural Language Understanding
    PRIMARY_LANGUAGE = 'sw'  # Swahili as primary language
    SUPPORTED_LANGUAGES = ['sw', 'en', 'es', 'pt', 'fr']  # Swahili, English, Spanish, Portuguese, French
    
    # Voice recognition settings
    VOICE_TIMEOUT = 10  # seconds
    VOICE_PHRASE_LIMIT = 15  # seconds
    VOICE_ENERGY_THRESHOLD = 4000  # Microphone sensitivity
    VOICE_AUTO_RETRY = 2  # Number of retries if recognition fails
    
    # NLU confidence thresholds
    NLU_CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence for intent recognition (0.0-1.0)
    ENTITY_CONFIDENCE_THRESHOLD = 0.6  # Minimum confidence for entity extraction
    
    # Entity database paths
    ARTIST_DATABASE_FILE = Path(__file__).parent / 'artist_database.json'
    SONG_DATABASE_FILE = Path(__file__).parent / 'song_database.json'
    LANGUAGE_MODELS_PATH = Path(__file__).parent / 'language_models.py'
    
    # Debug settings
    DEBUG_NLU = True  # Print NLU parsing details
    DEBUG_ENTITIES = True  # Print entity extraction details
    
    def __init__(self):
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()