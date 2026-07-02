from typing import List, Dict, Any
from .base import MusicProvider
from .jiosaavn import JioSaavnProvider
from .youtube_music import YouTubeMusicProvider
from .audiomack import AudiomackProvider
from .lastfm import LastfmProvider

# Only register the working and fully configured providers
ALL_PROVIDERS: List[MusicProvider] = [
    JioSaavnProvider(),
    YouTubeMusicProvider(),
    AudiomackProvider(),
    LastfmProvider()
]

def search_all(query: str, limit: int = 20, sources: List[str] = None) -> List[Dict[str, Any]]:
    results = []
    providers_to_use = ALL_PROVIDERS
    
    if sources:
        providers_to_use = [p for p in ALL_PROVIDERS if p.name in sources]
        
    for provider in providers_to_use:
        try:
            songs = provider.search(query, limit=limit)
            if songs:
                results.extend(songs)
        except Exception as e:
            print(f"[SEARCH ERROR] Provider {provider.name} failed: {e}")
            
    return results

def get_song(song_id: str, source: str) -> Dict[str, Any] | None:
    provider = next((p for p in ALL_PROVIDERS if p.name == source), None)
    if provider:
        try:
            return provider.song(song_id)
        except Exception as e:
            print(f"[SONG LOOKUP ERROR] Provider {source} failed for ID {song_id}: {e}")
    return None

def trending_all(limit: int = 20) -> List[Dict[str, Any]]:
    results = []
    for provider in ALL_PROVIDERS:
        try:
            songs = provider.trending(limit=limit)
            if songs:
                results.extend(songs)
        except Exception as e:
            print(f"[TRENDING ERROR] Provider {provider.name} failed: {e}")
    return results
                     
