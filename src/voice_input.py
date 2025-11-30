"""
Voice input module for speech-to-text command recognition.

Features:
- Speech-to-text using Google's free speech API
- NLU (Natural Language Understanding) for intent & entity extraction
- Multi-language support (Swahili, English, Spanish, Portuguese, French)
- Entity recognition (artist names, song titles with nickname support)
- Fuzzy matching for slang and colloquial terms
"""

import speech_recognition as sr
from typing import Optional, Dict
from pathlib import Path
import sys

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from nlu_engine import NLUEngine, ParsedCommand
from entity_recognizer import EntityRecognizer


class VoiceCommandListener:
    """Listen to microphone input and convert speech to text with NLU understanding."""

    def __init__(self, enable_nlu: bool = True, primary_language: str = 'sw'):
        """
        Initialize voice command listener.
        
        Args:
            enable_nlu: Enable Natural Language Understanding (default: True)
            primary_language: Primary language for NLU (default: 'sw' for Swahili)
        """
        self.recognizer = sr.Recognizer()
        
        # Tuned settings for better voice recognition:
        # - energy_threshold: Lower = more sensitive to quiet voices (default 300)
        # - dynamic_energy_threshold: Adjust threshold based on noise
        self.recognizer.energy_threshold = 2000  # Moderate sensitivity (not 4000 which is too strict)
        self.recognizer.dynamic_energy_threshold = True
        
        # Pause threshold: seconds of silence after speech ends before processing
        # Higher value = waits longer for speaker to finish (better for natural speech)
        self.recognizer.pause_threshold = 1.8  # Wait 1.8 seconds of silence before deciding speech ended
        self.recognizer.non_speaking_duration = 0.7  # More time before detecting start of speech
        self.recognizer.operation_timeout = 7  # Timeout for entire listen operation
        
        # Initialize NLU if enabled
        self.enable_nlu = enable_nlu
        self.primary_language = primary_language
        
        if self.enable_nlu:
            self.nlu_engine = NLUEngine()
            self.entity_recognizer = EntityRecognizer()
            print(f"✓ NLU engine initialized (Primary language: {primary_language})")
        else:
            self.nlu_engine = None
            self.entity_recognizer = None

    def listen_for_command(self, timeout: int = 10) -> Optional[str]:
        """
        Listen to the microphone for up to `timeout` seconds and return the recognized text.

        Returns:
            Recognized command as string, or None if no speech detected or recognition failed.
        """
        try:
            with sr.Microphone() as source:
                print("\n🎤 Listening... (speak your command)")
                
                # Adjust recognizer for ambient noise
                # Longer duration for better noise profile (avoids cutting off early)
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                
                # Keep energy threshold at moderate level
                self.recognizer.energy_threshold = 2000
                
                try:
                    # Listen with better timing:
                    # - timeout: max seconds to wait for sound to START
                    # - phrase_time_limit: max seconds to RECORD once phrase starts
                    # - Increased phrase_time_limit to allow natural speech pauses
                    audio = self.recognizer.listen(
                        source, 
                        timeout=timeout,              # How long to wait for sound to start (10 sec)
                        phrase_time_limit=15          # Max recording duration (was 5, now 15 for longer speech)
                    )
                except sr.RequestError as e:
                    print(f"❌ Listening error: {e}")
                    return None
                except sr.UnknownValueError as e:
                    print(f"❌ Listening timed out: {e}")
                    return None
                
            print("🔄 Processing speech...")
            
            # Try Google Speech Recognition (free, no API key needed)
            try:
                text = self.recognizer.recognize_google(audio)
                print(f"✓ Recognized: '{text}'")
                return text.lower()
            except sr.UnknownValueError:
                print("❌ Could not understand audio. Please speak clearly.")
                return None
            except sr.RequestError as e:
                print(f"❌ Speech API error: {e}")
                return None
                
        except sr.RequestError:
            print("❌ Microphone not available")
            return None
        except sr.UnknownValueError:
            print("❌ No speech detected")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def parse_command_with_nlu(self, text: str) -> ParsedCommand:
        """
        Parse voice command using NLU.
        
        Args:
            text: Raw voice input text
            
        Returns:
            ParsedCommand with intent, entities, and confidence
        """
        if not self.enable_nlu or not self.nlu_engine:
            # Fallback to basic parsing
            return ParsedCommand(
                intent='unknown',
                entities={},
                confidence=0.0,
                original_text=text,
                normalized_text=text.lower(),
                language='unknown',
            )
        
        # Parse with NLU engine
        parsed = self.nlu_engine.parse(text)
        
        # Extract and resolve entities
        if parsed.intent == 'play' or parsed.intent == 'search':
            entities_list = self.entity_recognizer.extract_entities(
                parsed.normalized_text,
                detected_language=parsed.language,
            )
            
            # Add recognized entities to parsed command
            for entity in entities_list:
                if entity.type == 'artist':
                    parsed.entities['artist'] = entity.normalized_value
                elif entity.type == 'song':
                    parsed.entities['song'] = entity.normalized_value
                elif entity.type == 'album':
                    parsed.entities['album'] = entity.normalized_value
        
        return parsed

    def voice_play_command(self) -> Optional[ParsedCommand]:
        """
        Listen for a voice play command and parse it with NLU with fallback chains.
        
        Fallback chain:
        1. Try speech-to-text with NLU parsing
        2. If no audio detected, prompt for text input
        3. If confidence low (<0.7), ask user to clarify
        4. Fall back to simple keyword matching
        
        Returns:
            ParsedCommand with intent='play' and extracted entities (artist, song, etc.)
            or None if no command recognized after all fallbacks.
            
        Example:
            User says "cheza backbencher ya toxic" (Swahili)
            -> ParsedCommand(
                intent='play',
                entities={'artist': 'Backbencher', 'song': 'Toxic'},
                confidence=0.95,
                language='sw'
            )
        """
        # ===== FALLBACK 1: Try Speech-to-Text =====
        text = self.listen_for_command()
        
        if not text:
            # No text recognized, return None to let the main app retry
            return None
        
        if self.enable_nlu:
            parsed = self.parse_command_with_nlu(text)
            
            # ===== FALLBACK 3: Confidence-Based Clarification =====
            if parsed.confidence < 0.7 and parsed.intent != 'unknown':
                print(f"\n🤔 Low confidence detection ({parsed.confidence:.0%})")
                print(f"   Detected: {parsed.intent} with entities {parsed.entities}")
                
                confirm = input("   Is this correct? (y/n/type correct command): ").strip().lower()
                
                if confirm == 'n':
                    # User wants to try again
                    alt_text = input("   Say or type again: ").strip()
                    if alt_text:
                        parsed = self.parse_command_with_nlu(alt_text)
                elif confirm and confirm not in ['y', 'n']:
                    # User provided correction
                    parsed = self.parse_command_with_nlu(confirm)
            
            # ===== FALLBACK 4: Intent Validation & Simple Matching =====
            if parsed.intent == 'unknown' or not text:
                print(f"⚠️  Could not determine intent confidently")
                
                # Try simple keyword matching as fallback
                text_lower = text.lower() if text else ""
                
                if any(keyword in text_lower for keyword in ['play', 'cheza', 'ucheze']):
                    parsed.intent = 'play'
                    parsed.confidence = 0.5
                    parsed.entities['query'] = text
                    print(f"📍 Using keyword fallback: play '{text}'")
                else:
                    # Default to play with full text as query
                    parsed.intent = 'play'
                    parsed.confidence = 0.3
                    parsed.entities['query'] = text
                    print(f"📍 Defaulting to play with query: '{text}'")
            
            # If intent isn't play, try to convert it
            if parsed.intent != 'play':
                print(f"ℹ️  Detected intent: {parsed.intent} (confidence: {parsed.confidence:.1%})")
                
                # If not confident about intent, default to play for this method
                if parsed.intent == 'unknown' or parsed.confidence < 0.5:
                    parsed.intent = 'play'
                    if 'query' not in parsed.entities:
                        parsed.entities['query'] = text
            
            print(f"✅ Final: Intent={parsed.intent} | Confidence={parsed.confidence:.1%}")
            if parsed.entities:
                print(f"   Entities: {parsed.entities}")
            return parsed
        else:
            # ===== FALLBACK 4 (No NLU): Simple Parsing =====
            if not text.startswith("play"):
                if "play" in text:
                    idx = text.index("play")
                    text = text[idx:]
                else:
                    text = f"play {text}"
            
            return ParsedCommand(
                intent='play',
                entities={'query': text.replace('play ', '')},
                confidence=0.7,
                original_text=text,
                normalized_text=text.lower(),
                language=self.primary_language,
            )

    def voice_control(self) -> Optional[ParsedCommand]:
        """
        Listen for a generic voice control command with NLU parsing.
        
        Returns:
            ParsedCommand with detected intent (play, pause, volume, etc.)
            or None if no command recognized.
        """
        text = self.listen_for_command()
        if not text:
            return None
        
        if self.enable_nlu:
            parsed = self.parse_command_with_nlu(text)
            
            if parsed.intent != 'unknown':
                print(f"🎯 Intent: {parsed.intent} | Entities: {parsed.entities} | Confidence: {parsed.confidence:.1%}")
            else:
                print(f"⚠️  Could not determine intent. Trying as search query...")
                parsed.intent = 'search'
                parsed.entities['query'] = text
            
            return parsed
        else:
            # Fallback to basic parsing
            return ParsedCommand(
                intent='unknown',
                entities={'query': text},
                confidence=0.5,
                original_text=text,
                normalized_text=text.lower(),
                language=self.primary_language,
            )

    def enable_language(self, language_code: str) -> None:
        """
        Enable support for a language.
        
        Args:
            language_code: Language code (sw, en, es, pt, fr)
        """
        if self.enable_nlu and self.nlu_engine:
            print(f"✓ Language '{language_code}' enabled")
            self.primary_language = language_code

    def add_artist_alias(self, artist_name: str, aliases: list) -> None:
        """
        Add artist aliases for better recognition.
        
        Args:
            artist_name: Official artist name
            aliases: List of nicknames/variations
        """
        if self.enable_nlu and self.entity_recognizer:
            self.entity_recognizer.add_artist(
                artist_name,
                aliases,
                language=self.primary_language,
            )

    def test_command(self, text: str) -> Optional[ParsedCommand]:
        """
        Test voice command with simulated text input (no STT).
        
        Useful for:
        - Testing NLU without microphone
        - Testing Swahili commands reliably
        - Debugging voice parsing
        
        Args:
            text: Command text to parse (simulates what STT would produce)
            
        Returns:
            ParsedCommand with intent, entities, and confidence
            
        Example:
            listener.test_command("cheza backbencher ya toxic")
            # Returns ParsedCommand(intent='play', entities={'artist': 'Backbencher', 'song': 'Toxic'})
        """
        print(f"🧪 Test Mode: '{text}'")
        
        if not self.enable_nlu:
            print("❌ NLU not enabled")
            return None
        
        # Parse with NLU
        parsed = self.parse_command_with_nlu(text)
        
        print(f"\n📊 Parsing Result:")
        print(f"   Intent: {parsed.intent}")
        print(f"   Language: {parsed.language}")
        print(f"   Confidence: {parsed.confidence:.1%}")
        
        if parsed.entities:
            print(f"   Entities:")
            for key, value in parsed.entities.items():
                print(f"     • {key}: {value}")
        
        return parsed
