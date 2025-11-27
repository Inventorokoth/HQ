# NLU Integration with Music Player

## Quick Start

### 1. Basic Integration (Plug and Play)

The NLU system is **already integrated** with the voice listener. Just use it:

```python
from src.voice_input import VoiceCommandListener

# Initialize with NLU enabled (default)
listener = VoiceCommandListener(enable_nlu=True, primary_language='sw')

# Listen for play command
parsed = listener.voice_play_command()

if parsed:
    print(f"Intent: {parsed.intent}")
    print(f"Artist: {parsed.entities.get('artist')}")
    print(f"Song: {parsed.entities.get('song')}")
```

### 2. Integration with Main App

Update your main application to use parsed commands:

```python
from src.music_player import MusicPlayer
from src.youtube_client import YouTubeClient
from src.voice_input import VoiceCommandListener

class MusicStreamApp:
    def __init__(self):
        self.player = MusicPlayer()
        self.client = YouTubeClient()
        self.voice_listener = VoiceCommandListener(
            enable_nlu=True,
            primary_language='sw'
        )
    
    def handle_voice_play(self):
        """Handle voice play command with NLU."""
        parsed = self.voice_listener.voice_play_command()
        
        if not parsed:
            print("❌ No command recognized")
            return
        
        # Extract song and artist info
        artist = parsed.entities.get('artist', '')
        song = parsed.entities.get('song', '')
        query = parsed.entities.get('query', '')
        
        # Build search query
        if artist and song:
            search_query = f"{artist} {song}"
        elif artist:
            search_query = artist
        elif song:
            search_query = song
        else:
            search_query = query
        
        print(f"🔍 Searching for: {search_query}")
        
        # Search and play
        results = self.client.search(search_query)
        if results:
            first_result = results[0]
            print(f"▶️  Playing: {first_result['title']}")
            self.player.play_youtube(first_result['url'])
    
    def handle_voice_control(self):
        """Handle generic voice control with NLU."""
        parsed = self.voice_listener.voice_control()
        
        if not parsed or parsed.intent == 'unknown':
            print("❌ Could not understand command")
            return
        
        intent = parsed.intent
        entities = parsed.entities
        
        # Execute command based on intent
        if intent == 'play':
            self.handle_voice_play()
        
        elif intent == 'pause':
            self.player.pause()
            print("⏸️  Paused")
        
        elif intent == 'resume':
            self.player.resume()
            print("▶️  Resumed")
        
        elif intent == 'stop':
            self.player.stop()
            print("⏹️  Stopped")
        
        elif intent == 'volume':
            direction = entities.get('direction', 'up')
            level = entities.get('level')
            
            if level:
                self.player.set_volume(int(level))
                print(f"🔊 Volume: {level}%")
            elif direction == 'up':
                self.player.volume_up()
                print(f"🔊 Volume: {self.player.get_volume()}%")
            elif direction == 'down':
                self.player.volume_down()
                print(f"🔉 Volume: {self.player.get_volume()}%")
        
        elif intent == 'search':
            query = entities.get('query', '')
            print(f"🔍 Searching for: {query}")
            results = self.client.search(query)
            for i, result in enumerate(results[:5], 1):
                print(f"  {i}. {result['title']}")
        
        elif intent == 'status':
            current = self.player.get_current_track()
            if current:
                print(f"Now playing: {current['title']}")
            else:
                print("Nothing is playing")
        
        elif intent == 'help':
            self.show_commands()
        
        elif intent == 'exit':
            self.stop()
    
    def show_commands(self):
        """Show available voice commands."""
        print("\n📋 Available Voice Commands:\n")
        print("🎵 Music Control:")
        print("  Swahili: 'cheza [artist/song]', 'simama', 'endelea', 'hankisha'")
        print("  English: 'play [artist/song]', 'pause', 'resume', 'stop'")
        print("\n🔊 Volume Control:")
        print("  Swahili: 'ongeza kasi', 'pungza sauti', 'sauti 50'")
        print("  English: 'volume up', 'volume down', 'volume 50'")
        print("\n🔍 Search:")
        print("  Swahili: 'tafuta [artist/song]'")
        print("  English: 'search [artist/song]'")
        print("\n📊 Status:")
        print("  Swahili: 'wimbo gani'")
        print("  English: 'what's playing'")
```

### 3. Language Configuration

Set up language support:

```python
from config.settings import settings

# Enable Swahili as primary
settings.PRIMARY_LANGUAGE = 'sw'
settings.SUPPORTED_LANGUAGES = ['sw', 'en', 'es', 'pt']

# Fine-tune NLU confidence
settings.NLU_CONFIDENCE_THRESHOLD = 0.5
settings.ENTITY_CONFIDENCE_THRESHOLD = 0.6

# Enable debug output
settings.DEBUG_NLU = True
settings.DEBUG_ENTITIES = True
```

## Advanced Usage

### Custom Artist Database

Add local artists to the system:

```python
from src.entity_recognizer import EntityRecognizer

recognizer = EntityRecognizer()

# Add Kenyan artist with nicknames
recognizer.add_artist(
    canonical_name="Backbencher",
    aliases=["backbencher", "bb", "back bencher"],
    language="sw",
    genres=["hiphop", "afrobeats"]
)

# Add song
recognizer.add_song(
    song_title="Toxic",
    artists=["Backbencher"],
    aliases=["toxic", "toxik"]
)
```

### Language Switching at Runtime

```python
listener = VoiceCommandListener(enable_nlu=True, primary_language='en')

# User wants to switch to Swahili
listener.enable_language('sw')

# Now listens for Swahili commands
parsed = listener.voice_play_command()
```

