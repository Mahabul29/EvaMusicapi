from typing import List, Dict, Any
from .base import MusicProvider
from .jiosaavn import JioSaavnProvider
from .youtube_music import YouTubeMusicProvider
from .audiomack import AudiomackProvider
from .lastfm import LastfmProvider

# Registered engines
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
        
    print(f"\n--- Starting Search for: '{query}' ---")
    for provider in providers_to_use:
        try:
            print(f"[DEBUG] Querying provider: {provider.name}...")
            songs = provider.search(query, limit=limit)
            
            if songs:
                print(f"[DEBUG] {provider.name} returned {len(songs)} tracks.")
                # Log a sample track structure to see what fields exist
                print(f"[DEBUG] Sample track format from {provider.name}: {songs[0]}")
                results.extend(songs)
            else:
                print(f"[DEBUG] {provider.name} returned 0 results.")
        except Exception as e:
            print(f"[ERROR] Provider {provider.name} crashed completely: {e}")
            
    print(f"--- Search Finished. Total combined items: {len(results)} ---\n")
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
                
