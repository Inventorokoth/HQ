# music_player

A minimal scaffold for a Python music player CLI.

Structure:

music_player/
├── src/: package code (player, youtube_client, parser, utils)
├── config/: settings
├── requirements.txt
├── main.py: simple CLI demo

How to run:

python3 main.py

Notes:
- Playback is simulated. Replace the Player internals with a real backend for
  actual audio playback.
- add dependencies like yt-dlp to `requirements.txt` when enabling YouTube.

Virtual environment (recommended)

I created a project venv at `.venv` under the project root. To activate it and run the demo:

```bash
# activate
source .venv/bin/activate

# then run
python main.py
```

To (re)install the example dependencies into the venv:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt  # or pip install yt-dlp python-vlc requests
```
