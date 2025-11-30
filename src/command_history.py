"""
Command History System - replay and suggest recent commands.

Features:
- Store command history with timestamps
- Replay previous commands
- Find similar commands by fuzzy matching
- Command templates/macros
- Quick access to recent patterns
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import deque
import difflib


@dataclass
class CommandRecord:
    """Record of a executed command."""
    timestamp: str
    intent: str
    entities: Dict[str, str]
    success: bool
    execution_time: float
    confidence: float
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class CommandHistory:
    """Manage command history with replay and suggestion capabilities."""
    
    def __init__(self, max_size: int = 100, history_file: Optional[Path] = None):
        """
        Initialize command history.
        
        Args:
            max_size: Maximum number of commands to keep in memory
            history_file: Path to JSON file for persistent storage
        """
        self.max_size = max_size
        self.history_file = history_file or Path('data/command_history.json')
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.history: deque = deque(maxlen=max_size)
        self.templates: Dict[str, Dict] = {}  # Named command templates/macros
        
        self._load_history()
    
    def _load_history(self):
        """Load history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        self.history.append(CommandRecord.from_dict(item))
                print(f"✓ Loaded {len(self.history)} commands from history")
            except Exception as e:
                print(f"⚠️  Could not load history: {e}")
    
    def _save_history(self):
        """Save history to file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([c.to_dict() for c in self.history], f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save history: {e}")
    
    def add(self, intent: str, entities: Dict[str, str], success: bool = True, 
            execution_time: float = 0.0, confidence: float = 1.0) -> CommandRecord:
        """
        Add command to history.
        
        Args:
            intent: Command intent
            entities: Command entities
            success: Whether command succeeded
            execution_time: Time taken to execute
            confidence: Confidence score (0.0-1.0)
            
        Returns:
            The created CommandRecord
        """
        record = CommandRecord(
            timestamp=datetime.now().isoformat(),
            intent=intent,
            entities=entities,
            success=success,
            execution_time=execution_time,
            confidence=confidence,
        )
        
        self.history.append(record)
        self._save_history()
        return record
    
    def get_last(self, n: int = 1) -> List[CommandRecord]:
        """
        Get last N commands from history.
        
        Args:
            n: Number of commands to return
            
        Returns:
            List of most recent commands
        """
        return list(reversed(list(self.history)))[:n]
    
    def replay(self, index: int = -1) -> Optional[CommandRecord]:
        """
        Get a command from history for replay.
        
        Args:
            index: Index in history (-1 = last, -2 = second-to-last, etc.)
            
        Returns:
            CommandRecord or None if index out of bounds
        """
        try:
            if index < 0 and abs(index) <= len(self.history):
                return self.get_last(abs(index))[0]
            elif 0 <= index < len(self.history):
                return list(self.history)[index]
            return None
        except (IndexError, ValueError):
            return None
    
    def find_similar(self, intent: str, top_k: int = 5) -> List[CommandRecord]:
        """
        Find similar commands in history using fuzzy matching.
        
        Args:
            intent: Intent to match
            top_k: Number of similar commands to return
            
        Returns:
            List of similar commands, ordered by similarity
        """
        # Get all commands with same intent first
        same_intent = [c for c in self.history if c.intent == intent]
        
        if same_intent:
            return same_intent[-top_k:]  # Return last N commands of this intent
        
        # If no exact match, use fuzzy matching on intents
        intents = [c.intent for c in self.history]
        matches = difflib.get_close_matches(intent, set(intents), n=top_k, cutoff=0.6)
        
        result = []
        for matched_intent in matches:
            for cmd in reversed(list(self.history)):
                if cmd.intent == matched_intent and cmd not in result:
                    result.append(cmd)
                    if len(result) >= top_k:
                        return result
        
        return result
    
    def suggest_next(self, current_intent: str) -> Optional[CommandRecord]:
        """
        Suggest next command based on patterns.
        
        Example: User usually plays a song, then sets volume.
        
        Args:
            current_intent: Current command intent
            
        Returns:
            Suggested next command or None
        """
        # Look for recent patterns where this intent is followed by another
        for i in range(len(self.history) - 1, 0, -1):
            if self.history[i].intent == current_intent:
                next_cmd = self.history[i + 1]
                # Check if this pattern repeats
                pattern_count = sum(
                    1 for j in range(len(self.history) - 1)
                    if self.history[j].intent == current_intent and 
                    self.history[j + 1].intent == next_cmd.intent
                )
                
                if pattern_count >= 2:  # Pattern must repeat at least twice
                    return next_cmd
        
        return None
    
    def create_template(self, name: str, commands: List[Tuple[str, Dict]]):
        """
        Create a command template/macro for quick replay.
        
        Example:
            history.create_template(
                'setup',
                [('play', {'query': 'backbencher'}), ('volume', {'level': '50'})]
            )
            
            # Later: history.replay_template('setup')
        
        Args:
            name: Template name
            commands: List of (intent, entities) tuples
        """
        self.templates[name.lower()] = {
            'commands': commands,
            'created': datetime.now().isoformat(),
            'uses': 0,
        }
        print(f"✓ Created template '{name}' with {len(commands)} commands")
    
    def replay_template(self, name: str) -> Optional[List[Tuple[str, Dict]]]:
        """
        Replay a command template.
        
        Args:
            name: Template name
            
        Returns:
            List of commands in template or None if not found
        """
        template = self.templates.get(name.lower())
        if template:
            template['uses'] += 1
            return template['commands']
        return None
    
    def list_templates(self) -> List[str]:
        """Get list of available template names."""
        return list(self.templates.keys())
    
    def delete_template(self, name: str) -> bool:
        """
        Delete a template.
        
        Args:
            name: Template name
            
        Returns:
            True if deleted, False if not found
        """
        if name.lower() in self.templates:
            del self.templates[name.lower()]
            print(f"✓ Deleted template '{name}'")
            return True
        return False
    
    def get_frequent_patterns(self, top_k: int = 5) -> List[Tuple[str, int]]:
        """
        Get most frequently executed intent sequences.
        
        Args:
            top_k: Number of patterns to return
            
        Returns:
            List of (intent_sequence, frequency) tuples
        """
        patterns = {}
        
        for i in range(len(self.history) - 1):
            current = self.history[i].intent
            next_intent = self.history[i + 1].intent
            pattern = f"{current} → {next_intent}"
            patterns[pattern] = patterns.get(pattern, 0) + 1
        
        return sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:top_k]
    
    def get_success_streak(self) -> int:
        """
        Get current success streak (consecutive successful commands).
        
        Returns:
            Number of consecutive successful commands
        """
        streak = 0
        for cmd in reversed(list(self.history)):
            if cmd.success:
                streak += 1
            else:
                break
        return streak
    
    def get_stats(self) -> Dict:
        """
        Get statistics about command history.
        
        Returns:
            Dict with various statistics
        """
        if not self.history:
            return {'total': 0}
        
        total = len(self.history)
        successful = sum(1 for c in self.history if c.success)
        failed = total - successful
        
        intents = {}
        for cmd in self.history:
            if cmd.intent not in intents:
                intents[cmd.intent] = {'count': 0, 'success': 0, 'avg_time': 0, 'avg_confidence': 0}
            
            intents[cmd.intent]['count'] += 1
            if cmd.success:
                intents[cmd.intent]['success'] += 1
            intents[cmd.intent]['avg_time'] += cmd.execution_time
            intents[cmd.intent]['avg_confidence'] += cmd.confidence
        
        # Calculate averages
        for intent_stats in intents.values():
            intent_stats['avg_time'] /= intent_stats['count']
            intent_stats['avg_confidence'] /= intent_stats['count']
        
        return {
            'total': total,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / total if total > 0 else 0,
            'by_intent': intents,
            'templates': len(self.templates),
            'recent_commands': [c.to_dict() for c in list(self.history)[-10:]],
        }
    
    def print_history(self, limit: int = 10):
        """
        Print recent command history.
        
        Args:
            limit: Number of recent commands to show
        """
        recent = self.get_last(limit)
        
        print("\n" + "="*70)
        print("📜 Recent Command History")
        print("="*70)
        
        for i, cmd in enumerate(reversed(recent), 1):
            status = "✓" if cmd.success else "✗"
            time_str = datetime.fromisoformat(cmd.timestamp).strftime("%H:%M:%S")
            entities_str = ", ".join(f"{k}={v}" for k, v in cmd.entities.items()) if cmd.entities else "none"
            
            print(f"{i}. [{time_str}] {status} {cmd.intent}")
            print(f"   Entities: {entities_str}")
            print(f"   Confidence: {cmd.confidence:.1%} | Time: {cmd.execution_time:.2f}s")
        
        print("="*70)
    
    def clear_history(self, before: Optional[timedelta] = None):
        """
        Clear old history entries.
        
        Args:
            before: Timedelta - clear entries older than this (default: clear all)
        """
        if before is None:
            self.history.clear()
            self._save_history()
            print("✓ Cleared all command history")
        else:
            cutoff_time = datetime.now() - before
            original_size = len(self.history)
            
            # Create new deque without old entries
            new_history = deque(maxlen=self.max_size)
            for cmd in self.history:
                cmd_time = datetime.fromisoformat(cmd.timestamp)
                if cmd_time > cutoff_time:
                    new_history.append(cmd)
            
            self.history = new_history
            self._save_history()
            
            removed = original_size - len(self.history)
            print(f"✓ Removed {removed} commands older than {before}")
