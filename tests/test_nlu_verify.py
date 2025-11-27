#!/usr/bin/env python3
"""
Simple NLU System Test - Verify core functionality
"""

import sys
from pathlib import Path

# Set up paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    print("\n╔" + "="*68 + "╗")
    print("║" + " "*15 + "NLU SYSTEM - VERIFICATION TEST" + " "*23 + "║")
    print("╚" + "="*68 + "╝\n")
    
    # Test 1: NLU Engine
    print("="*70)
    print("TEST 1: NLU Engine")
    print("="*70)
    
    try:
        from src.nlu_engine import NLUEngine
        engine = NLUEngine()
        
        # Test Swahili
        parsed = engine.parse("cheza backbencher")
        assert parsed.intent == 'play'
        assert parsed.language == 'sw'
        print("✓ Swahili 'cheza' recognized as 'play' intent")
        print(f"  Confidence: {parsed.confidence:.1%}, Language: {parsed.language}")
        
        # Test English
        parsed = engine.parse("volume up")
        assert parsed.intent == 'volume'
        assert 'direction' in parsed.entities
        print("✓ English 'volume up' recognized correctly")
        print(f"  Direction: {parsed.entities['direction']}")
        
    except Exception as e:
        print(f"✗ NLU Engine test failed: {e}")
        return 1
    
    # Test 2: Entity Recognizer
    print("\n" + "="*70)
    print("TEST 2: Entity Recognizer")
    print("="*70)
    
    try:
        from src.entity_recognizer import EntityRecognizer
        recognizer = EntityRecognizer()
        
        # Test artist extraction
        entities = recognizer.extract_entities("cheza backbencher", "sw")
        artist_found = any(e.type == 'artist' for e in entities)
        assert artist_found
        print("✓ Artist 'Backbencher' extracted successfully")
        
        # Show extracted entities
        for entity in entities:
            print(f"  - {entity.type}: '{entity.value}' → '{entity.normalized_value}'")
        
    except Exception as e:
        print(f"✗ Entity Recognizer test failed: {e}")
        return 1
    
    # Test 3: Language Models
    print("\n" + "="*70)
    print("TEST 3: Language Models")
    print("="*70)
    
    try:
        from config.language_models import list_languages, get_language_model
        
        languages = list_languages()
        print(f"✓ {len(languages)} languages supported:")
        
        for lang_info in languages:
            print(f"  - {lang_info['code']}: {lang_info['name']}")
        
        # Show Swahili commands
        sw_model = get_language_model('sw')
        play_keywords = sw_model['intents']['play']['keywords']
        print(f"\n✓ Swahili play commands: {', '.join(play_keywords)}")
        
    except Exception as e:
        print(f"✗ Language Models test failed: {e}")
        return 1
    
    # Test 4: Configuration
    print("\n" + "="*70)
    print("TEST 4: Configuration")
    print("="*70)
    
    try:
        from config.settings import settings
        
        print(f"✓ NLU Enabled: {settings.NLU_ENABLED}")
        print(f"✓ Primary Language: {settings.PRIMARY_LANGUAGE}")
        print(f"✓ Supported Languages: {', '.join(settings.SUPPORTED_LANGUAGES)}")
        print(f"✓ Confidence Threshold: {settings.NLU_CONFIDENCE_THRESHOLD}")
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return 1
    
    # Test 5: File Existence
    print("\n" + "="*70)
    print("TEST 5: File Existence")
    print("="*70)
    
    try:
        import json
        
        files_to_check = [
            ('src/nlu_engine.py', 'NLU Engine'),
            ('src/entity_recognizer.py', 'Entity Recognizer'),
            ('src/voice_input.py', 'Voice Input (Updated)'),
            ('config/language_models.py', 'Language Models'),
            ('config/settings.py', 'Settings'),
            ('config/artist_database.json', 'Artist Database'),
            ('config/song_database.json', 'Song Database'),
            ('docs/NLU_README.md', 'NLU README'),
            ('docs/NLU_GUIDE.md', 'NLU Complete Guide'),
            ('docs/NLU_INTEGRATION.md', 'Integration Guide'),
            ('docs/NLU_QUICK_REFERENCE.md', 'Quick Reference'),
            ('examples/nlu_examples.py', 'NLU Examples'),
        ]
        
        all_exist = True
        for file_path, description in files_to_check:
            full_path = project_root / file_path
            exists = "✓" if full_path.exists() else "✗"
            print(f"{exists} {description:25} ({file_path})")
            if not full_path.exists():
                all_exist = False
        
        if not all_exist:
            return 1
        
        # Check database contents
        print("\n✓ Checking database contents:")
        artist_db_path = project_root / 'config' / 'artist_database.json'
        with open(artist_db_path) as f:
            artist_db = json.load(f)
        print(f"  - Artists in database: {len(artist_db['artists'])}")
        
        song_db_path = project_root / 'config' / 'song_database.json'
        with open(song_db_path) as f:
            song_db = json.load(f)
        print(f"  - Songs in database: {len(song_db['songs'])}")
        
    except Exception as e:
        print(f"✗ File existence test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Summary
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED - NLU SYSTEM IS READY!")
    print("="*70)
    
    print("\n📚 Documentation:")
    print("  • Quick Start: docs/NLU_QUICK_REFERENCE.md")
    print("  • Full Guide: docs/NLU_GUIDE.md")
    print("  • Integration: docs/NLU_INTEGRATION.md")
    
    print("\n🚀 Next Steps:")
    print("  1. Run examples: python examples/nlu_examples.py")
    print("  2. Test voice: Use voice_play_command() with NLU enabled")
    print("  3. Add artists: Update config/artist_database.json")
    print("  4. Integrate: See docs/NLU_INTEGRATION.md")
    
    print("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
