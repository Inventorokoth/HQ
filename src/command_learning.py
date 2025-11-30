"""
Command Learning System - learns from user corrections to improve NLU.

Features:
- Tracks command corrections (when user corrects a misheard command)
- Analyzes patterns to identify weak intents/entities
- Builds user profiles for personalization
- Suggests improvements based on correction history
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict


@dataclass
class CommandCorrection:
    """Record of a user correction."""
    timestamp: str
    original_intent: str
    original_entities: Dict[str, str]
    corrected_intent: str
    corrected_entities: Dict[str, str]
    reason: str  # user's explanation
    confidence_before: float
    
    def to_dict(self):
        return asdict(self)


class CommandCorrectionsLogger:
    """Track and analyze command corrections for learning."""
    
    def __init__(self, corrections_file: Optional[Path] = None):
        """
        Initialize corrections logger.
        
        Args:
            corrections_file: Path to JSON file storing corrections (default: corrections.json)
        """
        self.corrections_file = corrections_file or Path('data/corrections.json')
        self.corrections_file.parent.mkdir(parents=True, exist_ok=True)
        self.corrections: List[CommandCorrection] = []
        self._load_corrections()
    
    def _load_corrections(self):
        """Load corrections from file."""
        if self.corrections_file.exists():
            try:
                with open(self.corrections_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.corrections = [CommandCorrection(**item) for item in data]
                print(f"✓ Loaded {len(self.corrections)} corrections")
            except Exception as e:
                print(f"⚠️  Could not load corrections: {e}")
                self.corrections = []
    
    def _save_corrections(self):
        """Save corrections to file."""
        try:
            with open(self.corrections_file, 'w', encoding='utf-8') as f:
                json.dump([c.to_dict() for c in self.corrections], f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save corrections: {e}")
    
    def log_correction(
        self,
        original_intent: str,
        original_entities: Dict[str, str],
        corrected_intent: str,
        corrected_entities: Dict[str, str],
        reason: str = "",
        confidence_before: float = 0.0
    ) -> CommandCorrection:
        """
        Log a correction when user corrects a misheard command.
        
        Args:
            original_intent: What the system detected
            original_entities: What entities were extracted
            corrected_intent: What the user actually wanted
            corrected_entities: Correct entities
            reason: Why the system was wrong (optional)
            confidence_before: Confidence of original detection
            
        Returns:
            The logged CommandCorrection
        """
        correction = CommandCorrection(
            timestamp=datetime.now().isoformat(),
            original_intent=original_intent,
            original_entities=original_entities,
            corrected_intent=corrected_intent,
            corrected_entities=corrected_entities,
            reason=reason,
            confidence_before=confidence_before,
        )
        
        self.corrections.append(correction)
        self._save_corrections()
        
        print(f"✓ Logged correction: {original_intent} → {corrected_intent}")
        return correction
    
    def get_statistics(self) -> Dict:
        """
        Analyze correction patterns.
        
        Returns:
            Dict with statistics about corrections
        """
        if not self.corrections:
            return {'total': 0}
        
        stats = {
            'total': len(self.corrections),
            'intent_confusions': defaultdict(Counter),
            'entity_errors': defaultdict(Counter),
            'most_corrected_intents': Counter(),
            'confidence_issues': [],
        }
        
        # Analyze intent confusions
        for correction in self.corrections:
            if correction.original_intent != correction.corrected_intent:
                stats['intent_confusions'][correction.corrected_intent][correction.original_intent] += 1
                stats['most_corrected_intents'][correction.corrected_intent] += 1
            
            # Analyze entity errors
            for key, value in correction.corrected_entities.items():
                if key not in correction.original_entities or correction.original_entities[key] != value:
                    stats['entity_errors'][key][correction.original_entities.get(key, 'MISSING')] += 1
            
            # Track low confidence corrections
            if correction.confidence_before < 0.7:
                stats['confidence_issues'].append({
                    'timestamp': correction.timestamp,
                    'intent': correction.corrected_intent,
                    'confidence': correction.confidence_before,
                })
        
        return stats
    
    def print_report(self):
        """Print analysis report of corrections."""
        stats = self.get_statistics()
        
        if stats['total'] == 0:
            print("📊 No corrections yet - system is learning!")
            return
        
        print("\n" + "="*60)
        print("📊 Command Corrections Report")
        print("="*60)
        print(f"Total corrections: {stats['total']}")
        
        if stats['most_corrected_intents']:
            print("\n🔴 Most Frequently Corrected Intents:")
            for intent, count in stats['most_corrected_intents'].most_common(5):
                print(f"   • {intent}: {count} corrections")
        
        if stats['intent_confusions']:
            print("\n🔀 Intent Confusions (what gets mixed up):")
            for correct_intent, confusions in stats['intent_confusions'].items():
                if confusions:
                    print(f"   {correct_intent} was mistaken as:")
                    for wrong_intent, count in confusions.most_common(3):
                        print(f"      → {wrong_intent}: {count} times")
        
        if stats['entity_errors']:
            print("\n❌ Entity Extraction Errors:")
            for entity_type, errors in stats['entity_errors'].items():
                if errors:
                    print(f"   {entity_type}:")
                    for wrong_value, count in errors.most_common(3):
                        print(f"      ✗ {wrong_value}: {count} times")
        
        if stats['confidence_issues']:
            low_conf = [c for c in stats['confidence_issues'] if c['confidence'] < 0.6]
            if low_conf:
                print(f"\n⚠️  Low Confidence Issues: {len(low_conf)} corrections with confidence < 60%")
                print("   Consider retraining NLU model or adjusting thresholds")
        
        print("="*60)
    
    def suggest_improvements(self) -> List[str]:
        """
        Suggest improvements based on correction patterns.
        
        Returns:
            List of improvement suggestions
        """
        stats = self.get_statistics()
        suggestions = []
        
        if stats['total'] < 5:
            return ["Keep collecting corrections for better suggestions"]
        
        # Suggest for frequently corrected intents
        for intent, count in stats['most_corrected_intents'].most_common(3):
            if count > 2:
                suggestions.append(
                    f"🎯 '{intent}' intent is frequently corrected ({count} times). "
                    f"Consider adding more training examples or keywords."
                )
        
        # Suggest for confidence issues
        low_conf_count = sum(1 for c in stats.get('confidence_issues', []) if c['confidence'] < 0.6)
        if low_conf_count > 2:
            suggestions.append(
                f"⚠️  {low_conf_count} corrections had low confidence. "
                f"Lower the confidence threshold or retrain the NLU model."
            )
        
        # Suggest for entity errors
        if stats['entity_errors']:
            total_entity_errors = sum(sum(errors.values()) for errors in stats['entity_errors'].values())
            if total_entity_errors > 3:
                suggestions.append(
                    f"🏷️  {total_entity_errors} entity extraction errors detected. "
                    f"Consider expanding the entity recognition database."
                )
        
        return suggestions if suggestions else ["System is performing well! ✨"]
    
    def export_corrections(self, output_file: Path):
        """Export corrections to a file for analysis."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([c.to_dict() for c in self.corrections], f, indent=2)
        print(f"✓ Exported {len(self.corrections)} corrections to {output_file}")
    
    def clear_old_corrections(self, days: int = 30):
        """
        Clear corrections older than specified days (for privacy/storage).
        
        Args:
            days: Keep only corrections from last N days
        """
        cutoff = datetime.now().timestamp() - (days * 86400)
        original_count = len(self.corrections)
        
        self.corrections = [
            c for c in self.corrections
            if datetime.fromisoformat(c.timestamp).timestamp() > cutoff
        ]
        
        removed = original_count - len(self.corrections)
        if removed > 0:
            self._save_corrections()
            print(f"✓ Removed {removed} corrections older than {days} days")


