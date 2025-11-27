"""
Language Models and Mappings for NLU.

Supports multiple languages with:
- Intent keywords for each language
- Context indicators
- Common phrases and slang
- Language-specific patterns
"""

from typing import Dict, List

# ============================================================================
# SWAHILI - East African Language (Primary Language for Music Player)
# ============================================================================

SWAHILI_MODELS = {
    'language_code': 'sw',
    'language_name': 'Swahili',
    'intents': {
        'play': {
            'keywords': ['cheza', 'ucheze', 'cheze', 'imba', 'tumia', 'anza'],
            'context_phrases': ['cheza', 'anza wajibu', 'jaribu'],
            'examples': [
                'cheza backbencher ya toxic',
                'imba diamond platinumz',
                'ucheze wizkid',
                'cheza songs za afrbeats',
            ],
        },
        'pause': {
            'keywords': ['simama', 'sakinisha', 'kamata', 'simamisha'],
            'context_phrases': ['simama kwa sasa', 'kamata kwa muda'],
            'examples': ['simama', 'simama wimbo'],
        },
        'resume': {
            'keywords': ['endelea', 'anza', 'rejea', 'rudia'],
            'context_phrases': ['endelea wimbo', 'anza tena'],
            'examples': ['endelea', 'anza tena wimbo'],
        },
        'stop': {
            'keywords': ['hankisha', 'acha', 'komesha', 'sitisha'],
            'context_phrases': ['hankisha kabisa', 'acha hiyo'],
            'examples': ['hankisha', 'acha wazimu'],
        },
        'volume': {
            'keywords': ['kasi', 'sauti', 'vitu', 'volamu'],
            'context_phrases': ['kasi nyingi', 'sauti nyingi', 'ongeza sauti'],
            'examples': [
                'ongeza kasi',
                'pungza sauti',
                'sauti 50',
                'volamu chini',
            ],
        },
        'search': {
            'keywords': ['tafuta', 'sagilia', 'shafuta', 'pata'],
            'context_phrases': ['tafuta wimbo', 'sagilia muziki'],
            'examples': [
                'tafuta cheap thrills',
                'sagilia backbencher',
                'pata songs za tanzania',
            ],
        },
        'next': {
            'keywords': ['ingia', 'iliyofuata', 'ijayo', 'forward'],
            'context_phrases': ['wimbo ijayo', 'nenda forward'],
            'examples': ['ingia wimbo', 'iliyofuata'],
        },
        'previous': {
            'keywords': ['nyuma', 'iliyotangulia', 'rudi', 'kurudi'],
            'context_phrases': ['wimbo uliotangulia', 'rudi nyuma'],
            'examples': ['nyuma', 'rudi nyuma wimbo'],
        },
        'status': {
            'keywords': ['hali', 'ingine', 'taarifa', 'nini'],
            'context_phrases': ['wimbo gani', 'nani anacheza'],
            'examples': ['hali gani', 'wimbo gani inachezwa'],
        },
        'help': {
            'keywords': ['msaada', 'nini', 'amri', 'ongea'],
            'context_phrases': ['nini ninaweza kufanya', 'amri gani'],
            'examples': ['msaada', 'nini anaweza', 'amri zote'],
        },
        'exit': {
            'keywords': ['toka', 'acha', 'kwaheri', 'enda'],
            'context_phrases': ['toka kabisa', 'kwaheri'],
            'examples': ['toka', 'kwaheri', 'acha programu'],
        },
    },
    'context_indicators': {
        'by': ['na', 'ya', 'kutoka'],  # "by" artist
        'from_album': ['kutoka', 'kwenye', 'ya'],
        'in_playlist': ['katika', 'kwenye'],
    },
    'entities': {
        'artists': {
            'backbencher': {
                'canonical': 'Backbencher',
                'nicknames': ['backbencher', 'bb', 'back bencher'],
                'genres': ['afrobeats', 'hiphop', 'east_african'],
            },
            'diamond': {
                'canonical': 'Diamond Platnumz',
                'nicknames': ['diamond', 'dpz', 'diamond platnumz'],
                'genres': ['afrobeats', 'tanzanian', 'bongo flava'],
            },
            'wizkid': {
                'canonical': 'Wizkid',
                'nicknames': ['wizkid', 'wiz', 'ayo balogun'],
                'genres': ['afrobeats', 'nigerian'],
            },
        },
        'songs': {
            'toxic': {
                'canonical': 'Toxic',
                'artists': ['Backbencher'],
                'aliases': ['toxic', 'toxik', 'toxics'],
            },
        },
    },
    'stop_words': {'na', 'ni', 'kwa', 'ya', 'wa', 'ama', 'cha', 'za', 'la'},
    'filler_words': ['jamani', 'sisi', 'wewe', 'yeye'],
}