### Entity Fuzzy Matching

Handle typos and variations:

```python
from src.entity_recognizer import EntityRecognizer

recognizer = EntityRecognizer()

# Matches "bakbencher" to "Backbencher"
match = recognizer.fuzzy_match(
    query="bakbencher",
    candidates=["Backbencher", "Sia", "Wizkid"],
    threshold=0.7
)
print(match)  # "Backbencher"
```

### Custom Intent Detection

Add new intents:

```python
from src.nlu_engine import NLUEngine

engine = NLUEngine()

# Add custom intent for repeat/replay
engine.add_custom_intent(
    intent='repeat',
    keywords=['rudia', 'tena', 'repeat again'],
    language='sw'
)

parsed = engine.parse("rudia wimbo")
print(parsed.intent)  # 'repeat'
```

## Common Patterns

### Pattern 1: Artist + Song Recognition

```python
# Input: "cheza backbencher ya toxic" (Swahili)
parsed = listener.voice_play_command()

artist = parsed.entities.get('artist')  # "Backbencher"
song = parsed.entities.get('song')      # "Toxic"
search_query = f"{artist} {song}"       # "Backbencher Toxic"

results = youtube_client.search(search_query)
player.play_youtube(results[0]['url'])
```

### Pattern 2: Volume Control with Levels

```python
# Input: "volume 75" or "sauti 75"
parsed = listener.voice_control()

if parsed.intent == 'volume':
    level = parsed.entities.get('level')
    if level:
        player.set_volume(int(level))
```

### Pattern 3: Multi-Language Context

```python
# Detect language automatically or use primary
listener.voice_listener.primary_language = 'sw'

parsed = listener.voice_play_command()
print(f"Language: {parsed.language}")     # "sw"
print(f"Confidence: {parsed.confidence}") # 0.95
```

### Pattern 4: Error Handling

```python
try:
    parsed = listener.voice_play_command()
    
    if not parsed:
        print("No command recognized, retrying...")
        parsed = listener.voice_play_command()
    
    if parsed and parsed.confidence > 0.7:
        # High confidence - execute
        execute_command(parsed)
    elif parsed and parsed.confidence > 0.4:
        # Medium confidence - ask for confirmation
        print(f"Did you mean: {parsed.intent}?")
    else:
        # Low confidence - ask user to repeat
        print("Please repeat that...")
        
except Exception as e:
    print(f"Error: {e}")
```

## Testing

### Test NLU with Examples Script

```bash
cd /home/shrimpman/Music/HQ/music_player
python examples/nlu_examples.py
```

### Interactive Testing

```python
from src.voice_input import VoiceCommandListener

listener = VoiceCommandListener(enable_nlu=True, primary_language='sw')

# Test with Swahili
print("🎤 Say something in Swahili...")
parsed = listener.voice_play_command()
print(f"Intent: {parsed.intent}")
print(f"Entities: {parsed.entities}")
print(f"Language: {parsed.language}")
print(f"Confidence: {parsed.confidence:.1%}")
```

### Unit Testing

```python
import unittest
from src.nlu_engine import NLUEngine

class TestNLU(unittest.TestCase):
    def setUp(self):
        self.engine = NLUEngine()
    
    def test_swahili_play_intent(self):
        parsed = self.engine.parse("cheza")
        self.assertEqual(parsed.intent, 'play')
        self.assertEqual(parsed.language, 'sw')
    
    def test_english_volume_intent(self):
        parsed = self.engine.parse("volume up")
        self.assertEqual(parsed.intent, 'volume')
        self.assertIn('direction', parsed.entities)
    
    def test_confidence_score(self):
        parsed = self.engine.parse("cheza backbencher")
        self.assertGreater(parsed.confidence, 0.7)

if __name__ == '__main__':
    unittest.main()
```

## Troubleshooting

### Issue: NLU Engine Not Initialized

```python
# ❌ Wrong
listener = VoiceCommandListener(enable_nlu=False)

# ✓ Correct
listener = VoiceCommandListener(enable_nlu=True)
```

### Issue: Artist Not Recognized

```python
# Check if artist is in database
from src.entity_recognizer import EntityRecognizer
recognizer = EntityRecognizer()

# Add the artist
recognizer.add_artist("Your Artist", ["nickname"], language="sw")
```

### Issue: Language Not Detected

```python
# Force language
listener = VoiceCommandListener(enable_nlu=True, primary_language='sw')

# Or switch at runtime
listener.enable_language('sw')
```

### Issue: Low Confidence Scores

```python
# Lower threshold for more permissive matching
settings.NLU_CONFIDENCE_THRESHOLD = 0.4  # Was 0.5

# Or enable fuzzy matching
recognizer.fuzzy_match(query, candidates, threshold=0.6)
```

## Performance Optimization

1. **Cache Models**: Language models are cached on first use
2. **Lazy Loading**: Only load languages you use
3. **Entity Database**: Pre-load common artists
4. **Confidence Tuning**: Set appropriate thresholds

```python
# Optimize startup
from src.voice_input import VoiceCommandListener

# Loads English by default
listener = VoiceCommandListener(enable_nlu=True, primary_language='en')

# Lazy load Swahili only when needed
listener.enable_language('sw')  # Loads language model
```

## Next Steps

1. ✅ Test NLU with voice commands
2. ✅ Add your local artists to database
3. ✅ Fine-tune confidence thresholds
4. ✅ Add support for more languages
5. ✅ Create language packs for your region

See `docs/NLU_GUIDE.md` for complete API reference.