class CommandAnalytics:
    """Track command execution analytics for performance monitoring."""
    
    def __init__(self, analytics_file: Optional[Path] = None):
        """
        Initialize command analytics.
        
        Args:
            analytics_file: Path to JSON file storing analytics (default: analytics.json)
        """
        self.analytics_file = analytics_file or Path('data/analytics.json')
        self.analytics_file.parent.mkdir(parents=True, exist_ok=True)
        self.stats = defaultdict(lambda: {'success': 0, 'failed': 0, 'times': []})
        self._load_stats()
    
    def _load_stats(self):
        """Load stats from file."""
        if self.analytics_file.exists():
            try:
                with open(self.analytics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for intent, values in data.items():
                        self.stats[intent] = values
            except Exception as e:
                print(f"⚠️  Could not load analytics: {e}")
    
    def _save_stats(self):
        """Save stats to file."""
        try:
            with open(self.analytics_file, 'w', encoding='utf-8') as f:
                json.dump(dict(self.stats), f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save analytics: {e}")
    
    def record_command(self, intent: str, success: bool, elapsed_time: float = 0.0):
        """
        Record a command execution.
        
        Args:
            intent: Command intent (play, pause, volume, etc.)
            success: Whether command succeeded
            elapsed_time: Time taken to execute (seconds)
        """
        stats = self.stats[intent]
        if success:
            stats['success'] += 1
        else:
            stats['failed'] += 1
        stats['times'].append(elapsed_time)
        
        # Keep only last 1000 times to avoid bloat
        if len(stats['times']) > 1000:
            stats['times'] = stats['times'][-1000:]
        
        self._save_stats()
    
    def get_success_rate(self, intent: Optional[str] = None) -> float:
        """
        Get success rate for intent or overall.
        
        Args:
            intent: Specific intent or None for overall
            
        Returns:
            Success rate 0.0 to 1.0
        """
        if intent:
            stats = self.stats[intent]
        else:
            # Overall stats
            total_success = sum(s['success'] for s in self.stats.values())
            total_failed = sum(s['failed'] for s in self.stats.values())
            total = total_success + total_failed
            return total_success / total if total > 0 else 0.0
        
        total = stats['success'] + stats['failed']
        return stats['success'] / total if total > 0 else 0.0
    
    def print_report(self):
        """Print analytics report."""
        print("\n" + "="*60)
        print("📊 Command Analytics Report")
        print("="*60)
        
        if not self.stats:
            print("No command history yet")
            return
        
        # Calculate totals
        total_success = sum(s['success'] for s in self.stats.values())
        total_failed = sum(s['failed'] for s in self.stats.values())
        total_commands = total_success + total_failed
        overall_rate = total_success / total_commands * 100 if total_commands > 0 else 0
        
        print(f"Total Commands: {total_commands}")
        print(f"Overall Success Rate: {overall_rate:.1f}%")
        
        print("\nPer-Intent Breakdown:")
        for intent, stats in sorted(self.stats.items()):
            total = stats['success'] + stats['failed']
            rate = stats['success'] / total * 100 if total > 0 else 0
            avg_time = sum(stats['times']) / len(stats['times']) if stats['times'] else 0
            
            print(f"  {intent}:")
            print(f"    ✓ {stats['success']}/{total} ({rate:.1f}%)")
            print(f"    ⏱️  {avg_time:.2f}s avg")
        
        print("="*60)
