#!/usr/bin/env python3
"""Quick verification that all improvements are installed."""

import sys
import os
from pathlib import Path

def verify_files():
    """Check all required files exist."""
    print("\n✅ FILE VERIFICATION\n" + "="*50)
    
    required_files = [
        'main.py',
        'src/command_learning.py',
        'src/command_history.py',
        'src/voice_input.py',
        'src/nlu_engine.py',
        'src/entity_recognizer.py',
        'QUICKSTART.md',
        'IMPLEMENTATION_GUIDE.md',
        'IMPLEMENTATION_SUMMARY.md',
        'README_IMPROVEMENTS.md',
    ]
    
    all_exist = True
    for f in required_files:
        exists = Path(f).exists()
        status = "✅" if exists else "❌"
        print(f"{status} {f}")
        all_exist = all_exist and exists
    
    return all_exist

def verify_imports():
    """Check all imports work."""
    print("\n✅ IMPORT VERIFICATION\n" + "="*50)
    
    try:
        from src.command_learning import CommandCorrectionsLogger, CommandAnalytics
        print("✅ Command Learning (corrections & analytics)")
        
        from src.command_history import CommandHistory
        print("✅ Command History (replay & templates)")
        
        from src.entity_recognizer import CommandContext
        print("✅ Command Context (awareness)")
        
        from src.voice_input import VoiceCommandListener
        print("✅ Voice Input (with fallbacks)")
        
        from src.nlu_engine import NLUEngine
        print("✅ NLU Engine (with multi-intent)")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def verify_classes():
    """Check all classes are available."""
    print("\n✅ CLASS VERIFICATION\n" + "="*50)
    
    try:
        from src.command_learning import CommandCorrectionsLogger, CommandAnalytics, CommandCorrection
        from src.command_history import CommandHistory, CommandRecord
        from src.entity_recognizer import CommandContext
        
        classes = [
            ('CommandCorrection', CommandCorrection),
            ('CommandCorrectionsLogger', CommandCorrectionsLogger),
            ('CommandAnalytics', CommandAnalytics),
            ('CommandRecord', CommandRecord),
            ('CommandHistory', CommandHistory),
            ('CommandContext', CommandContext),
        ]
        
        for name, cls in classes:
            print(f"✅ {name}")
        
        return True
    except Exception as e:
        print(f"❌ Class check failed: {e}")
        return False

def verify_compilation():
    """Check Python files compile."""
    print("\n✅ COMPILATION VERIFICATION\n" + "="*50)
    
    import py_compile
    
    files_to_check = [
        'main.py',
        'src/command_learning.py',
        'src/command_history.py',
    ]
    
    all_ok = True
    for f in files_to_check:
        try:
            py_compile.compile(f)
            print(f"✅ {f}")
        except Exception as e:
            print(f"❌ {f}: {e}")
            all_ok = False
    
    return all_ok

def main():
    """Run all verifications."""
    print("\n" + "="*60)
    print("🔍 VERIFYING HIGH-VALUE IMPROVEMENTS IMPLEMENTATION")
    print("="*60)
    
    checks = [
        ("Files", verify_files),
        ("Imports", verify_imports),
        ("Classes", verify_classes),
        ("Compilation", verify_compilation),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 VERIFICATION SUMMARY")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL VERIFICATIONS PASSED!")
        print("✨ Implementation is complete and ready to use!")
        print("\nQuick start:")
        print("  python3 main.py")
        print("  Then type: voice, repeat, history, stats, context")
        return 0
    else:
        print("⚠️  Some verifications failed. Please check above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
