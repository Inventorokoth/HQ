import time
import threading
from typing import Optional, Callable, Dict
from config.settings import settings

# Try importing the python-vlc binding and ensure the underlying libVLC
# C library is present by attempting to create an Instance. If that fails,
# we'll fall back to a simulated player implementation.
vlc = None
_HAS_VLC = False
try:
    import vlc as _vlc  # type: ignore
    try:
        # Attempt to create a short-lived instance to verify libVLC availability
        _vlc.Instance()
        vlc = _vlc
        _HAS_VLC = True
    except Exception:
        vlc = None
        _HAS_VLC = False
except Exception:
    vlc = None
    _HAS_VLC = False


if _HAS_VLC:
    class MusicPlayer:
        def __init__(self):
            self.instance = vlc.Instance('--no-video', '--aout=pulse')
            self.player = self.instance.media_player_new()
            self.current_media = None
            self.is_playing = False
            self.volume = settings.DEFAULT_VOLUME
            self.position = 0.0
            self.duration = 0.0
            self._last_error = None
            
            # Event callbacks
            self.on_track_change = None
            self.on_playback_end = None
            self.on_position_change = None
            
            # Setup event manager with detailed error tracking
            try:
                self.event_manager = self.player.event_manager()
                self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, 
                                              self._on_playback_end)
                self.event_manager.event_attach(vlc.EventType.MediaPlayerEncounteredError,
                                              self._on_playback_error)
                self.event_manager.event_attach(vlc.EventType.MediaPlayerMediaChanged,
                                              self._on_media_changed)
                self.event_manager.event_attach(vlc.EventType.MediaPlayerOpening,
                                              self._on_opening)
                self.event_manager.event_attach(vlc.EventType.MediaPlayerBuffering,
                                              self._on_buffering)
            except Exception:
                self.event_manager = None
            
            # Start position tracking thread
            self._tracking_thread = threading.Thread(target=self._track_position, daemon=True)
            self._tracking_thread.start()
        
        def _on_playback_end(self, event):
            """Handle playback end event."""
            self.is_playing = False
            if self._last_error:
                print(f"⚠️ Playback ended with error: {self._last_error}")
            if self.on_playback_end:
                self.on_playback_end()
        
        def _on_playback_error(self, event):
            """Handle VLC playback error event."""
            self._last_error = "MediaPlayerEncounteredError"
            print(f"❌ VLC Error: {self._last_error}")
            self.is_playing = False
        
        def _on_media_changed(self, event):
            """Handle media changed event."""
            print(f"📀 Media changed")
        
        def _on_opening(self, event):
            """Handle opening event."""
            print(f"🔄 Opening stream...")
        
        def _on_buffering(self, event):
            """Handle buffering event."""
            if hasattr(event, 'u') and hasattr(event.u, 'new_cache'):
                cache = event.u.new_cache
                print(f"📡 Buffering: {cache}%")
        
        def _track_position(self):
            """Track playback position in a separate thread."""
            while True:
                if self.is_playing and self.player.is_playing():
                    try:
                        self.position = self.player.get_position()
                        self.duration = self.player.get_length() / 1000.0  # Convert to seconds
                        
                        if self.on_position_change:
                            self.on_position_change(self.position, self.duration)
                    except:
                        pass
                time.sleep(0.5)
        
        def play_url(self, url: str, title: str = "Unknown"):
            """Play audio from URL."""
            try:
                media = self.instance.media_new(url)
                self.player.set_media(media)
                self.player.play()
                self.is_playing = True
                self.current_media = title
                
                if self.on_track_change:
                    self.on_track_change(title)
                    
                return True
            except Exception as e:
                print(f"Playback error: {e}")
                return False
        
        def pause(self):
            """Pause playback."""
            if self.player.can_pause():
                self.player.pause()
                self.is_playing = False
        
        def resume(self):
            """Resume playback."""
            if self.player.get_media():
                self.player.play()
                self.is_playing = True
        
        def stop(self):
            """Stop playback."""
            self.player.stop()
            self.is_playing = False
            self.position = 0.0
        
        def set_volume(self, volume: int):
            """Set volume level (0-100)."""
            volume = max(0, min(volume, settings.MAX_VOLUME))
            self.volume = volume
            try:
                self.player.audio_set_volume(volume)
            except Exception:
                pass
        
        def get_volume(self) -> int:
            """Get current volume level."""
            return self.volume
        
        def seek(self, position: float):
            """Seek to position (0.0 to 1.0)."""
            try:
                if self.player.is_seekable():
                    self.player.set_position(max(0.0, min(position, 1.0)))
            except Exception:
                pass
        
        def get_status(self) -> Dict:
            """Get current player status."""
            return {
                'playing': self.is_playing,
                'volume': self.volume,
                'position': self.position,
                'duration': self.duration,
                'current_track': self.current_media
            }