# ============================================================================
# ENGLISH - Global Language
# ============================================================================

ENGLISH_MODELS = {
    'language_code': 'en',
    'language_name': 'English',
    'intents': {
        'play': {
            'keywords': ['play', 'start', 'put on', 'play song', 'play music'],
            'context_phrases': ['play song', 'play artist', 'put on'],
            'examples': [
                'play cheap thrills',
                'play sia',
                'start the music',
                'put on wizkid',
            ],
        },
        'pause': {
            'keywords': ['pause', 'pause song', 'hold on'],
            'context_phrases': ['pause', 'pause the music'],
            'examples': ['pause', 'pause the song'],
        },
        'resume': {
            'keywords': ['resume', 'continue', 'start again', 'go on'],
            'context_phrases': ['resume song', 'keep playing'],
            'examples': ['resume', 'continue the song'],
        },
        'stop': {
            'keywords': ['stop', 'stop music', 'stop playing'],
            'context_phrases': ['stop', 'stop it'],
            'examples': ['stop', 'stop playing'],
        },
        'volume': {
            'keywords': ['volume', 'volume up', 'volume down', 'louder', 'quieter'],
            'context_phrases': ['turn volume', 'make it louder'],
            'examples': [
                'volume up',
                'volume down',
                'louder',
                'quieter',
                'volume 50',
            ],
        },
        'search': {
            'keywords': ['search', 'find', 'look for', 'search for'],
            'context_phrases': ['search song', 'find artist'],
            'examples': [
                'search cheap thrills',
                'find wizkid',
                'look for backbencher',
            ],
        },
        'next': {
            'keywords': ['next', 'next song', 'skip', 'forward'],
            'context_phrases': ['next song', 'skip song'],
            'examples': ['next', 'skip', 'next song'],
        },
        'previous': {
            'keywords': ['previous', 'back', 'previous song', 'go back'],
            'context_phrases': ['previous song', 'go back'],
            'examples': ['previous', 'back', 'go back'],
        },
        'status': {
            'keywords': ['status', "what's playing", 'current', 'what song'],
            'context_phrases': ['what is playing', 'current song'],
            'examples': ["what's playing", 'current song', 'what song is this'],
        },
        'help': {
            'keywords': ['help', 'commands', 'what can i do', 'tell me'],
            'context_phrases': ['help me', 'tell me commands'],
            'examples': ['help', 'what can i do', 'tell me commands'],
        },
        'exit': {
            'keywords': ['exit', 'quit', 'goodbye', 'bye', 'close'],
            'context_phrases': ['exit', 'quit program'],
            'examples': ['exit', 'quit', 'goodbye'],
        },
    },
    'context_indicators': {
        'by': ['by', 'from', 'artist'],
        'from_album': ['from', 'in', 'album'],
        'in_playlist': ['in', 'from', 'playlist'],
    },
    'entities': {
        'artists': {
            'sia': {
                'canonical': 'Sia',
                'nicknames': ['sia', 'sia furler'],
                'genres': ['pop', 'electropop', 'indie pop'],
            },
            'wizkid': {
                'canonical': 'Wizkid',
                'nicknames': ['wizkid', 'wiz'],
                'genres': ['afrobeats', 'nigerian'],
            },
        },
        'songs': {
            'cheap thrills': {
                'canonical': 'Cheap Thrills',
                'artists': ['Sia'],
                'aliases': ['cheap thrills', 'cheep thrills'],
            },
        },
    },
    'stop_words': {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'for', 'of'},
    'filler_words': ['uh', 'um', 'like', 'you know', 'i mean'],
}

# ============================================================================
# SPANISH - Latin American Language
# ============================================================================

