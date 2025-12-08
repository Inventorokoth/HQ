import os
import sys
import time
from typing import Optional

def clear_screen():
    """Clear terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')

def format_duration(seconds: float) -> str:
    """Format duration in seconds to MM:SS format."""
    if not seconds or seconds < 0:
        return "00:00"
    
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def format_progress_bar(position: float, length: int = 30) -> str:
    """Create a progress bar string."""
    if position < 0:
        position = 0
    if position > 1:
        position = 1
    
    filled = int(length * position)
    bar = '█' * filled + '░' * (length - filled)
    return f"[{bar}] {position*100:.1f}%"

def print_banner():
    """Print application banner."""
    banner = """
    🎵  Music Stream Player 🎵
    =========================
    Commands:
      play <song/url>    - Play music
      pause              - Pause playback
      resume             - Resume playback
      stop               - Stop playback
      volume <0-100>     - Set volume
      seek <0.0-1.0>     - Seek to position
      search <query>     - Search for music
      status             - Show player status
      voice              - Voice control (speak commands)
      repeat             - Repeat last command
      history            - Show command history
      stats              - Show analytics & corrections
      context            - Show playback context
      listen             - Start always-on listening (wake word: "HQ")
      nolisten           - Stop always-on listening
      wake_stats         - Show wake-word detector stats
      help               - Show this help
      exit               - Exit application
    =========================
    """
    print(banner)