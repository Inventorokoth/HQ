# Natural Language Understanding (NLU) System

## Overview

The NLU system transforms your music player from a simple speech-to-text interface into an intelligent voice command system that understands local languages, artist nicknames, and contextual phrases.

### What NLU Does

**Before NLU:**
- User says: "cheza backbencher ya toxic"
- System hears: "cheza backbencher ya toxic" (literal text)
- System tries to search for "cheza backbencher ya toxic" on YouTube → fails or gets wrong results

**With NLU:**
- User says: "cheza backbencher ya toxic" (Swahili: "play Backbencher's Toxic")
- System understands:
  - Intent: "play"
  - Artist: "Backbencher" (resolved from nickname "backbencher")
  - Song: "Toxic"
  - Language: Swahili
- System searches for "Backbencher Toxic" → correct result!

## Architecture

### 1. NLU Engine (`src/nlu_engine.py`)

Core intent recognition and command parsing.

**Key Features:**
- Intent extraction (play, pause, volume, search, etc.)
- Multi-language support (5 languages built-in)
- Language auto-detection
- Confidence scoring
- Extensible intent/keyword system

**Key Classes:**
```python
class NLUEngine:
    # Parse raw text into structured command
    def parse(text: str) -> ParsedCommand
    
    # Add custom intents for new languages
    def add_custom_intent(intent, keywords, language)
    
    # Resolve entity aliases
    def resolve_entity(entity_value, entity_type)
```

**Usage:**
```python
from src.nlu_engine import NLUEngine

engine = NLUEngine()
parsed = engine.parse("cheza backbencher ya toxic")

print(parsed.intent)           # "play"
print(parsed.language)         # "sw" (Swahili)
print(parsed.confidence)       # 0.95
```

### 2. Entity Recognizer (`src/entity_recognizer.py`)

Extracts and resolves artist names, songs, and albums with nickname support.

**Key Features:**
- Artist alias/nickname resolution
- Song title extraction
- Album/playlist detection
- Context-aware extraction
- Fuzzy matching for typos
- Language-specific pattern matching

**Key Classes:**
```python
class EntityRecognizer:
    # Extract all entities from text
    def extract_entities(text, language) -> List[Entity]
    
    # Add artist with aliases
    def add_artist(canonical_name, aliases, language)
    
    # Add song to database
    def add_song(song_title, artists, aliases)
    
    # Fuzzy match against candidates
    def fuzzy_match(query, candidates, threshold)
```

**Usage:**
```python
from src.entity_recognizer import EntityRecognizer

recognizer = EntityRecognizer()
entities = recognizer.extract_entities("cheza backbencher ya toxic", "sw")

for entity in entities:
    print(f"{entity.type}: {entity.value} -> {entity.normalized_value}")
    # Output:
    # artist: backbencher -> Backbencher
    # song: toxic -> Toxic
```

### 3. Language Models (`config/language_models.py`)

Predefined intent keywords and context indicators for multiple languages.

**Supported Languages:**
- 🇰🇪 **Swahili (sw)** - East African primary language
- 🇬🇧 **English (en)** - Global language
- 🇪🇸 **Spanish (es)** - Latin America & Spain
- 🇵🇹 **Portuguese (pt)** - Brazil & Portugal
- 🇫🇷 **French (fr)** - West/Central Africa & France

**Language Structure:**
```python
SWAHILI_MODELS = {
    'language_code': 'sw',
    'intents': {
        'play': {
            'keywords': ['cheza', 'ucheze', 'cheze', 'imba'],
            'context_phrases': ['cheza', 'anza wajibu'],
            'examples': ['cheza backbencher ya toxic'],
        },
        'pause': {...},
        'volume': {...},
        # ... other intents
    },
    'context_indicators': {
        'by': ['na', 'ya', 'kutoka'],  # Swahili: "by" artist
        'from_album': ['kutoka', 'kwenye'],
    },
    'entities': {
        'artists': {...},  # Artist aliases/nicknames
        'songs': {...},
    },
    'stop_words': {'na', 'ni', 'kwa', 'ya', 'wa'},
}
```

### 4. Entity Databases (`config/`)

JSON files storing artist and song information.

**artist_database.json:**
- Artist canonical names
- Nicknames and aliases
- Associated languages and genres

**song_database.json:**
- Song titles
- Artist credits
- Song aliases
- Genres and metadata

## Usage Examples

### Example 1: Swahili Command with Nickname

