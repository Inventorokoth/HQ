#!/usr/bin/env python3
"""
Test suite for wake-word detector functionality.

Tests:
- Wake-word detector initialization
- Wake-word detection logic
- Statistics tracking
- Error handling
- Integration with main app
"""

import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import speech_recognition as sr

# Add src to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.wake_word_detector import WakeWordDetector


def create_mocked_detector():
    """Helper to create a detector with properly mocked audio/speech components."""
    with patch('src.wake_word_detector.sr.Microphone') as mock_mic, \
         patch.object(sr.Recognizer, 'adjust_for_ambient_noise'):
        
        # Mock microphone
        mock_mic_instance = MagicMock()
        mock_mic.return_value = mock_mic_instance
        mock_mic_instance.__enter__.return_value = mock_mic_instance
        mock_mic_instance.__exit__.return_value = None
        
        detector = WakeWordDetector(wake_word="HQ", confidence_threshold=0.7)
        return detector


def test_wake_word_detector_initialization():
    """Test that WakeWordDetector initializes correctly."""
    print("\n" + "="*60)
    print("TEST 1: Wake-Word Detector Initialization")
    print("="*60)
    
    try:
        # Patch both the microphone and recognizer's adjust method
        with patch('src.wake_word_detector.sr.Microphone'), \
             patch.object(sr.Recognizer, 'adjust_for_ambient_noise'):
            
            detector = WakeWordDetector(
                wake_word="HQ",
                confidence_threshold=0.7
            )
            
            assert detector.wake_word == "hq", "Wake word should be lowercase"
            assert detector.confidence_threshold == 0.7, "Confidence threshold not set"
            assert detector.listening == False, "Should not be listening initially"
            assert detector.detections_total == 0, "Should have 0 detections initially"
            
            print("✅ PASS: Detector initialized correctly")
            print(f"   - Wake word: {detector.wake_word}")
            print(f"   - Confidence threshold: {detector.confidence_threshold}")
            print(f"   - Listening: {detector.listening}")
            return True
    except AssertionError as e:
        print(f"❌ FAIL: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wake_word_detection_logic():
    """Test that wake-word detection logic works correctly."""
    print("\n" + "="*60)
    print("TEST 2: Wake-Word Detection Logic")
    print("="*60)
    
    try:
        with patch('src.wake_word_detector.sr.Microphone'), \
             patch.object(sr.Recognizer, 'adjust_for_ambient_noise'):
            
            detector = WakeWordDetector(wake_word="HQ")
            
            # Create mock recognizer and audio
            mock_recognizer = Mock()
            mock_audio = Mock()
            
            # Test 1: Wake word detected
            with patch.object(mock_recognizer, 'recognize_google', return_value="HQ"):
                detector._process_audio(mock_recognizer, mock_audio)
                assert detector.detections_total == 1, "Should have 1 detection"
                print("✅ PASS: Wake word 'HQ' detected correctly")
            
            # Test 2: Wake word in phrase
            detector.detections_total = 0  # Reset
            with patch.object(mock_recognizer, 'recognize_google', return_value="HQ play music"):
                detector._process_audio(mock_recognizer, mock_audio)
                assert detector.detections_total == 1, "Should detect 'HQ' in phrase"
                print("✅ PASS: Wake word detected in phrase")
            
            # Test 3: Wake word not detected
            detector.detections_total = 0  # Reset
            detector.false_positives = 0
            with patch.object(mock_recognizer, 'recognize_google', return_value="play music"):
                detector._process_audio(mock_recognizer, mock_audio)
                assert detector.detections_total == 0, "Should not have detections"
                assert detector.false_positives == 1, "Should increment false positives"
                print("✅ PASS: Non-wake-word audio ignored")
            
            # Test 4: Case insensitivity
            detector.detections_total = 0
            with patch.object(mock_recognizer, 'recognize_google', return_value="hq play music"):
                detector._process_audio(mock_recognizer, mock_audio)
                assert detector.detections_total == 1, "Should detect lowercase 'hq'"
                print("✅ PASS: Wake word detection is case-insensitive")
            
            return True
    except AssertionError as e:
        print(f"❌ FAIL: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_statistics_tracking():
    """Test that statistics are tracked correctly."""
    print("\n" + "="*60)
    print("TEST 3: Statistics Tracking")
    print("="*60)
    
    try:
        with patch('src.wake_word_detector.sr.Microphone'), \
             patch.object(sr.Recognizer, 'adjust_for_ambient_noise'):
            
            detector = WakeWordDetector(wake_word="HQ")
            mock_recognizer = Mock()
            mock_audio = Mock()
            
            # Simulate some detections
            with patch.object(mock_recognizer, 'recognize_google', return_value="HQ"):
                detector._process_audio(mock_recognizer, mock_audio)
                detector._process_audio(mock_recognizer, mock_audio)
            
            with patch.object(mock_recognizer, 'recognize_google', return_value="play music"):
                detector._process_audio(mock_recognizer, mock_audio)
            
            stats = detector.get_statistics()
            
            assert stats['total_detections'] == 2, "Should have 2 detections"
            assert stats['false_positives'] == 1, "Should have 1 false positive"
            assert stats['is_listening'] == False, "Should not be listening"
            
            print("✅ PASS: Statistics tracked correctly")
            print(f"   - Total detections: {stats['total_detections']}")
            print(f"   - False positives: {stats['false_positives']}")
            print(f"   - Listening: {stats['is_listening']}")
            return True
    except AssertionError as e:
        print(f"❌ FAIL: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_error_handling():
    """Test error handling for unknown audio and API errors."""
    print("\n" + "="*60)
    print("TEST 4: Error Handling")
    print("="*60)
    
    try:
        from speech_recognition import UnknownValueError, RequestError
        
        with patch('src.wake_word_detector.sr.Microphone'), \
             patch.object(sr.Recognizer, 'adjust_for_ambient_noise'):
            
            detector = WakeWordDetector(wake_word="HQ")
            mock_recognizer = Mock()
            mock_audio = Mock()
            
            # Test 1: UnknownValueError (no speech detected)
            with patch.object(mock_recognizer, 'recognize_google', side_effect=UnknownValueError()):
                detector._process_audio(mock_recognizer, mock_audio)
                # Should not crash, just silently continue
                print("✅ PASS: UnknownValueError handled gracefully")
            
            # Test 2: RequestError (API error)
            with patch.object(mock_recognizer, 'recognize_google', side_effect=RequestError("API Error")):
                detector._process_audio(mock_recognizer, mock_audio)
                # Should not crash, just print warning
                print("✅ PASS: RequestError handled gracefully")
            
            # Test 3: Generic exception
            with patch.object(mock_recognizer, 'recognize_google', side_effect=Exception("Unknown error")):
                detector._process_audio(mock_recognizer, mock_audio)
                # Should not crash
                print("✅ PASS: Generic exceptions handled gracefully")
            
            return True
    except AssertionError as e:
        print(f"❌ FAIL: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_wake_word_configuration():
    """Test configuring wake word and threshold."""
    print("\n" + "="*60)
    print("TEST 5: Wake-Word Configuration")
    print("="*60)
    
    try:
        with patch('src.wake_word_detector.sr.Microphone'), \
             patch.object(sr.Recognizer, 'adjust_for_ambient_noise'):
            
            detector = WakeWordDetector(wake_word="HELLO")
            
            # Test changing wake word
            detector.set_wake_word("GOODBYE")
            assert detector.wake_word == "goodbye", "Wake word should be updated"
            print("✅ PASS: Wake word updated to 'goodbye'")
            
            # Test changing confidence threshold
            detector.set_confidence_threshold(0.8)
            assert detector.confidence_threshold == 0.8, "Threshold should be updated"
            print("✅ PASS: Confidence threshold updated to 0.8")
            
            # Test invalid threshold
            detector.set_confidence_threshold(1.5)  # Invalid
            assert detector.confidence_threshold == 0.8, "Invalid threshold should be rejected"
            print("✅ PASS: Invalid threshold (1.5) rejected")
            
            return True
    except AssertionError as e:
        print(f"❌ FAIL: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_callback_invocation():
    """Test that callback is invoked when wake word is detected."""
    print("\n" + "="*60)
    print("TEST 6: Callback Invocation")
    print("="*60)
    
    try:
        with patch('src.wake_word_detector.sr.Microphone'), \
             patch.object(sr.Recognizer, 'adjust_for_ambient_noise'):
            
            callback_mock = Mock()
            detector = WakeWordDetector(
                wake_word="HQ",
                callback=callback_mock
            )
            
            mock_recognizer = Mock()
            mock_audio = Mock()
            
            # Wake word detected - callback should be called
            with patch.object(mock_recognizer, 'recognize_google', return_value="HQ"):
                detector._process_audio(mock_recognizer, mock_audio)
                callback_mock.assert_called_once()
                print("✅ PASS: Callback invoked when wake word detected")
            
            # Reset callback
            callback_mock.reset_mock()
            
            # No wake word - callback should not be called
            with patch.object(mock_recognizer, 'recognize_google', return_value="hello"):
                detector._process_audio(mock_recognizer, mock_audio)
                callback_mock.assert_not_called()
                print("✅ PASS: Callback not invoked when wake word not detected")
            
            return True
    except AssertionError as e:
        print(f"❌ FAIL: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_main_app_integration():
    """Test that wake-word detector integrates with main app."""
    print("\n" + "="*60)
    print("TEST 7: Main App Integration")
    print("="*60)
    
    try:
        # Check that WakeWordDetector can be imported and used by main app
        from main import MusicStreamApp
        
        with patch('src.wake_word_detector.sr.Microphone'), \
             patch.object(sr.Recognizer, 'adjust_for_ambient_noise'), \
             patch('src.youtube_client.YouTubeClient'), \
             patch('src.player.MusicPlayer'), \
             patch('src.voice_input.VoiceCommandListener'):
            
            app = MusicStreamApp()
            
            # Check that detector is initialized
            assert hasattr(app, 'wake_detector'), "App should have wake_detector"
            assert app.wake_detector.wake_word == "hq", "Wake word should be 'hq'"
            print("✅ PASS: WakeWordDetector integrated into main app")
            
            # Check callback exists
            assert hasattr(app, '_on_wake_word_detected'), "App should have callback"
            print("✅ PASS: Wake-word callback method exists")
            
            return True
    except AssertionError as e:
        print(f"❌ FAIL: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "🎤 " * 20)
    print("WAKE-WORD DETECTOR TEST SUITE")
    print("🎤 " * 20)
    
    tests = [
        test_wake_word_detector_initialization,
        test_wake_word_detection_logic,
        test_statistics_tracking,
        test_error_handling,
        test_wake_word_configuration,
        test_callback_invocation,
        test_main_app_integration,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ CRASH: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("Wake-word detector is working correctly!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    print("="*60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
