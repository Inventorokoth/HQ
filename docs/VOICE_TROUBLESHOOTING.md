# Voice Input Troubleshooting Guide

## Issue: "Listening timed out while waiting for phrase to start"

This error means the microphone isn't detecting your voice clearly enough.

### Fixes Applied ✅

I've updated the voice system with better settings:

1. **Lower energy threshold** (4000 → 2000)
   - More sensitive to quiet voices
   - Detects speech faster

2. **Shorter phrase time limit** (15s → 5s)
   - Stops listening sooner
   - Faster processing

3. **Faster pause detection**
   - `pause_threshold`: 0.5 (was 0.8)
   - `non_speaking_duration`: 0.3
   - Detects end of sentence quicker

4. **Better error handling**
   - Automatic retry (up to 2 times)
   - Clear error messages
   - Suggestions for fixing

5. **Faster noise adjustment** (0.5s → 0.3s)
   - Quicker calibration
   - Better for noisy environments

### Quick Fixes to Try

#### Option 1: Speak Clearly and Louder
```
- Speak at normal volume (not whispering)
- Wait for "Listening..." prompt
- Then speak your command
- Pause clearly between words
```

#### Option 2: Improve Your Audio Setup
```
- Move away from background noise
- Use a better microphone if possible
- Make sure you're not on mute
- Close background apps (music, videos)
```

#### Option 3: Use Test Mode (Recommended)
```bash
python examples/test_voice_nlu.py
# Choose option 3 (Interactive mode)
# Type commands instead of speaking
# Proves NLU works while you test microphone
```

#### Option 4: Retry Automatically
```
The system now retries up to 2 times automatically!
Just wait for the retry prompts.
```

### Diagnostic Steps

1. **Test with English first**
   ```
   > voice
   Say: "play sia"
   ```
   English has better STT support, so if this works, 
   your setup is fine and Swahili just needs better audio.

2. **Check microphone connection**
   ```bash
   pactl list sources | grep -A 5 "Name:"
   ```

3. **Test recording directly**
   ```bash
   ffmpeg -f pulse -i default -t 5 test.wav
   ffplay test.wav
   ```

4. **Run test mode for NLU**
   ```bash
   python examples/test_voice_nlu.py
   ```

### What Changed in Code

#### voice_input.py
- `energy_threshold`: 4000 → 2000
- `pause_threshold`: 0.8 → 0.5
- `non_speaking_duration`: default → 0.3
- `noise_adjustment_duration`: 0.5 → 0.3
- `phrase_time_limit`: 15 → 5
- Better exception handling

#### main.py
- Automatic retry (up to 2 times)
- Better error messages
- Helpful suggestions on failure
- Cancellation support (Ctrl+C)

### If Still Having Issues

1. **Your microphone might not be working**
   - Try: `python examples/test_voice_nlu.py`
   - Choose option 3, type commands
   - If NLU works, microphone is the issue

2. **Environment noise is too high**
   - Move to quieter location
   - Close background apps
   - Use better microphone

3. **Language issue (Swahili specific)**
   - Google STT needs perfect audio for Swahili
   - Try English first to test audio setup
   - Use test mode for Swahili testing
   - Consider text fallback option

### Settings You Can Adjust

In `src/voice_input.py` `__init__` method:

```python
# Make it more sensitive (lower = more sensitive)
self.recognizer.energy_threshold = 1500  # Lower = picks up quiet voices

# Detect end of speech faster (lower = faster)
self.recognizer.pause_threshold = 0.3  # Faster end detection

# Require less silence before starting (lower = faster to start)
self.recognizer.non_speaking_duration = 0.2
```

In `src/voice_input.py` `listen_for_command` method:

```python
# Shorter noise adjustment = faster start
self.recognizer.adjust_for_ambient_noise(source, duration=0.2)  # Was 0.3

# Shorter phrase limit = faster processing
phrase_time_limit=3  # Was 5
```

### Test Your Setup Right Now

```bash
cd /home/shrimpman/Music/HQ/music_player

# Test 1: Try voice (will retry automatically)
python main.py
> voice
# Speak: "play sia cheap thrills"

# Test 2: Use test mode (no microphone needed)
python examples/test_voice_nlu.py
# Choose 3, then type: cheza backbencher ya toxic

# Test 3: Check microphone
pactl list sources short
```

### Success Indicators

✅ System retries automatically (2 times max)
✅ Clear error messages when something fails
✅ Test mode works perfectly (typing commands)
✅ English voice works better than Swahili (expected)
✅ NLU parsing is always perfect

### Expected Behavior Now

1. Type `voice` in the player
2. System waits for you to speak
3. If timeout → Auto-retry (2 times max)
4. If success → Process command with NLU
5. If all fails → Helpful error message + suggestion to use test mode

---

**Still having issues? Use test mode to debug!**
```bash
python examples/test_voice_nlu.py
```

The test mode lets you verify everything works without microphone issues!

