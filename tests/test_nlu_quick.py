#!/usr/bin/env python3
"""
NLU System Quick Test - Verify everything is working
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(project_root / 'config'))

def test_imports():
    """Test that all modules import correctly."""
    print("\n" + "="*70)
    print("  Testing Imports")
    print("="*70 + "\n")
    
    try:
        from nlu_engine import NLUEngine, ParsedCommand
        print("✓ NLUEngine imported successfully")
        
        from entity_recognizer import EntityRecognizer, Entity
        print("✓ EntityRecognizer imported successfully")
        
        from voice_input import VoiceCommandListener
        print("✓ VoiceCommandListener imported successfully")
        
        from language_models import LANGUAGE_MODELS, list_languages
        print("✓ Language models imported successfully")
        
        from settings import settings
        print("✓ Settings imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_nlu_engine():
    """Test NLU engine functionality."""
    print("\n" + "="*70)
    print("  Testing NLU Engine")
    print("="*70 + "\n")
    
    try:
        from nlu_engine import NLUEngine
        
        engine = NLUEngine()
        
        # Test Swahili
        parsed = engine.parse("cheza backbencher")
        assert parsed.intent == 'play', f"Expected 'play', got '{parsed.intent}'"
        assert parsed.language == 'sw', f"Expected 'sw', got '{parsed.language}'"
        assert parsed.confidence > 0.7, f"Confidence {parsed.confidence} too low"
        print("✓ Swahili intent recognition works")
        
        # Test English
        parsed = engine.parse("play sia")
        assert parsed.intent == 'play', f"Expected 'play', got '{parsed.intent}'"
        print("✓ English intent recognition works")
        
        # Test volume
        parsed = engine.parse("volume up")
        assert parsed.intent == 'volume', f"Expected 'volume', got '{parsed.intent}'"
        assert 'direction' in parsed.entities, "Direction not in entities"
        print("✓ Volume intent with entities works")
        
        # Test pause
        parsed = engine.parse("simama")
        assert parsed.intent == 'pause', f"Expected 'pause', got '{parsed.intent}'"
        print("✓ Pause intent works")
        
        return True
    except Exception as e:
        print(f"✗ NLU test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_entity_recognizer():
    """Test entity recognizer functionality."""
    print("\n" + "="*70)
    print("  Testing Entity Recognizer")
    print("="*70 + "\n")
    
    try:
        from entity_recognizer import EntityRecognizer
        
        recognizer = EntityRecognizer()
        
        # Test artist extraction
        entities = recognizer.extract_entities("cheza backbencher", "sw")
        artist_found = any(e.type == 'artist' for e in entities)
        assert artist_found, "Artist entity not found"
        print("✓ Artist extraction works")
        
        # Test fuzzy matching
        match = recognizer.fuzzy_match("bakbencher", ["Backbencher", "Sia"], threshold=0.7)
        assert match == "Backbencher", f"Expected 'Backbencher', got '{match}'"
        print("✓ Fuzzy matching works")
        
        # Test adding artist
        recognizer.add_artist("Test Artist", ["test", "ta"], language="sw")
        print("✓ Adding custom artist works")
        
        # Test adding song
        recognizer.add_song("Test Song", ["Test Artist"], ["test song"])
        print("✓ Adding custom song works")
        
        return True
    except Exception as e:
        print(f"✗ Entity recognizer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_voice_listener():
    """Test voice command listener."""
    print("\n" + "="*70)
    print("  Testing Voice Command Listener")
    print("="*70 + "\n")
    
    try:
        from voice_input import VoiceCommandListener
        
        # Initialize with NLU
        listener = VoiceCommandListener(enable_nlu=True, primary_language='sw')
        assert listener.enable_nlu == True, "NLU not enabled"
        assert listener.nlu_engine is not None, "NLU engine not initialized"
        assert listener.entity_recognizer is not None, "Entity recognizer not initialized"
        print("✓ VoiceCommandListener initialized with NLU")
        
        # Test language switching
        listener.enable_language('en')
        print("✓ Language switching works")
        
        # Test NLU parsing
        parsed = listener.parse_command_with_nlu("cheza backbencher")
        assert parsed.intent == 'play', f"Expected 'play', got '{parsed.intent}'"
        print("✓ NLU parsing in voice listener works")
        
        return True
    except Exception as e:
        print(f"✗ Voice listener test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_language_models():
    """Test language models."""
    print("\n" + "="*70)
    print("  Testing Language Models")
    print("="*70 + "\n")
    
    try:
        from language_models import LANGUAGE_MODELS, get_language_model, list_languages
        
        # Check supported languages
        languages = list_languages()
        assert len(languages) >= 4, f"Expected at least 4 languages, got {len(languages)}"
        print(f"✓ {len(languages)} languages supported")
        
        # Check Swahili model
        sw_model = get_language_model('sw')
        assert 'play' in sw_model['intents'], "Play intent not in Swahili"
        assert 'cheza' in sw_model['intents']['play']['keywords'], "Swahili keyword not found"
        print("✓ Swahili language model valid")
        
        # Check English model
        en_model = get_language_model('en')
        assert 'play' in en_model['intents'], "Play intent not in English"
        print("✓ English language model valid")
        
        return True
    except Exception as e:
        print(f"✗ Language models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration():
    """Test configuration."""
    print("\n" + "="*70)
    print("  Testing Configuration")
    print("="*70 + "\n")
    
    try:
        from settings import settings
        
        assert settings.NLU_ENABLED == True, "NLU not enabled in settings"
        print("✓ NLU enabled in settings")
        
        assert settings.PRIMARY_LANGUAGE == 'sw', "Primary language not Swahili"
        print("✓ Primary language is Swahili")
        
        assert 'sw' in settings.SUPPORTED_LANGUAGES, "Swahili not in supported languages"
        print("✓ Swahili in supported languages")
        
        assert settings.NLU_CONFIDENCE_THRESHOLD > 0, "Invalid confidence threshold"
        print("✓ Valid confidence thresholds")
        
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_databases():
    """Test database files."""
    print("\n" + "="*70)
    print("  Testing Database Files")
    print("="*70 + "\n")
    
    try:
        import json
        from pathlib import Path
        
        config_dir = Path(__file__).parent / 'config'
        
        # Check artist database
        artist_db_path = config_dir / 'artist_database.json'
        assert artist_db_path.exists(), "Artist database not found"
        with open(artist_db_path) as f:
            artist_db = json.load(f)
        assert 'artists' in artist_db, "Artists key not in database"
        assert len(artist_db['artists']) > 0, "No artists in database"
        print(f"✓ Artist database valid ({len(artist_db['artists'])} artists)")
        
        # Check song database
        song_db_path = config_dir / 'song_database.json'
        assert song_db_path.exists(), "Song database not found"
        with open(song_db_path) as f:
            song_db = json.load(f)
        assert 'songs' in song_db, "Songs key not in database"
        assert len(song_db['songs']) > 0, "No songs in database"
        print(f"✓ Song database valid ({len(song_db['songs'])} songs)")
        
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n╔" + "="*68 + "╗")
    print("║" + " "*15 + "NLU SYSTEM - QUICK TEST SUITE" + " "*25 + "║")
    print("╚" + "="*68 + "╝")
    
    tests = [
        ("Imports", test_imports),
        ("NLU Engine", test_nlu_engine),
        ("Entity Recognizer", test_entity_recognizer),
        ("Voice Listener", test_voice_listener),
        ("Language Models", test_language_models),
        ("Configuration", test_configuration),
        ("Databases", test_databases),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*70)
    print("  Test Summary")
    print("="*70 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}  {test_name}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 All tests passed! NLU system is ready to use.\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the output above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