SPANISH_MODELS = {
    'language_code': 'es',
    'language_name': 'Spanish',
    'intents': {
        'play': {
            'keywords': ['toca', 'reproduce', 'pon', 'toca la canción'],
            'context_phrases': ['toca canción', 'reproduce música'],
            'examples': ['toca wizkid', 'reproduce cheap thrills'],
        },
        'pause': {
            'keywords': ['pausa', 'parar', 'detén'],
            'context_phrases': ['pausa la canción'],
            'examples': ['pausa', 'parar la música'],
        },
        'resume': {
            'keywords': ['continúa', 'reanuda', 'sigue'],
            'context_phrases': ['continúa canción'],
            'examples': ['continúa', 'reanuda la canción'],
        },
        'stop': {
            'keywords': ['para', 'detén', 'cancela'],
            'context_phrases': ['para la música'],
            'examples': ['para', 'detén la música'],
        },
        'volume': {
            'keywords': ['volumen', 'sonido', 'más alto', 'más bajo'],
            'context_phrases': ['volumen arriba', 'volumen abajo'],
            'examples': ['volumen arriba', 'más bajo', 'volumen 50'],
        },
        'search': {
            'keywords': ['busca', 'encuentra', 'búsqueda'],
            'context_phrases': ['busca canción', 'encuentra artista'],
            'examples': ['busca wizkid', 'encuentra cheap thrills'],
        },
        'next': {
            'keywords': ['siguiente', 'próxima', 'saltar'],
            'context_phrases': ['siguiente canción'],
            'examples': ['siguiente', 'saltar canción'],
        },
        'previous': {
            'keywords': ['anterior', 'atrás', 'volver'],
            'context_phrases': ['canción anterior'],
            'examples': ['anterior', 'volver atrás'],
        },
        'status': {
            'keywords': ['estado', 'actual', 'qué canción'],
            'context_phrases': ['qué está sonando'],
            'examples': ['estado', 'qué canción está sonando'],
        },
        'help': {
            'keywords': ['ayuda', 'comandos', 'qué puedo hacer'],
            'context_phrases': ['ayuda', 'dime los comandos'],
            'examples': ['ayuda', 'qué puedo hacer', 'comandos'],
        },
        'exit': {
            'keywords': ['salir', 'adiós', 'hasta luego'],
            'context_phrases': ['salir del programa'],
            'examples': ['salir', 'adiós'],
        },
    },
    'context_indicators': {
        'by': ['de', 'por'],
        'from_album': ['de', 'del'],
        'in_playlist': ['en', 'de'],
    },
    'stop_words': {'el', 'la', 'los', 'las', 'y', 'o', 'pero', 'en', 'de'},
    'filler_words': ['eh', 'um', 'uh', 'mira', 'sabes'],
}

# ============================================================================
# PORTUGUESE - Brazilian/European Language
# ============================================================================

PORTUGUESE_MODELS = {
    'language_code': 'pt',
    'language_name': 'Portuguese',
    'intents': {
        'play': {
            'keywords': ['toca', 'reproduz', 'toco', 'põe'],
            'context_phrases': ['toca música', 'reproduz canção'],
            'examples': ['toca wizkid', 'reproduz cheap thrills'],
        },
        'pause': {
            'keywords': ['pausa', 'pára', 'para'],
            'context_phrases': ['pausa a música'],
            'examples': ['pausa', 'pára a canção'],
        },
        'resume': {
            'keywords': ['continua', 'volta', 'recomece'],
            'context_phrases': ['continua a canção'],
            'examples': ['continua', 'volta a música'],
        },
        'stop': {
            'keywords': ['para', 'pára', 'cancela'],
            'context_phrases': ['pára a música'],
            'examples': ['para', 'cancela tudo'],
        },
        'volume': {
            'keywords': ['volume', 'som', 'mais alto', 'mais baixo'],
            'context_phrases': ['volume acima', 'volume abaixo'],
            'examples': ['volume acima', 'mais baixo', 'volume 50'],
        },
        'search': {
            'keywords': ['procura', 'busca', 'encontra'],
            'context_phrases': ['procura canção', 'busca artista'],
            'examples': ['procura wizkid', 'busca cheap thrills'],
        },
        'next': {
            'keywords': ['próxima', 'seguinte', 'pula'],
            'context_phrases': ['próxima canção'],
            'examples': ['próxima', 'pula canção'],
        },
        'previous': {
            'keywords': ['anterior', 'volta', 'anterior'],
            'context_phrases': ['canção anterior'],
            'examples': ['anterior', 'volta'],
        },
        'status': {
            'keywords': ['status', 'atual', 'qual canção'],
            'context_phrases': ['qual está tocando'],
            'examples': ['status', 'qual canção está tocando'],
        },
        'help': {
            'keywords': ['ajuda', 'comandos', 'o que posso fazer'],
            'context_phrases': ['ajuda', 'me diz os comandos'],
            'examples': ['ajuda', 'o que posso fazer', 'comandos'],
        },
        'exit': {
            'keywords': ['sair', 'adeus', 'tchau'],
            'context_phrases': ['sair do programa'],
            'examples': ['sair', 'adeus'],
        },
    },
    'context_indicators': {
        'by': ['de', 'por'],
        'from_album': ['de', 'do'],
        'in_playlist': ['em', 'de'],
    },
    'stop_words': {'o', 'a', 'os', 'as', 'e', 'ou', 'mas', 'em', 'de'},
    'filler_words': ['eh', 'um', 'uh', 'sabe', 'tipo'],
}

