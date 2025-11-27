````markdown
# music_player

A fully-featured YouTube music player CLI with voice control and intelligent auto-play.

## Features

✨ **Core Features:**
- Search and play music from YouTube
- Local caching of downloaded audio files
- VLC-based audio playback with PulseAudio integration
- Voice command support using Google Speech-to-Text
- **Auto-play timeout**: Automatically plays the first search result after 5 seconds of inactivity

📖 **Commands:**
- `play <song/url>` - Search YouTube and play music
- `pause` / `resume` / `stop` - Playback control
- `volume <0-100>` - Adjust volume
- `seek <0.0-1.0>` - Seek to position
- `search <query>` - Search without playing
- `status` - Show current playback status
- `voice` - Activate voice command input
- `help` - Show help
- `exit` - Exit the app

## Project Structure

```
music_player/
├── src/
│   ├── player.py           # VLC audio playback
│   ├── youtube_client.py   # YouTube search & download
│   ├── voice_input.py      # Speech-to-text support
│   ├── command_parser.py   # CLI command parsing
│   └── utils.py            # Utility functions
├── config/
│   └── settings.py         # Configuration
├── main.py                 # CLI application
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── AUTO_PLAY.md            # Auto-play feature documentation
└── VOICE_CONTROL.md        # Voice control guide
```

## Quick Start

### Setup Virtual Environment

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Run the App

```bash
python main.py
```

### Examples

**Search and auto-select first result (wait 5 seconds):**
```
🎵 > play sia cheap thrills
[search results displayed]
⏱️  Auto-selecting first result in 5 seconds...
🎯 Select track (1-5) or 'c' to cancel: 
⏰ Auto-selecting: #1
🎶 Now playing: Sia - Cheap Thrills
```

**Voice control:**
```
🎵 > voice
🎤 Listening... (speak now)
# Say: "play black mirror"
✓ Recognized: play black mirror
🎶 Now playing: Black Mirror (first result auto-selected)
```

## Features in Detail

### Auto-Play Timeout (NEW!)
When you search for music, the app displays 5 results and waits for your selection. If you don't select anything within 5 seconds, it automatically plays the first (most relevant) result. This makes it perfect for hands-free or lazy operation.

See [AUTO_PLAY.md](AUTO_PLAY.md) for more details.

### Voice Control
Use the `voice` command to speak music requests. Requires a microphone and internet connection for Google Speech-to-Text API.

See [VOICE_CONTROL.md](VOICE_CONTROL.md) for more details.

### Audio Caching
Downloaded audio files are cached locally in `~/.cache/music_player/downloads/` to avoid re-downloading the same songs and to provide faster playback.

### System Requirements

- **OS**: Linux (with PulseAudio or PipeWire)
- **Python**: 3.6+
- **Audio**: PulseAudio/PipeWire audio server
- **Microphone**: Required for voice control feature

## Dependencies

- `yt-dlp` - YouTube video/audio extraction
- `python-vlc` - VLC audio playback
- `SpeechRecognition` - Google Speech-to-Text
- `pyaudio` - Microphone input
- `requests` - HTTP requests

See `requirements.txt` for specific versions.

## Troubleshooting

**No audio output?**
- Ensure PulseAudio is running: `pulseaudio --check`
- Check audio device: `pactl list sinks`
- Verify VLC is properly installed

**Voice commands not working?**
- Test microphone: `python -c "import pyaudio; pyaudio.PyAudio()"`
- Check internet connection (Google Speech-to-Text requires it)
- Increase microphone sensitivity in settings.py (energy_threshold)

**Download errors?**
- YouTube may be blocking requests; try using a VPN
- Check internet connectivity
- Clear cache: `rm -rf ~/.cache/music_player/downloads/`

````
