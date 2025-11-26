# Voice Control Guide

## Quick Start

1. Run the app:
```bash
python main.py
```

2. Type `voice` at the prompt and press Enter:
```
🎵 > voice
```

3. Speak your command clearly (e.g., "play sia cheap thrills")

4. The app will transcribe your speech and execute the command

## What You Can Say

### Music Commands
- **"play [song name]"** — Search and play a song
  - Example: "play bohemian rhapsody"
  - Example: "play michael jackson thriller"

- **"search [query]"** — Search for songs (shows results)
  - Example: "search drake"

- **"pause"** — Pause current playback

- **"resume"** — Resume playback

- **"stop"** — Stop playback

- **"volume [0-100]"** — Set volume level
  - Example: "volume 50"
  - Example: "volume maximum"

- **"status"** — Show current player status

## How It Works

1. When you type `voice`, the app listens to your microphone for up to 10 seconds
2. It captures your speech and sends it to Google's Speech-to-Text API (free, no key needed)
3. The transcribed text is parsed as a command
4. If your command contains "play" but doesn't start with it, the app automatically adds "play" prefix
5. Your music plays

## Tips

- **Speak clearly** — The API works better with clear pronunciation
- **Wait for the prompt** — You'll see "🎤 Listening..." when ready to speak
- **Keep it short** — Single commands work best (avoid long sentences)
- **Network required** — Google Speech-to-Text API requires internet connection
- **No audio?** — Make sure speakers are on, volume is up, and you're not on mute

## Examples

| Say | Result |
|-----|--------|
| "voice" then "play adele" | Searches for Adele, plays first result |
| "voice" then "play rolling stones satisfaction" | Plays the exact song |
| "voice" then "volume 80" | Sets volume to 80% |
| "voice" then "pause" | Pauses current playback |
| "voice" then "status" | Shows player status |

## Troubleshooting

**"Could not understand audio"**
- Speak more slowly and clearly
- Check background noise
- Get closer to microphone

**"Speech API error"**
- Check internet connection
- Google API may be rate-limited; try again in a moment

**"Microphone not available"**
- Check if microphone is connected
- Ensure audio permissions are granted
- Try `pactl list sinks` to verify audio device

## Advanced: Manual Voice Testing

Test the voice module directly:
```bash
python - <<'PY'
from src.voice_input import VoiceCommandListener
listener = VoiceCommandListener()
command = listener.listen_for_command()
print(f"You said: {command}")
PY
```
