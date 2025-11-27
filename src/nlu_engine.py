"""
Natural Language Understanding (NLU) Engine for voice commands.

Supports:
- Intent extraction (play, pause, resume, stop, volume, search, status)
- Entity extraction (song names, artists, local language variants)
- Multi-language support (English + local languages)
- Fuzzy matching for artist nicknames and colloquial terms
- Configurable intent/entity mappings
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class ParsedCommand:
    """Result of NLU parsing."""
    intent: str  # play, pause, resume, stop, volume, search, status, help, exit
    entities: Dict[str, str]  # entity_type -> value (e.g., {'song': 'cheap thrills', 'artist': 'sia'})
    confidence: float  # 0.0 to 1.0
    original_text: str
    normalized_text: str  # Cleaned and normalized text
    language: str  # detected language
    
    def to_dict(self) -> dict:
        """Convert to dictionary for logging/debugging."""
        return {
            'intent': self.intent,
            'entities': self.entities,
            'confidence': self.confidence,
            'original_text': self.original_text,
            'normalized_text': self.normalized_text,
            'language': self.language,
        }


class NLUEngine:
    """Natural Language Understanding engine for voice commands."""
    
    def __init__(self, custom_intents_file: Optional[Path] = None):
        """
        Initialize NLU engine.
        
        Args:
            custom_intents_file: Path to JSON file with custom intent/entity mappings
        """
        # Core intents
        self.core_intents = {
            'play': ['play', 'cheza', 'ucheze', 'cheze'],  # English + Swahili variants
            'pause': ['pause', 'simama', 'stop it'],
            'resume': ['resume', 'endelea', 'continue'],
            'stop': ['stop', 'hankisha'],
            'volume': ['volume', 'volume up', 'volume down', 'louder', 'quieter'],
            'search': ['search', 'find', 'look for', 'tafuta'],
            'status': ['status', 'what\'s playing', 'current', 'what song'],
            'help': ['help', 'commands', 'what can i do'],
            'exit': ['exit', 'quit', 'goodbye', 'bye'],
        }
        
        # Load custom intents if provided
        self.custom_intents = {}
        if custom_intents_file and custom_intents_file.exists():
            with open(custom_intents_file, 'r', encoding='utf-8') as f:
                self.custom_intents = json.load(f)
        
        # Language detection patterns
        self.language_patterns = {
            'en': r'[\x00-\x7F]+',  # ASCII
            'sw': r'[a-zäöüß]+',  # Swahili characters
        }
        
        # Entity extraction patterns
        self.entity_patterns = {
            'artist_mention': r'by\s+(\w+)|(\w+)\s+song',
            'volume_level': r'(\d{1,3})\s*%?',
            'seek_position': r'(\d{1,3})\s*%?|(\d{1,2}):(\d{2})',
        }
    
    def parse(self, text: str) -> ParsedCommand:
        """
        Parse voice command using NLU.
        
        Args:
            text: Raw voice input text
            
        Returns:
            ParsedCommand with intent, entities, and confidence
        """
        if not text or not text.strip():
            return ParsedCommand(
                intent='unknown',
                entities={},
                confidence=0.0,
                original_text=text,
                normalized_text='',
                language='unknown',
            )
        
        # Normalize text
        normalized = self._normalize_text(text)
        detected_lang = self._detect_language(text)
        
        # Extract intent
        intent, intent_confidence = self._extract_intent(normalized)
        
        # Extract entities
        entities = self._extract_entities(normalized, intent)
        
        # Overall confidence
        overall_confidence = intent_confidence
        
        return ParsedCommand(
            intent=intent,
            entities=entities,
            confidence=overall_confidence,
            original_text=text,
            normalized_text=normalized,
            language=detected_lang,
        )
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for processing."""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation except apostrophes
        text = re.sub(r"[^\w\s']", '', text)
        
        return text
    
    def _detect_language(self, text: str) -> str:
        """
        Detect language in text.
        
        Simple detection based on character patterns and keywords.
        """
        text_lower = text.lower()
        
        # Swahili keywords
        swahili_keywords = {'cheza', 'simama', 'endelea', 'tafuta', 'hankisha', 'ucheze'}
        
        # Check for Swahili keywords
        if any(keyword in text_lower for keyword in swahili_keywords):
            return 'sw'
        
        # Check for English keywords
        if any(word in text_lower for word in ['play', 'pause', 'stop', 'volume', 'search']):
            return 'en'
        
        # Default to English
        return 'en'
    
    def _extract_intent(self, text: str) -> Tuple[str, float]:
        """
        Extract intent from normalized text.
        
        Returns:
            (intent, confidence_score)
        """
        best_intent = 'unknown'
        best_score = 0.0
        
        # Combine core and custom intents
        all_intents = {**self.core_intents, **self.custom_intents}
        
        for intent, keywords in all_intents.items():
            for keyword in keywords:
                # Exact match gets highest score
                if keyword in text:
                    score = 1.0
                    if score > best_score:
                        best_score = score
                        best_intent = intent
                    break
                
                # Fuzzy match (if keyword is contained or starts with keyword)
                if text.startswith(keyword[:3]):  # At least 3 chars
                    score = 0.7
                    if score > best_score:
                        best_score = score
                        best_intent = intent
        
        return best_intent, best_score
    
    def _extract_entities(self, text: str, intent: str) -> Dict[str, str]:
        """
        Extract entities from text based on intent.
        
        Args:
            text: Normalized text
            intent: Detected intent
            
        Returns:
            Dictionary of entity_type -> value
        """
        entities = {}
        
        if intent == 'play':
            # Extract song/artist name (everything after "play" keyword)
            match = re.search(r'(?:play|cheza|ucheze|cheze)\s+(.+)', text)
            if match:
                query = match.group(1).strip()
                # Try to split into artist and song
                if ' by ' in query:
                    parts = query.split(' by ')
                    entities['song'] = parts[0].strip()
                    entities['artist'] = parts[1].strip()
                elif ' - ' in query:
                    parts = query.split(' - ')
                    entities['artist'] = parts[0].strip()
                    entities['song'] = parts[1].strip()
                else:
                    # Treat as combined query
                    entities['query'] = query
        
        elif intent == 'volume':
            # Extract volume level
            match = re.search(r'(\d{1,3})\s*%?', text)
            if match:
                entities['level'] = match.group(1)
            
            # Check for volume direction
            if 'up' in text or 'louder' in text:
                entities['direction'] = 'up'
            elif 'down' in text or 'quieter' in text:
                entities['direction'] = 'down'
        
        elif intent == 'seek':
            # Extract position (time or percentage)
            time_match = re.search(r'(\d{1,2}):(\d{2})', text)
            if time_match:
                entities['position'] = f"{time_match.group(1)}:{time_match.group(2)}"
            else:
                pct_match = re.search(r'(\d{1,3})\s*%', text)
                if pct_match:
                    entities['position_percent'] = pct_match.group(1)
        
        return entities
    
    def add_custom_intent(self, intent: str, keywords: List[str], language: str = 'sw') -> None:
        """
        Add custom intent for local language support.
        
        Example:
            engine.add_custom_intent('play', ['cheza', 'ucheze'], 'sw')  # Swahili
            engine.add_custom_intent('play', ['toca', 'toco'], 'pt')     # Portuguese
        
        Args:
            intent: Intent name (play, pause, etc.)
            keywords: List of keyword variants in local language
            language: Language code (sw, pt, es, etc.)
        """
        if intent not in self.custom_intents:
            self.custom_intents[intent] = []
        
        # Add to custom intents
        self.custom_intents[intent].extend(keywords)
        
        # Also add to core intents for faster matching
        if intent in self.core_intents:
            self.core_intents[intent].extend(keywords)
        else:
            self.core_intents[intent] = keywords
        
        print(f"✓ Added {language} keywords for '{intent}': {keywords}")
    
    def add_artist_alias(self, artist_name: str, aliases: List[str]) -> None:
        """
        Add artist aliases for better recognition.
        
        Example:
            engine.add_artist_alias('backbencher', ['backbencher', 'bb', 'backbenchers'])
        
        Args:
            artist_name: Canonical artist name
            aliases: List of aliases or nicknames
        """
        # This would be used in entity matching
        if not hasattr(self, 'artist_aliases'):
            self.artist_aliases = {}
        
        self.artist_aliases[artist_name] = aliases
        print(f"✓ Added aliases for '{artist_name}': {aliases}")
    
    def resolve_entity(self, entity_value: str, entity_type: str = 'artist') -> str:
        """
        Resolve entity aliases to canonical names.
        
        Example:
            "bb" -> "Backbencher"
            "toxic" -> "Toxic" (song by Backbencher)
        
        Args:
            entity_value: Entity value to resolve
            entity_type: Type of entity (artist, song, etc.)
            
        Returns:
            Canonical entity value or original if not found
        """
        if not hasattr(self, 'artist_aliases'):
            return entity_value
        
        # Reverse lookup in aliases
        for canonical, aliases in self.artist_aliases.items():
            if entity_value.lower() in [alias.lower() for alias in aliases]:
                return canonical
        
        return entity_value


