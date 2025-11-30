"""
Entity Recognizer for extracting songs, artists, and context from commands.

Handles:
- Artist name extraction with alias/nickname support
- Song title extraction
- Context phrases (e.g., "ya" in Swahili = "from/by")
- Fuzzy matching for misspellings
- Language-specific patterns
- Contextual entity disambiguation
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import deque


@dataclass
class Entity:
    """Represents an extracted entity."""
    type: str  # artist, song, album, playlist, etc.
    value: str  # extracted value
    confidence: float  # 0.0 to 1.0
    normalized_value: str  # canonical form
    language: str  # language in which it was detected
    position: Tuple[int, int]  # start, end position in original text


class EntityRecognizer:
    """Recognizes and extracts entities from voice commands."""
    
    def __init__(self):
        """Initialize entity recognizer with language-specific patterns."""
        
        # Context indicators for different languages
        self.context_indicators = {
            'by_artist': {
                'en': ['by', 'from', 'artist'],
                'sw': ['na', 'ya'],  # Swahili: "na" = with, "ya" = of/from
                'es': ['de', 'por'],
                'pt': ['de', 'por'],
                'fr': ['de', 'par'],
            },
            'from_album': {
                'en': ['from', 'in', 'album'],
                'sw': ['kutoka', 'kwenye'],
                'es': ['de', 'del'],
                'pt': ['de', 'do'],
                'fr': ['de', 'du'],
            },
            'in_playlist': {
                'en': ['in', 'from', 'playlist'],
                'sw': ['katika'],
                'es': ['en', 'de'],
                'pt': ['em', 'de'],
                'fr': ['dans', 'de'],
            },
        }
        
        # Artist aliases/nicknames database
        self.artist_database = {
            'backbencher': {
                'canonical': 'Backbencher',
                'aliases': ['backbencher', 'bb', 'back bencher', 'backbenchers'],
                'language': 'sw',  # Primary language
                'genres': ['afrobeats', 'hiphop', 'east_african'],
            },
            'toxic': {
                'canonical': 'Toxic',
                'aliases': ['toxic', 'toxik', 'toxics'],
                'is_song': True,
                'artists': ['backbencher'],
            },
            'diamond': {
                'canonical': 'Diamond Platnumz',
                'aliases': ['diamond', 'diamond platnumz', 'diamond platinumz', 'dpz'],
                'language': 'sw',
                'genres': ['afrobeats', 'tanzanian'],
            },
            'wizkid': {
                'canonical': 'Wizkid',
                'aliases': ['wizkid', 'wiz', 'ayo balogun'],
                'language': 'sw',
                'genres': ['afrobeats', 'nigerian'],
            },
            'sia': {
                'canonical': 'Sia',
                'aliases': ['sia', 'sia furler'],
                'language': 'en',
                'genres': ['pop', 'electropop'],
            },
        }
        
        # Common phrases that shouldn't be entities
        self.stop_words = {
            'en': {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'for', 'of'},
            'sw': {'na', 'ni', 'kwa', 'ya', 'wa', 'ama'},
        }
    
    def extract_entities(
        self,
        text: str,
        detected_language: str = 'en',
        include_confidence: bool = True
    ) -> List[Entity]:
        """
        Extract all entities from text.
        
        Args:
            text: Input text to extract entities from
            detected_language: Language code (en, sw, es, etc.)
            include_confidence: Whether to compute confidence scores
            
        Returns:
            List of extracted entities
        """
        entities = []
        text_lower = text.lower()
        
        # Extract artist names
        artist_entities = self._extract_artists(text_lower, detected_language)
        entities.extend(artist_entities)
        
        # Extract song titles
        song_entities = self._extract_songs(text_lower, detected_language, artist_entities)
        entities.extend(song_entities)
        
        # Extract albums/playlists
        album_entities = self._extract_albums(text_lower, detected_language)
        entities.extend(album_entities)
        
        return entities
    
    def _extract_artists(self, text: str, language: str) -> List[Entity]:
        """Extract artist names from text."""
        artists = []
        
        # Check against artist database
        for canonical_name, info in self.artist_database.items():
            if info.get('is_song'):  # Skip if it's marked as a song
                continue
            
            aliases = info.get('aliases', [canonical_name])
            
            for alias in aliases:
                pattern = r'\b' + re.escape(alias) + r'\b'
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                
                for match in matches:
                    confidence = self._calculate_confidence(
                        alias,
                        text[match.start():match.end()],
                        language,
                        info.get('language', language)
                    )
                    
                    artists.append(Entity(
                        type='artist',
                        value=match.group(),
                        confidence=confidence,
                        normalized_value=canonical_name,
                        language=info.get('language', language),
                        position=(match.start(), match.end()),
                    ))
        
        # Remove duplicates, keep highest confidence
        seen = {}
        for entity in artists:
            key = entity.normalized_value.lower()
            if key not in seen or entity.confidence > seen[key].confidence:
                seen[key] = entity
        
        return list(seen.values())
    
    def _extract_songs(
        self,
        text: str,
        language: str,
        artist_entities: List[Entity]
    ) -> List[Entity]:
        """Extract song titles from text."""
        songs = []
        
        # Look for songs by known artists
        for canonical_name, info in self.artist_database.items():
            if not info.get('is_song'):
                continue
            
            aliases = info.get('aliases', [canonical_name])
            
            for alias in aliases:
                pattern = r'\b' + re.escape(alias) + r'\b'
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                
                for match in matches:
                    # Check if there's an artist context
                    related_artist = None
                    for artist in info.get('artists', []):
                        if artist.lower() in text:
                            related_artist = artist
                            break
                    
                    confidence = self._calculate_confidence(
                        alias,
                        text[match.start():match.end()],
                        language
                    )
                    
                    songs.append(Entity(
                        type='song',
                        value=match.group(),
                        confidence=confidence,
                        normalized_value=info.get('canonical', canonical_name),
                        language=language,
                        position=(match.start(), match.end()),
                    ))
        
        return songs
    
    def _extract_albums(self, text: str, language: str) -> List[Entity]:
        """Extract album names from text."""
        # This could be extended to support album database
        albums = []
        
        # Pattern: "from album [name]" or "del album [name]"
        album_patterns = {
            'en': r'(?:from|in|album)\s+([\'"]?)([a-z\s]+)\1',
            'sw': r'(?:kwenye|katika)\s+([\'"]?)([a-z\s]+)\1',
            'es': r'(?:del|de)\s+(?:album|álbum)\s+([\'"]?)([a-z\s]+)\1',
        }
        
        pattern = album_patterns.get(language, album_patterns['en'])
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        
        for match in matches:
            album_name = match.group(2) if match.lastindex >= 2 else match.group(1)
            albums.append(Entity(
                type='album',
                value=album_name,
                confidence=0.7,
                normalized_value=album_name.title(),
                language=language,
                position=(match.start(), match.end()),
            ))
        
        return albums
    
    def _calculate_confidence(
        self,
        pattern: str,
        found_text: str,
        detected_language: str,
        entity_language: str = None
    ) -> float:
        """
        Calculate confidence for entity extraction.
        
        Args:
            pattern: The pattern we searched for
            found_text: The text that was found
            detected_language: Detected language
            entity_language: Native language of the entity
            
        Returns:
            Confidence score 0.0 to 1.0
        """
        confidence = 0.5  # Base confidence
        
        # Exact match gets higher confidence
        if pattern.lower() == found_text.lower():
            confidence = 0.95
        else:
            # Fuzzy match
            matches = sum(1 for a, b in zip(pattern.lower(), found_text.lower()) if a == b)
            similarity = matches / max(len(pattern), len(found_text))
            confidence = 0.5 + (similarity * 0.45)
        
        # If entity language matches detected language, boost confidence
        if entity_language and entity_language == detected_language:
            confidence = min(1.0, confidence + 0.05)
        
        return confidence
    
    def resolve_entity_context(
        self,
        text: str,
        entity: Entity,
        language: str = 'en'
    ) -> Dict[str, str]:
        """
        Resolve entity context by looking at surrounding text.
        
        Example:
            "cheza backbencher ya toxic" 
            -> entity "toxic" with context {'artist': 'Backbencher', 'type': 'song'}
        
        Args:
            text: Full input text
            entity: Entity to resolve context for
            language: Detected language
            
        Returns:
            Dictionary of context information
        """
        context = {'type': entity.type}
        
        # Look before entity
        before_text = text[:entity.position[0]].strip()
        
        # Check for artist indicators
        by_patterns = self.context_indicators['by_artist'].get(language, [])
        for pattern in by_patterns:
            if pattern in before_text:
                # Extract artist name before the pattern
                artist_part = before_text.split(pattern)[-1].strip()
                if artist_part:
                    context['artist'] = artist_part
        
        return context
    
    def add_artist(
        self,
        canonical_name: str,
        aliases: List[str],
        language: str = 'en',
        genres: Optional[List[str]] = None
    ) -> None:
        """
        Add artist to database.
        
        Example:
            recognizer.add_artist(
                'Backbencher',
                ['backbencher', 'bb'],
                language='sw',
                genres=['afrobeats', 'hiphop']
            )
        
        Args:
            canonical_name: Canonical/official artist name
            aliases: List of aliases/nicknames
            language: Primary language
            genres: Associated genres
        """
        self.artist_database[canonical_name.lower()] = {
            'canonical': canonical_name,
            'aliases': aliases,
            'language': language,
            'genres': genres or [],
        }
        print(f"✓ Added artist: {canonical_name} ({language})")
        print(f"  Aliases: {', '.join(aliases)}")
    
    def add_song(
        self,
        song_title: str,
        artists: List[str],
        aliases: Optional[List[str]] = None
    ) -> None:
        """
        Add song to database.
        
        Example:
            recognizer.add_song(
                'Toxic',
                ['Backbencher'],
                aliases=['toxic', 'toxik']
            )
        
        Args:
            song_title: Official song title
            artists: List of artists credited
            aliases: Alternative titles/spellings
        """
        key = song_title.lower()
        self.artist_database[key] = {
            'canonical': song_title,
            'aliases': aliases or [song_title.lower()],
            'is_song': True,
            'artists': artists,
        }
        print(f"✓ Added song: {song_title} by {', '.join(artists)}")
    
    def fuzzy_match(
        self,
        query: str,
        candidates: List[str],
        threshold: float = 0.7
    ) -> Optional[str]:
        """
        Fuzzy match query against candidates.
        
        Args:
            query: Text to match
            candidates: List of candidate matches
            threshold: Minimum similarity score (0.0-1.0)
            
        Returns:
            Best matching candidate or None
        """
        best_match = None
        best_score = 0.0
        
        query_lower = query.lower()
        
        for candidate in candidates:
            candidate_lower = candidate.lower()
            
            # Exact match
            if query_lower == candidate_lower:
                return candidate
            
            # Calculate Levenshtein-like similarity
            score = self._similarity_score(query_lower, candidate_lower)
            
            if score > best_score:
                best_score = score
                best_match = candidate
        
        if best_score >= threshold:
            return best_match
        
        return None
    
    def _similarity_score(self, s1: str, s2: str) -> float:
        """Calculate similarity score between two strings (0.0-1.0)."""
        if not s1 or not s2:
            return 0.0
        
        # Common prefix
        common = 0
        for a, b in zip(s1, s2):
            if a == b:
                common += 1
            else:
                break
        
        # Length-based similarity
        max_len = max(len(s1), len(s2))
        length_sim = (max_len - abs(len(s1) - len(s2))) / max_len
        
        # Character matching
        matches = sum(1 for a in s1 if a in s2)
        char_sim = matches / max_len
        
        # Combined score
        return (common / max_len) * 0.3 + length_sim * 0.3 + char_sim * 0.4


class CommandContext:
    """
    Track command context for disambiguating entities.
    
    Examples:
        If user recently played 'Backbencher', and now says "play toxic",
        we can infer it's "Toxic by Backbencher" from context.
    """
    
    def __init__(self, max_recent: int = 10):
        """
        Initialize command context tracker.
        
        Args:
            max_recent: Number of recent items to track
        """
        self.recent_artists = deque(maxlen=max_recent)
        self.recent_songs = deque(maxlen=max_recent)
        self.recent_albums = deque(maxlen=max_recent)
        self.user_favorites = {}  # artist/song -> play count
        self.playback_history = deque(maxlen=100)  # Full playback history
    
    def add_artist(self, artist: str):
        """Track recently played artist."""
        self.recent_artists.appendleft(artist)
        self.user_favorites[artist] = self.user_favorites.get(artist, 0) + 1
    
    def add_song(self, song: str, artist: Optional[str] = None):
        """Track recently played song."""
        self.recent_songs.appendleft(song)
        key = f"{artist}/{song}" if artist else song
        self.user_favorites[key] = self.user_favorites.get(key, 0) + 1
        
        if artist:
            self.add_artist(artist)
    
    def add_album(self, album: str):
        """Track recently played album."""
        self.recent_albums.appendleft(album)
    
    def suggest_artist_from_context(self, partial_query: str) -> Optional[str]:
        """
        Suggest artist from recently played items.
        
        If user says "play toxic" and recently played Backbencher,
        suggest that "toxic" might be from Backbencher.
        
        Args:
            partial_query: Song or query fragment
            
        Returns:
            Suggested artist or None
        """
        partial_lower = partial_query.lower()
        
        # Check if any recent artist might have this song
        for artist in self.recent_artists:
            # This is a heuristic - in real implementation,
            # would check against a music database
            if artist.lower().startswith(partial_lower[:2]):
                return artist
        
        # Check favorites for most played artist
        if self.user_favorites:
            favorite_artist = max(self.user_favorites.items(), key=lambda x: x[1])[0]
            if '/' not in favorite_artist:  # It's an artist, not a song
                return favorite_artist
        
        return None
    
    def suggest_entity_from_context(self, entity_type: str) -> Optional[str]:
        """
        Get most recently used entity of a type.
        
        Useful when entity wasn't clearly recognized.
        
        Args:
            entity_type: 'artist', 'song', or 'album'
            
        Returns:
            Most recent entity of this type or None
        """
        if entity_type == 'artist' and self.recent_artists:
            return self.recent_artists[0]
        elif entity_type == 'song' and self.recent_songs:
            return self.recent_songs[0]
        elif entity_type == 'album' and self.recent_albums:
            return self.recent_albums[0]
        
        return None
    
    def get_top_favorites(self, entity_type: str = 'artist', limit: int = 5) -> List[str]:
        """
        Get top favorite artists or songs.
        
        Args:
            entity_type: 'artist' or 'song'
            limit: Number to return
            
        Returns:
            List of top favorites
        """
        # Filter by type (songs have '/' in their key)
        if entity_type == 'artist':
            favorites = {k: v for k, v in self.user_favorites.items() if '/' not in k}
        else:
            favorites = {k: v for k, v in self.user_favorites.items() if '/' in k}
        
        if not favorites:
            return []
        
        return [k for k, v in sorted(favorites.items(), key=lambda x: x[1], reverse=True)][:limit]
    
    def disambiguate_entity(
        self,
        partial_entity: str,
        entity_type: str = 'artist',
        candidates: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Disambiguate entity using context.
        
        Example:
            If user says "play toxic" with partial recognition,
            and context shows Backbencher was recently played,
            we can disambiguate that it's "Toxic by Backbencher"
        
        Args:
            partial_entity: Partial or ambiguous entity
            entity_type: Type of entity
            candidates: List of possible candidates
            
        Returns:
            Best disambiguated entity or None
        """
        partial_lower = partial_entity.lower()
        
        # Try to find in recent history first
        if entity_type == 'artist':
            recent = list(self.recent_artists)
        elif entity_type == 'song':
            recent = list(self.recent_songs)
        elif entity_type == 'album':
            recent = list(self.recent_albums)
        else:
            recent = []
        
        # Check recent items
        for item in recent:
            if item.lower().startswith(partial_lower):
                return item
        
        # Check candidates
        if candidates:
            for candidate in candidates:
                if candidate.lower().startswith(partial_lower):
                    return candidate
        
        # Check favorites
        favorites = self.get_top_favorites(entity_type, limit=10)
        for fav in favorites:
            if fav.lower().startswith(partial_lower):
                return fav
        
        return None
    
    def to_dict(self) -> Dict:
        """Export context as dictionary."""
        return {
            'recent_artists': list(self.recent_artists),
            'recent_songs': list(self.recent_songs),
            'recent_albums': list(self.recent_albums),
            'user_favorites': self.user_favorites,
            'playback_count': len(self.playback_history),
        }
    
    def print_context(self):
        """Print current context state."""
        print("\n" + "="*60)
        print("🎵 Playback Context")
        print("="*60)
        
        if self.recent_artists:
            print(f"Recent Artists: {', '.join(list(self.recent_artists)[:3])}")
        
        if self.recent_songs:
            print(f"Recent Songs: {', '.join(list(self.recent_songs)[:3])}")
        
        if self.user_favorites:
            top_favorites = sorted(self.user_favorites.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"Top Favorites: {', '.join([k for k, v in top_favorites])}")
        
        print(f"Total Plays: {len(self.playback_history)}")
        print("="*60)
