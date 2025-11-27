# NLU Quick Reference Card

## TL;DR - Get Started in 5 Minutes

### 1. Initialize Voice Listener with NLU
```python
from src.voice_input import VoiceCommandListener

# Initialize with Swahili as primary language
listener = VoiceCommandListener(enable_nlu=True, primary_language='sw')
```

### 2. Listen for Voice Command
```python
# User says: "cheza backbencher ya toxic"
parsed = listener.voice_play_command()

print(parsed.intent)              # "play"
print(parsed.entities['artist'])  # "Backbencher"
print(parsed.entities['song'])    # "Toxic"
print(parsed.language)            # "sw"
```

### 3. Use Parsed Data
```python
# Search YouTube with extracted entities
artist = parsed.entities.get('artist', '')
song = parsed.entities.get('song', '')
query = f"{artist} {song}".strip()

results = youtube_client.search(query)
player.play_youtube(results[0]['url'])
```

---

## Command Cheat Sheet

### Swahili Commands
```
🎵 Music Control:
   cheza [artist/song]    → Play
   simama                 → Pause
   endelea                → Resume
   hankisha               → Stop

🔊 Volume:
   ongeza kasi            → Volume up
   pungza sauti           → Volume down
   sauti 50               → Set volume 50%

🔍 Search:
   tafuta [artist]        → Search

📊 Info:
   wimbo gani             → What's playing
   msaada                 → Help
```

### English Commands
```
🎵 Music Control:
   play [artist/song]     → Play
   pause                  → Pause
   resume                 → Resume
   stop                   → Stop

🔊 Volume:
   volume up              → Volume up
   volume down            → Volume down
   volume 50              → Set volume 50%

🔍 Search:
   search [artist]        → Search

📊 Info:
   what's playing         → Current song
   help                   → Help
```

---

## Key Classes & Methods

### VoiceCommandListener
```python
listener = VoiceCommandListener(
    enable_nlu=True,              # Enable NLU
    primary_language='sw'         # Language: sw, en, es, pt, fr
)

# Listen for play command
parsed = listener.voice_play_command()

# Listen for any command
parsed = listener.voice_control()

# Switch language
listener.enable_language('en')

# Add artist
listener.add_artist_alias('Backbencher', ['backbencher', 'bb'])
```

### NLUEngine
```python
from src.nlu_engine import NLUEngine

engine = NLUEngine()

# Parse text
parsed = engine.parse("cheza backbencher")

# Add custom intent
engine.add_custom_intent(
    intent='repeat',
    keywords=['rudia', 'tena'],
    language='sw'
)

# Resolve alias
canonical = engine.resolve_entity('bb', 'artist')  # → "Backbencher"
```

### EntityRecognizer
```python
from src.entity_recognizer import EntityRecognizer

recognizer = EntityRecognizer()

# Extract entities
entities = recognizer.extract_entities(
    text="cheza backbencher ya toxic",
    detected_language='sw'
)

# Add artist
recognizer.add_artist(
    "Backbencher",
    ["backbencher", "bb"],
    language="sw",
    genres=["hiphop"]
)

# Add song
recognizer.add_song(
    "Toxic",
    ["Backbencher"],
    aliases=["toxic", "toxik"]
)

# Fuzzy match
match = recognizer.fuzzy_match(
    "bakbencher",  # Typo!
    ["Backbencher", "Sia"],
    threshold=0.7
)  # → "Backbencher"
```

### ParsedCommand (Result)
```python
@dataclass
class ParsedCommand:
    intent: str              # 'play', 'pause', 'volume', etc.
    entities: Dict[str, str] # {'artist': 'Backbencher', 'song': 'Toxic'}
    confidence: float        # 0.0-1.0 (0.95 = very confident)
    original_text: str       # "cheza backbencher ya toxic"
    normalized_text: str     # "cheza backbencher ya toxic" (cleaned)
    language: str            # 'sw', 'en', 'es', etc.
```

---

## Configuration

### Enable/Disable NLU
```python
from config.settings import settings

settings.NLU_ENABLED = True               # Enable
settings.NLU_ENABLED = False              # Disable
```

### Language Settings
```python
settings.PRIMARY_LANGUAGE = 'sw'          # Default language
settings.SUPPORTED_LANGUAGES = [          # Available languages
    'sw', 'en', 'es', 'pt', 'fr'
]
```

### Confidence Thresholds
```python
# Lower = more permissive, higher = more strict
settings.NLU_CONFIDENCE_THRESHOLD = 0.5
settings.ENTITY_CONFIDENCE_THRESHOLD = 0.6
```

