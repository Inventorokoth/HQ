## Always-On Listening with Wake-Word Detection

This feature enables continuous background listening for a wake word ("HQ") to automatically activate voice commands without needing to say the "voice" command each time.

### Features

- **Always-on listening**: Runs in the background and continuously monitors for the wake word
- **Wake-word detection**: Listens for "HQ" to activate voice command mode
- **Non-blocking**: Runs in a separate thread so it doesn't interfere with music playback
- **Statistics tracking**: Monitor detection accuracy and false positives
- **Configurable**: Change the wake word and confidence threshold as needed

### How to Use

#### Start Always-On Listening
```
listen
```

The app will start listening for the wake word "HQ" in the background. When detected, it automatically activates voice command mode.

#### Stop Always-On Listening
```
nolisten
```

This stops the background listening and returns to manual voice activation.

#### View Wake-Word Statistics
```
wake_stats
```

Shows statistics about wake-word detection:
- Total detections
- False positives
- False negatives
- Average confidence

### How It Works

1. **Background Thread**: Once `listen` is activated, a background thread continuously processes audio
2. **Audio Chunks**: Audio is processed in 1-second chunks to balance responsiveness and CPU usage
3. **Wake Word Detection**: Each chunk is checked against the wake word using Google's Speech Recognition API
4. **Activation**: When the wake word is detected, the app automatically enters voice command mode
5. **Non-blocking**: The background thread doesn't interfere with playback or other operations

### Example Workflow

```
🎵 > listen
🎤 Wake-word detector started (listening for 'HQ')

[Music playing...]
[You speak: "HQ"]

✅ Wake word detected! Activating voice commands...
🎤 Activating voice control...

[Now ready to receive voice commands]
🎤 Listening... (speak your command)
[You speak: "play sia cheap thrills"]
🔍 Searching for: sia cheap thrills
```

### Technical Details

- **Wake Word**: Default is "HQ" (case-insensitive)
- **Confidence Threshold**: Default is 70% for internal confidence scoring
- **Audio Chunk Duration**: 1 second for balance between responsiveness and accuracy
- **Threading**: Uses Python's `threading` module with daemon threads
- **API**: Uses Google's Cloud Speech-to-Text API (via `speech_recognition` library)

### Performance Considerations

- **CPU Usage**: Minimal - processes audio in background with ~0.1s sleep intervals
- **Network Usage**: Makes API calls for each detected speech segment (only when audio is detected)
- **Memory**: Lightweight - only stores wake-word patterns and statistics
- **Latency**: ~1-2 seconds from wake-word detection to voice command activation (API call time)

### Troubleshooting

**Wake word not detected:**
- Make sure microphone is working and ambient noise is low
- Speak clearly and at normal volume
- Try increasing detection threshold tolerance (lower = more sensitive)

**Too many false positives:**
- Try raising the confidence threshold
- Reduce ambient noise
- Speak the wake word more distinctly

**Background process not starting:**
- Check that microphone is accessible
- Ensure enough system resources
- Check for permission errors in error logs

### Advanced Configuration

You can modify the wake-word detector settings in `main.py`:

```python
self.wake_detector = WakeWordDetector(
    wake_word="HQ",              # Change wake word here
    confidence_threshold=0.7,    # Adjust sensitivity (0.0-1.0)
    callback=self._on_wake_word_detected,
    on_error=None
)
```

### Combining with Voice Commands

You can chain commands after saying the wake word:

1. Say: "HQ play sia cheap thrills and set volume 50"
2. System detects "HQ", activates voice mode
3. Processes multi-intent command to play song and adjust volume

Or use the traditional method:
1. Type: `listen` to start background listening
2. Say: "HQ"
3. Then: "play sia"
