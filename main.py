#!/usr/bin/env python3

import sys
import os
import select

# Add src to path
#!/usr/bin/env python3

import sys
import os
import threading
import time

# Add project root to path so `src` and `config` are importable
PROJECT_ROOT = os.path.dirname(__file__)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.youtube_client import YouTubeClient
from src.player import MusicPlayer
from src.command_parser import CommandParser
from src.voice_input import VoiceCommandListener
from src.utils import print_banner, format_duration, format_progress_bar, clear_screen
from config.settings import settings


class MusicStreamApp:
    def __init__(self):
        self.youtube = YouTubeClient()
        self.player = MusicPlayer()
        self.parser = CommandParser()
        self.voice_listener = VoiceCommandListener()
        self.running = False
        
        # Setup player callbacks
        self.player.on_track_change = self._on_track_change
        self.player.on_playback_end = self._on_playback_end
        self.player.on_position_change = self._on_position_change
        
        self.current_track_info = None
    
    def _on_track_change(self, title: str):
        """Handle track change event."""
        print(f"\n🎶 Now playing: {title}")
    
    def _on_playback_end(self):
        """Handle playback end event."""
        print("\n✅ Playback finished")
        self.current_track_info = None
    
    def _on_position_change(self, position: float, duration: float):
        """Handle position change event (could be used for UI updates)."""
        pass
    
    def display_status(self):
        """Display current player status."""
        status = self.player.get_status()
        
        print("\n" + "="*50)
        print("🎵 Player Status")
        print("="*50)
        print(f"Track:    {status['current_track'] or 'None'}")
        print(f"State:    {'Playing' if status['playing'] else 'Paused'}")
        print(f"Volume:   {status['volume']}%")
        
        if status['duration'] > 0:
            current_time = status['position'] * status['duration']
            progress = format_progress_bar(status['position'])
            time_display = f"{format_duration(current_time)} / {format_duration(status['duration'])}"
            print(f"Progress: {progress}")
            print(f"Time:     {time_display}")
        print("="*50)
    
    def handle_play(self, params: dict):
        """Handle play command with auto-select after 5 seconds."""
        if 'error' in params:
            print(f"❌ {params['error']}")
            return
        
        query = params['query']
        
        # Check if it's a URL
        if self.youtube.is_valid_youtube_url(query):
            video_id = self.youtube.extract_video_id(query)
            if not video_id:
                print("❌ Invalid YouTube URL")
                return
        else:
            # Search for the query
            print(f"🔍 Searching for: {query}")
            results = self.youtube.search_videos(query, max_results=5)
            
            if not results:
                print("❌ No results found")
                return
            
            # Display results
            print("\n📋 Search Results:")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.get('title', 'Unknown')} "
                      f"({format_duration(result.get('duration', 0))})")
            
            # Auto-select logic: wait for user input with 5 second timeout
            timeout_seconds = 5
            
            print(f"\n⏱️  Auto-selecting first result in {timeout_seconds} seconds...")
            print(f"🎯 Select track (1-5) or 'c' to cancel: ", end='', flush=True)
            sys.stdout.flush()
            
            # Use select to wait for input with timeout (Unix-only, non-blocking)
            try:
                ready, _, _ = select.select([sys.stdin], [], [], timeout_seconds)
                
                if ready:
                    # Input is available, read it
                    choice = sys.stdin.readline().strip()
                    if choice.lower() == 'c':
                        print("\n❌ Cancelled")
                        return
                    else:
                        try:
                            sel = int(choice) - 1
                            if 0 <= sel < len(results):
                                video_id = results[sel]['id']
                                self.current_track_info = results[sel]
                            else:
                                print("\n❌ Invalid selection")
                                return
                        except ValueError:
                            print("\n❌ Invalid selection")
                            return
                else:
                    # Timeout occurred - auto-select first result
                    print(f"\n⏰ Auto-selecting: #1")
                    video_id = results[0]['id']
                    self.current_track_info = results[0]
            except (OSError, select.error):
                # select not available (Windows) or other error - fall back to auto-select
                print(f"\n⏰ Auto-selecting: #1")
                video_id = results[0]['id']
                self.current_track_info = results[0]
        
        # Get audio stream URL and play
        print("🔄 Getting audio stream...")
        stream_url = self.youtube.get_audio_stream_url(video_id)
        
        if not stream_url:
            print("❌ Could not get audio stream")
            return
        
        # Get track info for display
        if not self.current_track_info:
            self.current_track_info = self.youtube.get_video_info(video_id)
        
        track_title = self.current_track_info.get('title', 'Unknown') if self.current_track_info else 'Unknown'
        
        if self.player.play_url(stream_url, track_title):
            self.player.set_volume(settings.DEFAULT_VOLUME)
        else:
            print("❌ Failed to start playback")
    
    def handle_volume(self, params: dict):
        """Handle volume command."""
        if 'error' in params:
            print(f"❌ {params['error']}")
            return
        
        volume = params['volume']
        self.player.set_volume(volume)
        print(f"🔊 Volume set to {volume}%")
    
    def handle_seek(self, params: dict):
        """Handle seek command."""
        if 'error' in params:
            print(f"❌ {params['error']}")
            return
        
        position = params['position']
        self.player.seek(position)
        print(f"⏩ Seeked to {position*100:.1f}%")
    
    def handle_search(self, params: dict):
        """Handle search command."""
        if 'error' in params:
            print(f"❌ {params['error']}")
            return
        
        query = params['query']
        print(f"🔍 Searching for: {query}")
        results = self.youtube.search_videos(query)
        
        if not results:
            print("❌ No results found")
            return
        
        print("\n📋 Search Results:")
        for i, result in enumerate(results, 1):
            duration = format_duration(result.get('duration', 0))
            print(f"{i}. {result.get('title', 'Unknown')} - {duration}")
    
    def handle_voice(self):
        """Handle voice input command."""
        print("\n🎤 Activating voice control...")
        voice_result = self.voice_listener.voice_play_command()
        
        if voice_result:
            # Check if we got a ParsedCommand object from NLU
            if hasattr(voice_result, 'intent'):
                # It's a ParsedCommand from NLU
                parsed_cmd = voice_result
                print(f"📝 Intent: {parsed_cmd.intent} | Confidence: {parsed_cmd.confidence:.1%}")
                if parsed_cmd.entities:
                    print(f"   Entities: {parsed_cmd.entities}")
                
                command = parsed_cmd.intent
                
                # Build params dict from ParsedCommand
                params = parsed_cmd.entities.copy() if parsed_cmd.entities else {}
                
                # Add query field if not present (for play/search intents)
                if 'query' not in params and command in ['play', 'search']:
                    # Try to construct query from entities
                    parts = []
                    if 'artist' in params:
                        parts.append(params['artist'])
                    if 'song' in params:
                        parts.append(params['song'])
                    if 'album' in params:
                        parts.append(params['album'])
                    params['query'] = ' '.join(parts) if parts else parsed_cmd.original_text
            else:
                # It's a string from fallback mode - parse it normally
                print(f"📝 Executing: {voice_result}")
                command, params = self.parser.parse(str(voice_result))
            
            # Execute the parsed command
            if command == 'play':
                self.handle_play(params)
            elif command == 'pause':
                self.player.pause()
                print("⏸️ Playback paused")
            elif command == 'resume':
                self.player.resume()
                print("▶️ Playback resumed")
            elif command == 'stop':
                self.player.stop()
                print("⏹️ Playback stopped")
            elif command == 'volume':
                self.handle_volume(params)
            elif command == 'search':
                self.handle_search(params)
            elif command == 'status':
                self.display_status()
            else:
                print(f"❌ Voice command not recognized: {command}")
        else:
            print("❌ Could not process voice input")
    
    def run(self):
        """Main application loop."""
        clear_screen()
        print_banner()
        
        self.running = True
        print("🚀 Music Stream Player is ready! Type 'help' for commands.\n")
        
        while self.running:
            try:
                user_input = input("🎵 > ").strip()
                
                if not user_input:
                    continue
                
                command, params = self.parser.parse(user_input)
                
                if command == 'exit':
                    self.running = False
                    print("👋 Goodbye!")
                
                elif command == 'play':
                    self.handle_play(params)
                
                elif command == 'pause':
                    self.player.pause()
                    print("⏸️ Playback paused")
                
                elif command == 'resume':
                    self.player.resume()
                    print("▶️ Playback resumed")
                
                elif command == 'stop':
                    self.player.stop()
                    print("⏹️ Playback stopped")
                
                elif command == 'volume':
                    self.handle_volume(params)
                
                elif command == 'seek':
                    self.handle_seek(params)
                
                elif command == 'search':
                    self.handle_search(params)
                
                elif command == 'status':
                    self.display_status()
                
                elif command == 'voice':
                    self.handle_voice()
                
                elif command == 'help':
                    print_banner()
                
                elif command == 'unknown':
                    print(f"❌ Unknown command: {params.get('input', '')}")
                    print("💡 Type 'help' for available commands")
                
                elif command == 'error':
                    print(f"❌ Command error: {params.get('error', 'Unknown error')}")
                
            except KeyboardInterrupt:
                print("\n\n🛑 Interrupted by user")
                self.running = False
            except EOFError:
                print("\n\n👋 Goodbye!")
                self.running = False
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
        
        # Cleanup
        self.player.stop()

if __name__ == "__main__":
    app = MusicStreamApp()
    app.run()