# Preset configurations for common languages

SWAHILI_INTENTS = {
    'play': ['cheza', 'ucheze', 'cheze', 'imba'],
    'pause': ['simama', 'sakinisha'],
    'resume': ['endelea', 'anza'],
    'stop': ['hankisha', 'acha'],
    'volume': ['kasi', 'sauti'],
    'search': ['tafuta', 'sagilia'],
    'status': ['hali', 'ingine'],
}

SPANISH_INTENTS = {
    'play': ['toca', 'toco', 'reproduc'],
    'pause': ['pausa', 'detén'],
    'resume': ['continúa', 'reanuda'],
    'stop': ['para', 'detén'],
    'volume': ['volumen', 'sonido'],
    'search': ['busca', 'encuentra'],
    'status': ['estado', 'actual'],
}

FRENCH_INTENTS = {
    'play': ['joue', 'lance', 'lis'],
    'pause': ['pause', 'arrête'],
    'resume': ['continue', 'reprend'],
    'stop': ['arrête', 'stoppe'],
    'volume': ['volume', 'son'],
    'search': ['cherche', 'trouve'],
    'status': ['statut', 'actuel'],
}

PORTUGUESE_INTENTS = {
    'play': ['toca', 'reproduz', 'toco'],
    'pause': ['pausa', 'parou'],
    'resume': ['continua', 'volta'],
    'stop': ['para', 'pára'],
    'volume': ['volume', 'som'],
    'search': ['busca', 'procura'],
    'status': ['estado', 'atual'],
}