else:
    # Fallback simulated player for environments without libVLC
    class MusicPlayer:
        def __init__(self):
            self.current_media = None
            self.is_playing = False
            self.volume = settings.DEFAULT_VOLUME
            self.position = 0.0
            self.duration = 0.0

            self.on_track_change = None
            self.on_playback_end = None
            self.on_position_change = None

        def _simulate_playback(self, title: str):
            # Non-blocking simulation: set flags only
            self.current_media = title
            self.is_playing = True
            if self.on_track_change:
                self.on_track_change(title)

        def play_url(self, url: str, title: str = "Unknown"):
            try:
                print(f"[SimulatedPlayer] Playing {title} from {url}")
                self._simulate_playback(title)
                return True
            except Exception as e:
                print(f"Simulated playback error: {e}")
                return False

        def pause(self):
            self.is_playing = False

        def resume(self):
            if self.current_media:
                self.is_playing = True

        def stop(self):
            self.is_playing = False
            self.position = 0.0
            if self.on_playback_end:
                self.on_playback_end()

        def set_volume(self, volume: int):
            self.volume = max(0, min(volume, settings.MAX_VOLUME))

        def get_volume(self) -> int:
            return self.volume

        def seek(self, position: float):
            self.position = max(0.0, min(position, 1.0))

        def get_status(self) -> Dict:
            return {
                'playing': self.is_playing,
                'volume': self.volume,
                'position': self.position,
                'duration': self.duration,
                'current_track': self.current_media
            }
    
    def _on_playback_end(self, event):
        """Handle playback end event."""
        self.is_playing = False
        if self.on_playback_end:
            self.on_playback_end()
    
    def _track_position(self):
        """Track playback position in a separate thread."""
        while True:
            if self.is_playing and self.player.is_playing():
                try:
                    self.position = self.player.get_position()
                    self.duration = self.player.get_length() / 1000.0  # Convert to seconds
                    
                    if self.on_position_change:
                        self.on_position_change(self.position, self.duration)
                except:
                    pass
            time.sleep(0.5)
    
    def play_url(self, url: str, title: str = "Unknown"):
        """Play audio from URL."""
        try:
            media = self.instance.media_new(url)
            self.player.set_media(media)
            self.player.play()
            self.is_playing = True
            self.current_media = title
            
            if self.on_track_change:
                self.on_track_change(title)
                
            return True
        except Exception as e:
            print(f"Playback error: {e}")
            return False
    
    def pause(self):
        """Pause playback."""
        if self.player.can_pause():
            self.player.pause()
            self.is_playing = False
    
    def resume(self):
        """Resume playback."""
        if self.player.get_media():
            self.player.play()
            self.is_playing = True
    
    def stop(self):
        """Stop playback."""
        self.player.stop()
        self.is_playing = False
        self.position = 0.0
    
    def set_volume(self, volume: int):
        """Set volume level (0-100)."""
        volume = max(0, min(volume, settings.MAX_VOLUME))
        self.volume = volume
        self.player.audio_set_volume(volume)
    
    def get_volume(self) -> int:
        """Get current volume level."""
        return self.volume
    
    def seek(self, position: float):
        """Seek to position (0.0 to 1.0)."""
        if self.player.is_seekable():
            self.player.set_position(max(0.0, min(position, 1.0)))
    
    def get_status(self) -> Dict:
        """Get current player status."""
        return {
            'playing': self.is_playing,
            'volume': self.volume,
            'position': self.position,
            'duration': self.duration,
            'current_track': self.current_media
        }