### Debug Mode
```python
settings.DEBUG_NLU = True              # Print NLU details
settings.DEBUG_ENTITIES = True         # Print entity extraction
```

---

## File Structure

```
music_player/
├── src/
│   ├── nlu_engine.py          ← Intent recognition
│   ├── entity_recognizer.py   ← Artist/song extraction
│   └── voice_input.py         ← Integrated STT + NLU
├── config/
│   ├── settings.py            ← Configuration
│   ├── language_models.py     ← Intent keywords
│   ├── artist_database.json   ← Artist nicknames
│   └── song_database.json     ← Song info
├── docs/
│   ├── NLU_README.md          ← Overview
│   ├── NLU_GUIDE.md           ← Complete guide
│   └── NLU_INTEGRATION.md     ← Integration examples
└── examples/
    └── nlu_examples.py        ← Runnable examples
```

---

## Common Patterns

### Pattern 1: Play Command
```python
parsed = listener.voice_play_command()

if parsed:
    artist = parsed.entities.get('artist', '')
    song = parsed.entities.get('song', '')
    query = parsed.entities.get('query', '')
    
    search_term = f"{artist} {song}".strip() or query
    results = youtube_client.search(search_term)
    player.play_youtube(results[0]['url'])
```

### Pattern 2: Volume Control
```python
parsed = listener.voice_control()

if parsed.intent == 'volume':
    level = parsed.entities.get('level')
    direction = parsed.entities.get('direction')
    
    if level:
        player.set_volume(int(level))
    elif direction == 'up':
        player.volume_up()
    elif direction == 'down':
        player.volume_down()
```

### Pattern 3: Multi-Language Support
```python
# Auto-detect language
parsed = listener.voice_play_command()
detected_lang = parsed.language  # 'sw', 'en', etc.

# Or set explicitly
listener.enable_language('sw')
```

### Pattern 4: Confidence Check
```python
parsed = listener.voice_play_command()

if parsed.confidence > 0.8:
    # High confidence - execute
    execute_command(parsed)
elif parsed.confidence > 0.5:
    # Medium confidence - confirm
    print(f"Did you mean {parsed.intent}?")
else:
    # Low confidence - retry
    print("Please repeat that")
```

---

## Testing

### Run Examples
```bash
python examples/nlu_examples.py
```

### Interactive Test
```python
from src.voice_input import VoiceCommandListener

listener = VoiceCommandListener(enable_nlu=True, primary_language='sw')
parsed = listener.voice_play_command()

print(f"Intent: {parsed.intent}")
print(f"Entities: {parsed.entities}")
print(f"Confidence: {parsed.confidence:.0%}")
```

### Unit Test
```python
from src.nlu_engine import NLUEngine

engine = NLUEngine()
parsed = engine.parse("cheza backbencher")

assert parsed.intent == 'play'
assert parsed.language == 'sw'
assert parsed.confidence > 0.7
```

---

## Supported Languages

| Code | Language | Example |
|------|----------|---------|
| sw | Swahili | cheza, simama, sauti |
| en | English | play, pause, volume |
| es | Spanish | toca, pausa, volumen |
| pt | Portuguese | toca, pausa, som |
| fr | French | joue, pause, volume |

---

## Adding Artist

### Quick Add
```python
listener.add_artist_alias(
    'Artist Name',
    ['nickname1', 'nickname2']
)
```

### Full Add
```python
recognizer.add_artist(
    canonical_name='Artist Name',
    aliases=['nickname1', 'nickname2'],
    language='sw',
    genres=['afrobeats', 'hiphop']
)
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Artist not recognized | Add to database: `recognizer.add_artist(...)` |
| Wrong language | Set explicitly: `listener.enable_language('sw')` |
| Low confidence | Lower threshold: `settings.NLU_CONFIDENCE_THRESHOLD = 0.4` |
| Typo not handled | Use fuzzy match: `recognizer.fuzzy_match(...)` |
| Can't understand | Enable debug: `settings.DEBUG_NLU = True` |

---

## Performance

```
Speech-to-Text:  ~500ms
NLU Parsing:     ~20ms
Entity Extract:  ~10ms
Total:           ~530ms
```

---

## Next Steps

1. ✅ Test with Swahili commands
2. ✅ Add your local artists to database
3. ✅ Switch to other languages
4. ✅ Fine-tune confidence thresholds
5. ✅ Create language packs for more languages

---

**Happy voice commanding! 🎤→🎵**

For detailed info, see:
- NLU_README.md - Overview
- NLU_GUIDE.md - Complete API
- NLU_INTEGRATION.md - Integration examples