```python
from src.voice_input import VoiceCommandListener

listener = VoiceCommandListener(enable_nlu=True, primary_language='sw')

# User says: "cheza backbencher ya toxic"
parsed = listener.voice_play_command()

print(f"Intent: {parsed.intent}")           # "play"
print(f"Artist: {parsed.entities['artist']}")  # "Backbencher"
print(f"Song: {parsed.entities['song']}")     # "Toxic"
print(f"Language: {parsed.language}")        # "sw"
print(f"Confidence: {parsed.confidence}")    # 0.95
```

**Expected Behavior:**
- NLU recognizes "cheza" as "play" intent (Swahili keyword)
- Entity recognizer finds "backbencher" nickname → resolves to "Backbencher"
- Entity recognizer finds "toxic" song
- System searches YouTube for "Backbencher Toxic" → plays correct result!

### Example 2: English Command with Artist

```python
listener.enable_language('en')

# User says: "play sia cheap thrills"
parsed = listener.voice_play_command()

print(f"Intent: {parsed.intent}")
print(f"Artist: {parsed.entities['artist']}")  # "Sia"
print(f"Song: {parsed.entities['song']}")     # "Cheap Thrills"
```

### Example 3: Volume Control

```python
# User says: "volume up" or "sauti nyingi" (Swahili: louder)
parsed = listener.voice_control()

print(f"Intent: {parsed.intent}")             # "volume"
print(f"Direction: {parsed.entities['direction']}")  # "up"
```

### Example 4: Adding Custom Artist

```python
# Add a new artist with Swahili nickname
listener.add_artist_alias(
    artist_name='Tanzanian Artist Name',
    aliases=['tz artist', 'artist nick', 'artist']
)
```

## Configuration

### Settings (`config/settings.py`)

```python
class Settings:
    # NLU Settings
    NLU_ENABLED = True                          # Enable/disable NLU
    PRIMARY_LANGUAGE = 'sw'                     # Default language
    SUPPORTED_LANGUAGES = ['sw', 'en', 'es', 'pt', 'fr']
    
    # Voice Recognition
    VOICE_TIMEOUT = 10                          # Seconds to listen
    VOICE_ENERGY_THRESHOLD = 4000               # Microphone sensitivity
    
    # NLU Confidence Thresholds
    NLU_CONFIDENCE_THRESHOLD = 0.5              # Min confidence for intent
    ENTITY_CONFIDENCE_THRESHOLD = 0.6           # Min confidence for entity
    
    # Debug Settings
    DEBUG_NLU = True                            # Print NLU details
    DEBUG_ENTITIES = True                       # Print entity extraction
```

## Supported Commands by Language

### Swahili (Primary Language)

| Intent | Keywords | Example |
|--------|----------|---------|
| Play | cheza, ucheze, cheze, imba | `cheza backbencher ya toxic` |
| Pause | simama, sakinisha | `simama` |
| Resume | endelea, anza | `endelea` |
| Stop | hankisha, acha | `hankisha` |
| Volume | kasi, sauti | `ongeza kasi`, `sauti nyingi` |
| Search | tafuta, sagilia | `tafuta cheap thrills` |
| Next | ingia, ijayo | `ingia wimbo` |
| Previous | nyuma, rudi | `nyuma` |
| Status | hali, nini | `wimbo gani inachezwa` |
| Help | msaada, amri | `msaada` |
| Exit | toka, kwaheri | `kwaheri` |

### English

| Intent | Keywords | Example |
|--------|----------|---------|
| Play | play, start, put on | `play sia cheap thrills` |
| Pause | pause, hold on | `pause` |
| Resume | resume, continue | `resume` |
| Stop | stop | `stop` |
| Volume | volume, louder, quieter | `volume up`, `volume 50` |
| Search | search, find | `search diamond` |
| Next | next, skip | `next` |
| Previous | previous, back | `previous` |
| Status | status, what's playing | `what's playing` |
| Help | help, commands | `help` |
| Exit | exit, quit | `exit` |

### Spanish, Portuguese, French

Complete command sets available in `config/language_models.py`

## Adding New Languages

### Step 1: Define Language Model

Add to `config/language_models.py`:

```python
PORTUGUESE_MODELS = {
    'language_code': 'pt',
    'language_name': 'Portuguese',
    'intents': {
        'play': {
            'keywords': ['toca', 'reproduz', 'toco'],
            'context_phrases': ['toca música'],
            'examples': ['toca wizkid'],
        },
        # ... other intents
    },
    'context_indicators': {
        'by': ['de', 'por'],
        'from_album': ['de', 'do'],
    },
    'entities': {
        'artists': {...},
        'songs': {...},
    },
    'stop_words': {'o', 'a', 'os', 'as', 'e', 'ou', 'de'},
}

