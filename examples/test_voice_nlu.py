#!/usr/bin/env python3
"""
Test Voice + NLU System Without Microphone

This script lets you test the NLU system by typing commands instead of speaking.
Perfect for testing Swahili commands and debugging the voice parsing pipeline.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.voice_input import VoiceCommandListener


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_examples():
    """Print command examples."""
    print_section("📚 EXAMPLE COMMANDS TO TEST")
    
    print("SWAHILI Commands:")
    print("  cheza backbencher ya toxic          → Play Backbencher - Toxic")
    print("  cheza bb ya toxic                   → Play (nickname recognition)")
    print("  simama                              → Pause")
    print("  endelea                             → Resume")
    print("  ongeza kasi                         → Volume")
    print("  tafuta afrobeats                    → Search")
    print()
    
    print("ENGLISH Commands:")
    print("  play sia cheap thrills              → Play Sia - Cheap Thrills")
    print("  play sia                            → Play Sia (artist only)")
    print("  pause                               → Pause")
    print("  volume up                           → Volume up")
    print("  search wizkid                       → Search Wizkid")
    print()
    
    print("MIXED Commands:")
    print("  cheza sia                           → Play Sia (Swahili + English artist)")
    print("  play backbencher                    → Play Backbencher (English + Swahili artist)")
    print()


def test_swahili_commands():
    """Test Swahili-specific commands."""
    print_section("🇹🇿 TESTING SWAHILI COMMANDS")
    
    listener = VoiceCommandListener(enable_nlu=True, primary_language='sw')
    
    test_commands = [
        "cheza backbencher ya toxic",
        "cheza bb ya toxic",
        "simama",
        "endelea",
        "ongeza kasi",
        "tafuta afrobeats",
    ]
    
    for cmd in test_commands:
        result = listener.test_command(cmd)
        print()


def test_english_commands():
    """Test English commands."""
    print_section("🇬🇧 TESTING ENGLISH COMMANDS")
    
    listener = VoiceCommandListener(enable_nlu=True, primary_language='en')
    
    test_commands = [
        "play sia cheap thrills",
        "play sia",
        "pause",
        "volume up",
        "search wizkid",
    ]
    
    for cmd in test_commands:
        result = listener.test_command(cmd)
        print()


def interactive_test():
    """Interactive test mode."""
    print_section("🎤 INTERACTIVE TEST MODE")
    print("Enter voice commands (or 'quit' to exit, 'help' for examples)\n")
    
    listener = VoiceCommandListener(enable_nlu=True, primary_language='sw')
    
    while True:
        try:
            user_input = input("🎙️  Enter command: ").strip()
            
            if user_input.lower() == 'quit':
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print_examples()
                continue
            
            if user_input.lower() == 'en':
                listener.primary_language = 'en'
                print("✓ Switched to English mode\n")
                continue
            
            if user_input.lower() == 'sw':
                listener.primary_language = 'sw'
                print("✓ Switched to Swahili mode\n")
                continue
            
            if not user_input:
                continue
            
            # Test the command
            result = listener.test_command(user_input)
            
            if result:
                print(f"\n✅ Would execute: {result.intent}")
                if result.entities:
                    print(f"   With params: {result.entities}")
            else:
                print("\n❌ Could not parse command")
            
            print()
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue


def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("  🎙️  VOICE + NLU TEST SYSTEM")
    print("="*70)
    print("\nThis tool lets you test the NLU system without a microphone.")
    print("Perfect for testing Swahili commands and debugging!\n")
    
    print_examples()
    
    print("\nTesting Mode Options:")
    print("  1. Test Swahili commands")
    print("  2. Test English commands")
    print("  3. Interactive mode")
    print("  4. Exit")
    print()
    
    while True:
        choice = input("Choose an option (1-4): ").strip()
        
        if choice == '1':
            test_swahili_commands()
        elif choice == '2':
            test_english_commands()
        elif choice == '3':
            interactive_test()
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid option\n")


if __name__ == '__main__':
    main()
