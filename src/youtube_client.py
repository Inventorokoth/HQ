import yt_dlp
import re
import os
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs
from pathlib import Path

class YouTubeClient:
    def __init__(self):
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
        }
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats."""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:shorts\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def is_valid_youtube_url(self, url: str) -> bool:
        """Check if the URL is a valid YouTube URL."""
        youtube_domains = [
            'youtube.com',
            'www.youtube.com',
            'm.youtube.com',
            'youtu.be',
            'www.youtu.be'
        ]
        
        try:
            parsed = urlparse(url)
            return any(domain in parsed.netloc for domain in youtube_domains)
        except:
            return False
    
    def search_videos(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search YouTube for videos."""
        search_opts = {
            **self.ydl_opts,
            'extract_flat': True,
            'default_search': 'ytsearch',
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                info = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
                return info.get('entries', []) if info else []
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_audio_stream_url(self, video_id: str) -> Optional[str]:
        """
        Get audio stream URL or download path.
        
        Strategy:
        - Files < 10MB: Download and cache locally (faster, more reliable)
        - Files ≥ 10MB: Stream directly (saves bandwidth and disk space)
        """
        # Create cache directory
        cache_dir = Path.home() / '.cache' / 'music_player' / 'downloads'
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if already cached
        mp3_path = cache_dir / f"{video_id}.mp3"
        if mp3_path.exists():
            print(f"📀 Using cached: {mp3_path}")
            return str(mp3_path)
        
        # Get file size info first (without downloading)
        print(f"🔍 Checking file size...")
        try:
            info_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio',  # Prefer m4a audio format for better compatibility
                'quiet': True,
                'no_warnings': True,
                'socket_timeout': 30,
                'skip_unavailable_fragments': True,
            }
            
            with yt_dlp.YoutubeDL(info_opts) as ydl:
                info = ydl.extract_info(video_id, download=False)
                
                if not info:
                    print(f"❌ Could not get audio info")
                    return None
                
                # Get file size in bytes
                file_size_bytes = info.get('filesize') or info.get('filesize_approx', 0)
                file_size_mb = file_size_bytes / (1024 * 1024) if file_size_bytes else 0
                
                # Check if we should stream or download
                if file_size_mb >= 10:
                    # Large file: use streaming
                    print(f"📡 File size: {file_size_mb:.1f}MB (≥10MB) → Streaming")
                    
                    # Get the direct stream URL with proper format
                    formats = info.get('formats', [])
                    stream_url = None
                    
                    # Find the best audio format that VLC can handle
                    for fmt in formats:
                        if fmt.get('vcodec') == 'none':  # Audio only
                            if fmt.get('ext') in ['m4a', 'webm', 'ogg', 'aac']:
                                stream_url = fmt.get('url')
                                if stream_url:
                                    break
                    
                    # Fallback to any available URL
                    if not stream_url:
                        stream_url = info.get('url')
                    
                    if stream_url:
                        print(f"✓ Streaming: {info.get('title', 'Unknown')}")
                        return stream_url
                    else:
                        print(f"⚠️ Could not get stream URL, falling back to download...")
                        # Fall through to download logic below
                else:
                    # Small file: download to cache
                    print(f"📥 File size: {file_size_mb:.1f}MB (<10MB) → Downloading to cache")
        
        except Exception as e:
            print(f"⚠️ Could not get file size info: {e}, attempting download...")
        
        # Download and cache the audio
        print(f"📥 Downloading audio to cache...")
        max_retries = 2
        for attempt in range(max_retries):
            try:
                # Download and convert to MP3
                opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': str(cache_dir / '%(id)s'),
                    'quiet': True,
                    'no_warnings': True,
                    'socket_timeout': 30,
                    'force_ipv4': True,
                }
                
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(video_id, download=True)
                    if info:
                        print(f"✓ Downloaded: {info.get('title', 'Unknown')}")
                        # Return the MP3 file path
                        if mp3_path.exists():
                            print(f"📀 Cached to: {mp3_path}")
                            return str(mp3_path)
                        
            except Exception as e:
                print(f"⚠️ Download attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)  # Wait before retry
                continue
        
        print(f"❌ Could not download audio after {max_retries} attempts")
        return None
    
    def get_video_info(self, video_id: str) -> Optional[Dict]:
        """Get video information."""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                return ydl.extract_info(video_id, download=False)
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None