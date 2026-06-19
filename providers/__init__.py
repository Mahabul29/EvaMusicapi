from typing import List, Dict, Any
from .jiosaavn import JioSaavnProvider
from .jamendo import JamendoProvider
from .deezer import DeezerProvider

ALL_PROVIDERS = [
    JioSaavnProvider(),
    DeezerProvider(),
    JamendoProvider(),
]

def search_all(query: str, limit: int = 20, sources: List[str] | None = None) -> List[Dict[str, Any]]:
    results = []
    for provider in ALL_PROVIDERS:
        if sources and provider.name not in sources:
            continue
        try:
            songs = provider.search(query, limit)
            results.extend(songs)
        except Exception as e:
            print(f"[Provider ERROR] {provider.name}: {e}")
    return results

def get_song(song_id: str, source: str = "jiosaavn") -> Dict[str, Any] | None:
    for provider in ALL_PROVIDERS:
        if provider.name == source:
            try:
                return provider.song(song_id)
            except Exception as e:
                print(f"[Provider ERROR] {provider.name}: {e}")
                return None
    return None

def trending_all(limit: int = 20) -> List[Dict[str, Any]]:
    results = []
    for provider in ALL_PROVIDERS:
        try:
            songs = provider.trending(limit)
            results.extend(songs)
        except Exception as e:
            print(f"[Provider ERROR] {provider.name}: {e}")
    return results
      
