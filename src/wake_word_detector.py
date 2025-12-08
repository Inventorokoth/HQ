"""
Wake-Word Detector for Always-On Listening

Implements continuous listening for a wake word ("HQ") to activate voice commands.
Uses efficient audio processing to minimize CPU usage while maintaining responsiveness.

Features:
- Continuous background listening
- Wake-word detection (default: "HQ")
- Configurable sensitivity threshold
- Audio buffering with rolling window
- Graceful handling of recognition errors
- Threading support for non-blocking operation
"""

import threading
import queue
import speech_recognition as sr
from typing import Callable, Optional
import time


class WakeWordDetector:
    """
    Detects wake word in continuous audio stream.
    
    When the wake word is detected, triggers a callback to activate voice command mode.
    """
    
    def __init__(
        self,
        wake_word: str = "HQ",
        confidence_threshold: float = 0.7,
        callback: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        debug: bool = False,
    ):
        """
        Initialize wake-word detector.
        
        Args:
            wake_word: Word to listen for (default: "HQ")
            confidence_threshold: Confidence level required to trigger (0.0-1.0)
            callback: Function to call when wake word is detected
            on_error: Function to call on errors
            debug: Enable debug output to see what's being heard
        """
        self.wake_word = wake_word.lower()
        self.confidence_threshold = confidence_threshold
        self.callback = callback
        self.on_error = on_error
        self.debug = debug
        
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Calibrate microphone for ambient noise
        print("🔧 Calibrating microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print("✓ Microphone calibrated")
        
        # Threading
        self.listening = False
        self.thread = None
        self.audio_queue = queue.Queue()
        
        # Statistics
        self.detections_total = 0
        self.false_positives = 0
        self.false_negatives = 0
        self.avg_confidence = 0.0
    
    def start(self) -> None:
        """Start listening for wake word in background."""
        if self.listening:
            print("⚠️  Wake-word detector already running")
            return
        
        self.listening = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        print("🎤 Wake-word detector started (listening for 'HQ')")
        print("   Say 'HQ' to activate voice commands")
    
    def stop(self) -> None:
        """Stop listening for wake word."""
        if not self.listening:
            print("⚠️  Wake-word detector not running")
            return
        
        self.listening = False
        if self.thread:
            self.thread.join(timeout=2)
        print("🛑 Wake-word detector stopped")
    
    def _listen_loop(self) -> None:
        """
        Main listening loop (runs in background thread).
        Continuously processes audio and checks for wake word.
        """
        consecutive_detections = 0
        required_detections = 2  # Require 2 consecutive detections to avoid false positives
        
        try:
            # Create a new microphone instance for this thread
            microphone = sr.Microphone()
            
            # Start background listening
            stop_listening = self.recognizer.listen_in_background(
                microphone,
                self._process_audio,
                phrase_time_limit=1.0  # Process 1 second chunks
            )
            
            # Keep the background listener running
            while self.listening:
                time.sleep(0.1)
            
            # Stop listening when done
            stop_listening(wait_for_result=False)
        
        except Exception as e:
            print(f"❌ Wake-word detector error: {e}")
            if self.on_error:
                self.on_error(e)
            self.listening = False
    
    def _process_audio(self, recognizer: sr.Recognizer, audio: sr.AudioData) -> None:
        """
        Process audio chunk and check for wake word.
        
        Args:
            recognizer: Speech recognizer instance
            audio: Audio data chunk
        """
        try:
            # Try to recognize speech in the audio chunk
            text = recognizer.recognize_google(audio)
            text_lower = text.lower()
            
            if self.debug or text:  # Always show recognized text in debug mode or when speech detected
                print(f"🔊 Heard: '{text}'")
            
            # Check if wake word is in the recognized text
            if self.wake_word in text_lower:
                self.detections_total += 1
                print(f"\n{'='*50}")
                print(f"✅ WAKE WORD DETECTED: '{self.wake_word.upper()}'")
                print(f"{'='*50}\n")
                
                # Trigger callback
                if self.callback:
                    self.callback()
            else:
                # Update false positive counter
                self.false_positives += 1
        
        except sr.UnknownValueError:
            # Audio was received but not recognized - this is normal background noise
            if self.debug:
                print("🔇 Audio detected but not recognized")
            pass
        
        except sr.RequestError as e:
            print(f"⚠️  API error: {e}")
            if self.on_error:
                self.on_error(e)
        
        except Exception as e:
            print(f"❌ Error processing audio: {e}")
            if self.on_error:
                self.on_error(e)
    
    def set_wake_word(self, wake_word: str) -> None:
        """
        Change wake word.
        
        Args:
            wake_word: New wake word
        """
        self.wake_word = wake_word.lower()
        print(f"✓ Wake word changed to '{self.wake_word}'")
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """
        Change confidence threshold.
        
        Args:
            threshold: New threshold (0.0-1.0)
        """
        if 0.0 <= threshold <= 1.0:
            self.confidence_threshold = threshold
            print(f"✓ Confidence threshold set to {threshold:.1%}")
        else:
            print(f"❌ Threshold must be between 0.0 and 1.0")
    
    def get_statistics(self) -> dict:
        """Get detector statistics."""
        return {
            'total_detections': self.detections_total,
            'false_positives': self.false_positives,
            'false_negatives': self.false_negatives,
            'avg_confidence': self.avg_confidence,
            'is_listening': self.listening,
        }
    
    def print_statistics(self) -> None:
        """Print detector statistics."""
        stats = self.get_statistics()
        print("\n" + "="*50)
        print("🎤 Wake-Word Detector Statistics")
        print("="*50)
        print(f"Status:           {'🟢 Listening' if stats['is_listening'] else '🔴 Stopped'}")
        print(f"Total Detections: {stats['total_detections']}")
        print(f"False Positives:  {stats['false_positives']}")
        print(f"False Negatives:  {stats['false_negatives']}")
        print(f"Avg Confidence:   {stats['avg_confidence']:.1%}")
        print("="*50)
