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
from src.command_learning import CommandCorrectionsLogger, CommandAnalytics
from src.command_history import CommandHistory
from src.entity_recognizer import CommandContext
from src.wake_word_detector import WakeWordDetector
from config.settings import settings
import time


class MusicStreamApp:
    def __init__(self):
        self.youtube = YouTubeClient()
        self.player = MusicPlayer()
        self.parser = CommandParser()
        self.voice_listener = VoiceCommandListener()
        self.running = False
        
        # Initialize new learning and history systems
        self.corrections_logger = CommandCorrectionsLogger()
        self.analytics = CommandAnalytics()
        self.history = CommandHistory()
        self.context = CommandContext()
        
        # Initialize wake-word detector
        self.wake_detector = WakeWordDetector(
            wake_word="HQ",
            callback=self._on_wake_word_detected,
            debug=True  # Enable debug output to see what's being heard
        )
        self.wake_word_active = False
        
        # Setup player callbacks
        self.player.on_track_change = self._on_track_change
        self.player.on_playback_end = self._on_playback_end
        self.player.on_position_change = self._on_position_change
        
        self.current_track_info = None
    
    def _on_track_change(self, title: str):
        """Handle track change event."""
        print(f"\n🎶 Now playing: {title}")
        # Track artist in context
        if title:
            self.context.add_song(title)
    
    def _on_wake_word_detected(self):
        """Handle wake-word detection."""
        print("\n" + "🎤 " * 15)
        print("🎤 WAKE WORD DETECTED - ACTIVATING VOICE COMMANDS 🎤")
        print("🎤 " * 15 + "\n")
        self.wake_word_active = True
        # Automatically trigger voice command handling
        self.handle_voice()
        self.wake_word_active = False
    
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
        """Handle play command with auto-select after 5 seconds and command tracking."""
        start_time = time.time()
        success = False
        
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
                self.analytics.record_command('play', False, time.time() - start_time)
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
                        self.analytics.record_command('play', False, time.time() - start_time)
                        return
                    else:
                        try:
                            sel = int(choice) - 1
                            if 0 <= sel < len(results):
                                video_id = results[sel]['id']
                                self.current_track_info = results[sel]
                            else:
                                print("\n❌ Invalid selection")
                                self.analytics.record_command('play', False, time.time() - start_time)
                                return
                        except ValueError:
                            print("\n❌ Invalid selection")
                            self.analytics.record_command('play', False, time.time() - start_time)
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
            self.analytics.record_command('play', False, time.time() - start_time)
            return
        
        # Get track info for display
        if not self.current_track_info:
            self.current_track_info = self.youtube.get_video_info(video_id)
        
        track_title = self.current_track_info.get('title', 'Unknown') if self.current_track_info else 'Unknown'
        
        if self.player.play_url(stream_url, track_title):
            self.player.set_volume(settings.DEFAULT_VOLUME)
            success = True
            # Add to history and context
            self.history.add('play', {'query': query}, success=True, execution_time=time.time() - start_time)
            self.context.add_song(track_title)
        else:
            print("❌ Failed to start playback")
        
        self.analytics.record_command('play', success, time.time() - start_time)
    
    def handle_volume(self, params: dict):
        """Handle volume command with tracking."""
        start_time = time.time()
        
        if 'error' in params:
            print(f"❌ {params['error']}")
            self.analytics.record_command('volume', False, time.time() - start_time)
            return
        
        if 'volume' not in params:
            print(f"❌ No volume specified. Params: {params}")
            self.analytics.record_command('volume', False, time.time() - start_time)
            return
        
        volume = params['volume']
        if not isinstance(volume, int):
            try:
                volume = int(volume)
            except (ValueError, TypeError):
                print(f"❌ Invalid volume value: {volume}")
                self.analytics.record_command('volume', False, time.time() - start_time)
                return
        
        self.player.set_volume(volume)
        print(f"🔊 Volume set to {volume}%")
        
        self.history.add('volume', params, success=True, execution_time=time.time() - start_time)
        self.analytics.record_command('volume', True, time.time() - start_time)
    
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
        """Handle voice input with multi-intent support and learning."""
        print("\n🎤 Activating voice control...")
        print("   (Press Ctrl+C to cancel)")
        
        # Prepare for voice input: pause or duck music if playing
        playback_state = self.player.prepare_for_voice_input()
        
        max_retries = 2
        retry_count = 0
        
        try:
            while retry_count <= max_retries:
                try:
                    voice_result = self.voice_listener.voice_play_command()
                    
                    if voice_result:
                        # Check if we got a ParsedCommand object from NLU
                        if hasattr(voice_result, 'intent'):
                            # It's a ParsedCommand from NLU
                            parsed_cmd = voice_result
                            print(f"📝 Intent: {parsed_cmd.intent} | Confidence: {parsed_cmd.confidence:.1%}")
                            if parsed_cmd.entities:
                                print(f"   Entities: {parsed_cmd.entities}")
                            
                            # Try multi-intent parsing
                            intents_to_execute = self.voice_listener.nlu_engine.parse_multi_intent(
                                parsed_cmd.original_text
                            ) if hasattr(self.voice_listener, 'nlu_engine') else [parsed_cmd]
                            
                            for intent_cmd in intents_to_execute:
                                command = intent_cmd.intent
                                
                                # Build params dict from ParsedCommand
                                params = intent_cmd.entities.copy() if intent_cmd.entities else {}
                                
                                # Map NLU entity names to handler parameter names
                                if 'level' in params:
                                    try:
                                        params['volume'] = int(params.pop('level'))
                                    except (ValueError, TypeError):
                                        print(f"❌ Could not parse volume level: {params.get('level')}")
                                        continue
                                
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
                                    params['query'] = ' '.join(parts) if parts else intent_cmd.original_text
                                
                                # Execute the parsed command
                                self._execute_command(command, params, intent_cmd.confidence)
                        else:
                            # It's a string from fallback mode - parse it normally
                            print(f"📝 Executing: {voice_result}")
                            command, params = self.parser.parse(str(voice_result))
                            self._execute_command(command, params, confidence=0.7)
                        
                        # Success! Exit retry loop
                        return
                    else:
                        # No voice result - check if we should retry
                        retry_count += 1
                        
                        if retry_count <= max_retries:
                            print(f"\n⚠️  Retry {retry_count}/{max_retries}...")
                            print("   (Make sure to speak clearly and wait for the 'Listening' prompt)")
                        else:
                            print("\n❌ Could not process voice input after multiple attempts")
                            print("   Tip: Use test mode to verify NLU works: python examples/test_voice_nlu.py")
                            return
                        
                except KeyboardInterrupt:
                    print("\n\n❌ Voice input cancelled")
                    return
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                    retry_count += 1
                    
                    if retry_count <= max_retries:
                        print(f"⚠️  Retry {retry_count}/{max_retries}...")
                    else:
                        return
        finally:
            # Always restore playback state after voice input
            self.player.restore_after_voice_input(playback_state)
    
    def _execute_command(self, command: str, params: dict, confidence: float = 1.0):
        """Execute a command and track it."""
        start_time = time.time()
        success = True
        
        try:
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
                success = False
        except Exception as e:
            import traceback
            print(f"❌ Command execution error: {e}")
            traceback.print_exc()
            success = False
        
        # Track in history and analytics
        if command not in ['status', 'search', 'unknown']:
            self.history.add(command, params, success=success, 
                           execution_time=time.time() - start_time, 
                           confidence=confidence)
        self.analytics.record_command(command, success, time.time() - start_time)
    
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
                
                elif command == 'repeat':
                    # Replay last command
                    last_cmd = self.history.get_last(1)
                    if last_cmd:
                        last = last_cmd[0]
                        print(f"🔄 Repeating: {last.intent} {last.entities}")
                        self._execute_command(last.intent, last.entities)
                    else:
                        print("❌ No commands in history")
                
                elif command == 'history':
                    self.history.print_history(limit=10)
                
                elif command == 'stats':
                    # Show analytics and corrections
                    self.analytics.print_report()
                    print("\n")
                    self.corrections_logger.print_report()
                
                elif command == 'context':
                    # Show playback context
                    self.context.print_context()
                
                elif command == 'listen':
                    # Start wake-word detection
                    if not self.wake_detector.listening:
                        self.wake_detector.start()
                        print("🎤 Always-on listening activated (say 'HQ' to activate voice commands)")
                    else:
                        print("⚠️  Wake-word detector already running")
                
                elif command == 'nolisten':
                    # Stop wake-word detection
                    if self.wake_detector.listening:
                        self.wake_detector.stop()
                        print("🛑 Always-on listening deactivated")
                    else:
                        print("⚠️  Wake-word detector not running")
                
                elif command == 'wake_stats':
                    # Show wake-word statistics
                    self.wake_detector.print_statistics()
                
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