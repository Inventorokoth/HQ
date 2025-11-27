#!/usr/bin/env python3
"""
NLU System Examples and Tests

Demonstrates how to use the NLU engine, entity recognizer, and voice listener
with multi-language support.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.nlu_engine import NLUEngine
from src.entity_recognizer import EntityRecognizer
from src.voice_input import VoiceCommandListener
from config.language_models import get_language_model, list_languages, SWAHILI_MODELS, ENGLISH_MODELS


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def example_1_nlu_engine():
    """Example 1: Basic NLU Engine Usage"""
    print_section("Example 1: NLU Engine - Intent Recognition")
    
    engine = NLUEngine()
    
    # Test commands in different languages
    test_commands = [
        ("cheza backbencher", "Swahili play command"),
        ("simama", "Swahili pause command"),
        ("play sia cheap thrills", "English play command"),
        ("pause", "English pause command"),
        ("ongeza kasi", "Swahili volume command"),
        ("volume up", "English volume command"),
    ]
    
    for command, description in test_commands:
        print(f"Command: '{command}' ({description})")
        parsed = engine.parse(command)
        print(f"  Intent: {parsed.intent}")
        print(f"  Language: {parsed.language}")
        print(f"  Confidence: {parsed.confidence:.1%}")
        print(f"  Entities: {parsed.entities}")
        print()


def example_2_entity_recognition():
    """Example 2: Entity Recognition and Resolution"""
    print_section("Example 2: Entity Recognition")
    
    recognizer = EntityRecognizer()
    
    # Test entity extraction
    test_texts = [
        ("cheza backbencher ya toxic", "Swahili with artist and song"),
        ("play sia", "English with artist"),
        ("find cheap thrills", "English with song title"),
    ]
    
    for text, description in test_texts:
        print(f"Text: '{text}' ({description})")
        entities = recognizer.extract_entities(text, detected_language='sw')
        
        if entities:
            for entity in entities:
                print(f"  {entity.type.capitalize()}: '{entity.value}'")
                print(f"    -> Canonical: '{entity.normalized_value}'")
                print(f"    -> Confidence: {entity.confidence:.1%}")
        else:
            print(f"  (No entities found)")
        print()


def example_3_language_models():
    """Example 3: Language Models and Multi-Language Support"""
    print_section("Example 3: Supported Languages")
    
    languages = list_languages()
    print(f"Total languages supported: {len(languages)}\n")
    
    for lang_info in languages:
        model = get_language_model(lang_info['code'])
        intent_count = len(model['intents'])
        print(f"  🌐 {lang_info['name']:15} ({lang_info['code']})")
        print(f"     Intents: {intent_count}, Keywords: {len(model.get('stop_words', []))} stop words")
    
    print("\n\nSwahili Intent Keywords (Example):")
    sw_model = get_language_model('sw')
    for intent, details in list(sw_model['intents'].items())[:3]:
        keywords = details['keywords']
        print(f"  {intent.upper():8} → {', '.join(keywords)}")


def example_4_voice_listener():
    """Example 4: Voice Command Listener with NLU (Interactive)"""
    print_section("Example 4: Voice Command Listener")
    
    print("Initializing voice listener with NLU...")
    listener = VoiceCommandListener(enable_nlu=True, primary_language='sw')
    
    print("\n✓ Voice listener ready!")
    print("\nSupported commands in Swahili:")
    print("  • 'cheza [artist/song]' - Play music")
    print("  • 'simama' - Pause")
    print("  • 'ongeza kasi' / 'pungza sauti' - Volume control")
    print("  • 'tafuta [artist/song]' - Search")
    print("\nSupported commands in English:")
    print("  • 'play [artist/song]' - Play music")
    print("  • 'pause' - Pause")
    print("  • 'volume up/down' - Volume control")
    print("  • 'search [artist/song]' - Search")
    
    print("\n\nTo test voice commands, uncomment the code below:")
    print("# command = listener.voice_play_command()")
    print("# if command:")
    print("#     print(f'Intent: {command.intent}')")
    print("#     print(f'Entities: {command.entities}')")


def example_5_custom_artists():
    """Example 5: Adding Custom Artists and Songs"""
    print_section("Example 5: Custom Artist Management")
    
    recognizer = EntityRecognizer()
    
    # Add a custom artist with Swahili nickname
    print("Adding custom artist: Diamond Platnumz (with Swahili nickname)")
    recognizer.add_artist(
        canonical_name="Diamond Platnumz",
        aliases=["diamond", "dpz", "diamond platnumz"],
        language="sw",
        genres=["afrobeats", "tanzanian"]
    )
    
    # Add a custom song
    print("Adding custom song: 'Levitating' by Dua Lipa")
    recognizer.add_song(
        song_title="Levitating",
        artists=["Dua Lipa"],
        aliases=["levitating", "levitate"]
    )
    
    print("\n✓ Custom entries added to entity database!")
    
    # Test recognition of new artist
    print("\nTesting recognition with new artist...")
    text = "cheza diamond"
    entities = recognizer.extract_entities(text, detected_language='sw')
    
    for entity in entities:
        print(f"  Found: {entity.value} → {entity.normalized_value}")


def example_6_fuzzy_matching():
    """Example 6: Fuzzy Matching for Typos"""
    print_section("Example 6: Fuzzy Matching")
    
    recognizer = EntityRecognizer()
    
    test_cases = [
        ("bakbencher", ["Backbencher", "Sia", "Wizkid"]),
        ("sia", ["Sia", "Wizkid", "Diamond"]),
        ("chez", ["play", "pause", "stop"]),
    ]
    
    print("Fuzzy matching with threshold=0.7:\n")
    
    for query, candidates in test_cases:
        match = recognizer.fuzzy_match(query, candidates, threshold=0.7)
        if match:
            print(f"  '{query}' → '{match}' ✓")
        else:
            print(f"  '{query}' → No match (below threshold)")


def example_7_advanced_parsing():
    """Example 7: Advanced NLU Parsing"""
    print_section("Example 7: Advanced Command Parsing")
    
    engine = NLUEngine()
    
    # Complex Swahili command
    complex_commands = [
        "cheza backbencher na diamond platnumz kwa spotify",
        "ongeza sauti hadi 80 percent",
        "tafuta wimbo mpya za afrbeats",
    ]
    
    print("Parsing complex commands:\n")
    
    for command in complex_commands:
        print(f"Command: '{command}'")
        parsed = engine.parse(command)
        print(f"  Intent: {parsed.intent}")
        print(f"  Language: {parsed.language}")
        print(f"  Confidence: {parsed.confidence:.1%}")
        print(f"  Normalized: '{parsed.normalized_text}'")
        print()


def example_8_language_switching():
    """Example 8: Dynamic Language Switching"""
    print_section("Example 8: Language Switching")
    
    listener = VoiceCommandListener(enable_nlu=True, primary_language='en')
    
    print("Initial setup: English (en)")
    print("  Supported: en, sw, es, pt, fr\n")
    
    # Simulate language switching
    languages = ['en', 'sw', 'es', 'pt']
    
    for lang in languages:
        listener.enable_language(lang)
        model = get_language_model(lang)
        print(f"\n🌐 Switched to: {model['language_name']} ({lang})")
        
        # Show sample commands
        sample_intent = 'play'
        if sample_intent in model['intents']:
            keywords = model['intents'][sample_intent]['keywords']
            example = model['intents'][sample_intent]['examples'][0]
            print(f"   Play keyword: {keywords[0]}")
            print(f"   Example: \"{example}\"")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "NLU SYSTEM - EXAMPLES & TESTS" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝")
    
    examples = [
        ("1", "NLU Engine - Intent Recognition", example_1_nlu_engine),
        ("2", "Entity Recognition", example_2_entity_recognition),
        ("3", "Language Models", example_3_language_models),
        ("4", "Voice Command Listener", example_4_voice_listener),
        ("5", "Custom Artist Management", example_5_custom_artists),
        ("6", "Fuzzy Matching", example_6_fuzzy_matching),
        ("7", "Advanced Parsing", example_7_advanced_parsing),
        ("8", "Language Switching", example_8_language_switching),
    ]
    
    print("\nAvailable examples:")
    for num, title, _ in examples:
        print(f"  {num}. {title}")
    
    print("\nRunning all examples...\n")
    
    for num, title, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n❌ Error in example {num}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