LANGUAGE_MODELS = {
    'pt': PORTUGUESE_MODELS,
    # ... other languages
}
```

### Step 2: Enable Language in Voice Listener

```python
listener = VoiceCommandListener(enable_nlu=True)
listener.enable_language('pt')  # Portuguese

# Now accepts Portuguese commands
parsed = listener.voice_play_command()
```

### Step 3: Add Artist/Song Database Entries

Update `config/artist_database.json` and `config/song_database.json` with Portuguese nicknames:

```json
{
  "artists": {
    "wizkid": {
      "canonical": "Wizkid",
      "nicknames": ["wizkid", "wiz", "ayo balogun", "wizard"],
      "languages": ["en", "pt", "sw"]
    }
  }
}
```

## Advanced Features

### Fuzzy Matching

Handles typos and spelling variations:

```python
recognizer = EntityRecognizer()
match = recognizer.fuzzy_match(
    query="bakbencher",  # Typo!
    candidates=["Backbencher", "Sia", "Wizkid"],
    threshold=0.7
)
print(match)  # "Backbencher" (matched despite typo)
```

### Context Resolution

Understands context from surrounding words:

```python
# "play toxic by backbencher"
entity = Entity(type='song', value='toxic', ...)
context = recognizer.resolve_entity_context(
    "play toxic by backbencher",
    entity,
    language='en'
)
print(context)  # {'type': 'song', 'artist': 'backbencher'}
```

### Confidence Scoring

Provides confidence scores for all extractions:

```python
parsed = engine.parse("cheza backbencher")
print(parsed.confidence)  # 0.95 (high confidence)

parsed = engine.parse("something unclear")
print(parsed.confidence)  # 0.3 (low confidence)
```

## Troubleshooting

### Issue: NLU not recognizing command

**Solutions:**
1. Check language setting matches spoken language
2. Add artist to database if new
3. Lower confidence threshold in settings
4. Enable debug mode: `settings.DEBUG_NLU = True`

### Issue: Entity not recognized

**Solutions:**
1. Add alias to artist_database.json
2. Use exact spelling (or enable fuzzy matching)
3. Check if artist is in database
4. Enable debug: `settings.DEBUG_ENTITIES = True`

### Issue: Wrong intent detected

**Solutions:**
1. Make sure keyword is in language model
2. Add custom intent if needed
3. Increase confidence threshold
4. Provide more context in command

## Performance Tips

1. **Cache language models** - Load once, reuse:
```python
listener = VoiceCommandListener(enable_nlu=True)
# Models cached automatically
```

2. **Use primary language** - Faster detection for common language:
```python
listener.primary_language = 'sw'  # Swahili
```

3. **Optimize confidence thresholds** - Balance accuracy vs speed:
```python
settings.NLU_CONFIDENCE_THRESHOLD = 0.5  # Lower = faster
```

4. **Preload artist database** - Load common artists on startup:
```python
recognizer.add_artist("Backbencher", ["backbencher", "bb"], "sw")
```

## API Reference

### ParsedCommand

```python
@dataclass
class ParsedCommand:
    intent: str              # Detected intent
    entities: Dict[str, str] # Extracted entities
    confidence: float        # Confidence score (0.0-1.0)
    original_text: str       # Raw input text
    normalized_text: str     # Cleaned text
    language: str            # Detected language
```

### Entity

```python
@dataclass
class Entity:
    type: str               # Entity type (artist, song, album)
    value: str             # Found value
    confidence: float      # Confidence (0.0-1.0)
    normalized_value: str  # Canonical form
    language: str          # Language
    position: Tuple        # Position in text
```

## Next Steps

1. **Test with voice commands** in different languages
2. **Add your local artists** to artist_database.json
3. **Create language packs** for other African languages
4. **Fine-tune confidence thresholds** for your environment
5. **Expand entity database** with more songs/artists

## Support

For issues or questions:
1. Check DEBUG output: `settings.DEBUG_NLU = True`
2. Review language model for your language
3. Verify artist/song databases have entries
4. Test with simple commands first
