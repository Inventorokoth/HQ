# Voice Recognition Quick Reference

## 30-Second Setup Guide

### Problem: Recognition keeps failing

1. **Open settings**:
   ```bash
   nano /home/shrimpman/Music/HQ/music_player/config/settings.py
   ```

2. **Choose your adjustment**:

   **For quiet/soft speech:**
   ```python
   VOICE_ENERGY_THRESHOLD = 2500  # More sensitive (was 3000)
   ```

   **For noisy environment:**
   ```python
   VOICE_ENERGY_THRESHOLD = 3500  # Less sensitive (was 3000)
   VOICE_AMBIENT_NOISE_DURATION = 2.0  # Longer calibration (was 1.0)
   ```

   **For unreliable internet:**
   ```python
   VOICE_RECOGNITION_RETRIES = 3  # More retries (was 2)
   ```

3. **Save and test**:
   ```bash
   python main.py
   # Type: voice
   # Speak clearly
   ```

## Settings Explained

| Setting | Default | Range | What It Does |
|---------|---------|-------|--------------|
| `VOICE_ENERGY_THRESHOLD` | 3000 | 1000-5000 | Microphone sensitivity (lower = more sensitive) |
| `VOICE_AMBIENT_NOISE_DURATION` | 1.0 | 0.5-2.0 | Calibration time in seconds |
| `VOICE_RECOGNITION_RETRIES` | 2 | 1-5 | Automatic retry attempts |
| `VOICE_TIMEOUT` | 10 | 5-30 | Max listening time in seconds |
| `VOICE_PAUSE_THRESHOLD` | 0.8 | 0.5-1.5 | Pause detection sensitivity |

## Before You Adjust

✅ **Try this first:**
1. Speak **clearly** and **slowly**
2. Speak **louder** (but not shouting)
3. Get **closer to microphone**
4. Reduce **background noise**

These usually fix 80% of recognition issues!

## Preset Configurations

### Quiet Home Office
```python
VOICE_ENERGY_THRESHOLD = 2500
VOICE_AMBIENT_NOISE_DURATION = 1.0
VOICE_RECOGNITION_RETRIES = 2
```

### Noisy Kitchen/Office
```python
VOICE_ENERGY_THRESHOLD = 3500
VOICE_AMBIENT_NOISE_DURATION = 2.0
VOICE_RECOGNITION_RETRIES = 3
```

### Slow Internet
```python
VOICE_RECOGNITION_RETRIES = 3
VOICE_TIMEOUT = 15  # Give API more time
```

### Fast Responses
```python
VOICE_PAUSE_THRESHOLD = 0.5
VOICE_NON_SPEAKING_DURATION = 0.2
VOICE_TIMEOUT = 8
```

## Testing

**Quick microphone test:**
```bash
cd /home/shrimpman/Music/HQ/music_player
source .venv/bin/activate
python -c "
from src.voice_input import VoiceCommandListener
listener = VoiceCommandListener()
print('Say something in 5 seconds...')
result = listener.listen_for_command(timeout=5)
print(f'You said: {result}')
"
```

## Success Indicators

✅ You'll see:
```
🎤 Listening... (speak now)
🎙️  Calibrating microphone...
🔄 Processing speech...
✓ Recognized: 'your command here'
```

❌ Common errors:
```
❌ Could not understand audio
❌ No speech detected
❌ Speech API error
```

## Getting Help

If recognition still fails after adjustments:

1. **Check microphone:**
   ```bash
   arecord -l  # List audio devices
   ```

2. **Test with app:**
   ```bash
   python main.py
   help
   voice  # Try voice command
   ```

3. **Adjust energy threshold step-by-step:**
   - Current: 3000
   - Try: 2750 (quieter), 3250 (louder)
   - Adjust by 250-500 at a time

## Still Having Issues?

See **VOICE_IMPROVEMENTS.md** for detailed troubleshooting guide.
