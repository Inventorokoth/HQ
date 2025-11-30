impoclass CommandParser:
    def __init__(self):
        self.commands = {
            'play': self._parse_play,
            'pause': self._parse_simple,
            'resume': self._parse_simple,
            'stop': self._parse_simple,
            'volume': self._parse_volume,
            'seek': self._parse_seek,
            'search': self._parse_search,
            'status': self._parse_simple,
            'help': self._parse_simple,
            'voice': self._parse_simple,
            'repeat': self._parse_simple,
            'history': self._parse_simple,
            'stats': self._parse_simple,
            'context': self._parse_simple,
            'exit': self._parse_simple,
        }from typing import Dict, List, Tuple, Optional

class CommandParser:
    def __init__(self):
        self.commands = {
            'play': self._parse_play,
            'pause': self._parse_simple,
            'resume': self._parse_simple,
            'stop': self._parse_simple,
            'volume': self._parse_volume,
            'seek': self._parse_seek,
            'search': self._parse_search,
            'status': self._parse_simple,
            'help': self._parse_simple,
            'voice': self._parse_simple,
            'repeat': self._parse_simple,
            'history': self._parse_simple,
            'stats': self._parse_simple,
            'context': self._parse_simple,
            'exit': self._parse_simple,
        }
    
    def parse(self, input_str: str) -> Tuple[str, Dict]:
        """Parse input string and return command and parameters."""
        if not input_str.strip():
            return '', {}
        
        try:
            parts = shlex.split(input_str)
            if not parts:
                return '', {}
            
            command = parts[0].lower()
            args = parts[1:]
            
            if command in self.commands:
                return command, self.commands[command](args)
            else:
                return 'unknown', {'input': input_str}
                
        except Exception as e:
            return 'error', {'error': str(e)}
    
    def _parse_simple(self, args: List[str]) -> Dict:
        return {}
    
    def _parse_play(self, args: List[str]) -> Dict:
        if not args:
            return {'error': 'No search term or URL provided'}
        
        query = ' '.join(args)
        return {'query': query}
    
    def _parse_volume(self, args: List[str]) -> Dict:
        if not args:
            return {'error': 'No volume level provided'}
        
        try:
            volume = int(args[0])
            return {'volume': volume}
        except ValueError:
            return {'error': 'Volume must be a number'}
    
    def _parse_seek(self, args: List[str]) -> Dict:
        if not args:
            return {'error': 'No position provided'}
        
        try:
            position = float(args[0])
            return {'position': position}
        except ValueError:
            return {'error': 'Position must be a number'}
    
    def _parse_search(self, args: List[str]) -> Dict:
        if not args:
            return {'error': 'No search term provided'}
        
        query = ' '.join(args)
        return {'query': query}