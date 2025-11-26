"""
Voice input module for speech-to-text command recognition.
Uses the SpeechRecognition library with Google's free speech API.
"""

import speech_recognition as sr
from typing import Optional


class VoiceCommandListener:
    """Listen to microphone input and convert speech to text commands."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000  # Adjust sensitivity
        self.recognizer.dynamic_energy_threshold = True

    def listen_for_command(self, timeout: int = 10) -> Optional[str]:
        """
        Listen to the microphone for up to `timeout` seconds and return the recognized text.

        Returns:
            Recognized command as string, or None if no speech detected or recognition failed.
        """
        try:
            with sr.Microphone() as source:
                print("\n🎤 Listening... (speak now)")
                
                # Adjust recognizer for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Record audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=15)
                
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

    def voice_play_command(self) -> Optional[str]:
        """
        Listen for a voice command and return a play command.
        Example: User says "play sia cheap thrills" -> returns "play sia cheap thrills"
        """
        command = self.listen_for_command()
        if command:
            # If user didn't say "play", add it
            if not command.startswith("play"):
                if "play" in command:
                    # Extract the part after "play"
                    idx = command.index("play")
                    command = command[idx:]
                else:
                    command = f"play {command}"
            return command
        return None

    def voice_control(self) -> Optional[str]:
        """
        Listen for a generic voice control command.
        Returns the recognized text as-is.
        """
        return self.listen_for_command()