# ============================================================================
# FRENCH - European Language
# ============================================================================

FRENCH_MODELS = {
    'language_code': 'fr',
    'language_name': 'French',
    'intents': {
        'play': {
            'keywords': ['joue', 'lance', 'lis', 'mets'],
            'context_phrases': ['joue la chanson', 'lance la musique'],
            'examples': ['joue wizkid', 'lance cheap thrills'],
        },
        'pause': {
            'keywords': ['pause', 'arrête', 'paus'],
            'context_phrases': ['pause la chanson'],
            'examples': ['pause', 'arrête la musique'],
        },
        'resume': {
            'keywords': ['continue', 'reprend', 'relance'],
            'context_phrases': ['continue la chanson'],
            'examples': ['continue', 'reprend la musique'],
        },
        'stop': {
            'keywords': ['arrête', 'stoppe', 'arrêt'],
            'context_phrases': ['arrête tout'],
            'examples': ['arrête', 'stoppe la musique'],
        },
        'volume': {
            'keywords': ['volume', 'son', 'plus fort', 'plus bas'],
            'context_phrases': ['volume haut', 'volume bas'],
            'examples': ['volume haut', 'plus fort', 'volume 50'],
        },
        'search': {
            'keywords': ['cherche', 'trouve', 'recherche'],
            'context_phrases': ['cherche chanson', 'trouve artiste'],
            'examples': ['cherche wizkid', 'trouve cheap thrills'],
        },
        'next': {
            'keywords': ['suivante', 'prochaine', 'saut'],
            'context_phrases': ['prochaine chanson'],
            'examples': ['suivante', 'saut chanson'],
        },
        'previous': {
            'keywords': ['précédente', 'retour', 'avant'],
            'context_phrases': ['chanson précédente'],
            'examples': ['précédente', 'retour'],
        },
        'status': {
            'keywords': ['statut', 'actuel', 'quelle chanson'],
            'context_phrases': ['quelle est la chanson'],
            'examples': ['statut', 'quelle chanson joue'],
        },
        'help': {
            'keywords': ['aide', 'commandes', 'que puis je faire'],
            'context_phrases': ['aide', 'dis moi les commandes'],
            'examples': ['aide', 'que puis je faire', 'commandes'],
        },
        'exit': {
            'keywords': ['quitter', 'adieu', 'au revoir'],
            'context_phrases': ['quitter le programme'],
            'examples': ['quitter', 'adieu'],
        },
    },
    'context_indicators': {
        'by': ['de', 'par'],
        'from_album': ['de', 'du'],
        'in_playlist': ['dans', 'de'],
    },
    'stop_words': {'le', 'la', 'les', 'et', 'ou', 'mais', 'dans', 'de'},
    'filler_words': ['euh', 'um', 'uh', 'tu sais', 'quoi'],
}

# ============================================================================
# Language Models Registry
# ============================================================================

LANGUAGE_MODELS = {
    'sw': SWAHILI_MODELS,
    'en': ENGLISH_MODELS,
    'es': SPANISH_MODELS,
    'pt': PORTUGUESE_MODELS,
    'fr': FRENCH_MODELS,
}

# Get language model by code
def get_language_model(language_code: str) -> Dict:
    """Get language model by code."""
    return LANGUAGE_MODELS.get(language_code, ENGLISH_MODELS)

# List all supported languages
def list_languages() -> List[Dict[str, str]]:
    """List all supported languages."""
    return [
        {'code': code, 'name': model['language_name']}
        for code, model in LANGUAGE_MODELS.items()
    ]
