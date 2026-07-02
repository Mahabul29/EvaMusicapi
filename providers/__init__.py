from typing import List, Dict, Any
from .jiosaavn import JioSaavnProvider
from .jamendo import JamendoProvider
from .hyperpipe import HyperpipeProvider
from .youtube_music import YouTubeMusicProvider
from .spotify import SpotifyProvider  # Import the new Spotify provider

ALL_PROVIDERS = [
    JioSaavnProvider(),       # Primary: Bollywood, Indian
    SpotifyProvider(),        # Global Curated Metadata & Search Results
    HyperpipeProvider(),      # Western, YouTube Music (piped api alternative)
    YouTubeMusicProvider(),   # Native YouTube Music + On-Demand yt-dlp Resolution
    JamendoProvider(),        # Fallback: royalty-free
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
    # 1. Handle native lookups for standard providers
    for provider in ALL_PROVIDERS:
        if provider.name == source:
            try:
                # If source is 'spotify', this gets metadata but might have a 30s or empty preview link
                song_data = provider.song(song_id)
                
                # 2. SMART CONVERSION FALLBACK FOR SPOTIFY:
                # If a spotify track is chosen for play, intercept and resolve a full stream via YouTube or JioSaavn
                if source == "spotify" and song_data:
                    search_query = f"{song_data['title']} {song_data['artist']}"
                    
                    # Try resolving stream through YouTube Music provider
                    yt_provider = next((p for p in ALL_PROVIDERS if p.name == "youtube"), None)
                    if yt_provider:
                        # Search YT for the track context
                        yt_results = yt_provider.search(search_query, limit=1)
                        if yt_results:
                            # Swap in the streamable URL and update duration if needed
                            song_data["url"] = yt_results[0]["url"]
                            song_data["source"] = "youtube_resolved"
                            return song_data
                            
                return song_data
            except Exception as e:
                print(f"[Provider ERROR] {provider.name}: {e}")
                return None
    return None

def trending_all(limit: int = 20) -> List[Dict[str, Any]]:
    results = []
    for provider in ALL_PROVIDERS:
        try:
            # Skip spotify for trending if it lacks a global generic trending feed config, 
            # or allow it if your provider class supports trending playlists!
            if provider.name == "spotify" and not hasattr(provider, 'trending'):
                continue
            songs = provider.trending(limit)
            results.extend(songs)
        except Exception as e:
            print(f"[Provider ERROR] {provider.name}: {e}")
    return results
                        
