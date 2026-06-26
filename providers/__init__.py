from typing import List, Dict, Any
from .jiosaavn import JioSaavnProvider
from .jamendo import JamendoProvider
from .hyperpipe import HyperpipeProvider
from .youtube_music import YouTubeMusicProvider  # Import the new provider

ALL_PROVIDERS = [
    JioSaavnProvider(),    # Primary: Bollywood, Indian
    HyperpipeProvider(),   # Western, YouTube Music (piped api alternative)
    YouTubeMusicProvider(),# Native YouTube Music + On-Demand yt-dlp Resolution
    JamendoProvider(),     # Fallback: royalty-free
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
                # When source == "youtube", this executes the heavy yt-dlp lookup 
                # strictly for this single song_id on-demand.
                return provider.song(song_id)
            except Exception as e:
                print(f"[Provider ERROR] {provider.name}: {e}")
                return None
    return None

def trending_all(limit: int = 20) -> List[Dict[str, Any]]:
    results = []
    for provider in ALL_PROVIDERS:
        try:
            # YouTubeMusicProvider.trending() will return lightweight YouTube watch 
            # links to breeze past the frontend/Flask validation constraints.
            songs = provider.trending(limit)
            results.extend(songs)
        except Exception as e:
            print(f"[Provider ERROR] {provider.name}: {e}")
    return results
