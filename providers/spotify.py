import requests
from .base import MusicProvider

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

# Free, public community API wrapper instances for Spotify metadata
SPOTIFY_SEARCH_CONFIGS = [
    ("https://spotify-api-wrapper.appspot.com", "/artist", "query"),  # Public community master instance
]

MAX_ROUNDS = 2

def _get_spotify(url, params=None, timeout=15):
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"[Spotify API Error] {url}: {e}")
    return None

class SpotifyProvider(MusicProvider):
    name = "spotify"

    def _format_track(self, track: dict) -> dict:
        if not track:
            return {}

        # Parse album graphics safely
        images = track.get("album", {}).get("images", [])
        image_url = images[0].get("url", "") if images else ""

        # Gather collaborating artists
        artists = track.get("artists", [])
        artist_name = ", ".join([a.get("name", "") for a in artists])

        return {
            "id":       str(track.get("id", "")),
            "title":    track.get("name", "Unknown Title"),
            "artist":   artist_name or "Unknown Artist",
            "album":    track.get("album", {}).get("name", "Unknown Album"),
            "image":    image_url,
            "url":      track.get("preview_url") or "",  # 30-second audio stream endpoint
            "duration": int(track.get("duration_ms", 0) / 1000) if track.get("duration_ms") else 0,
            "year":     track.get("album", {}).get("release_date", "")[:4],
            "source":   "spotify",
        }

    def search(self, query: str, limit: int = 20):
        # Queries the public wrapper to extract track information without an official token
        for _ in range(MAX_ROUNDS):
            for base, path, key in SPOTIFY_SEARCH_CONFIGS:
                # Modifying path to request top tracks for a queried artist name via the public tool
                url = f"{base}/artist/{query}/top-tracks"
                data = _get_spotify(url)
                
                if data and isinstance(data, dict):
                    tracks = data.get("tracks", [])
                    return [self._format_track(t) for t in tracks[:limit]]
        return []

    def song(self, song_id: str):
        # Fallback to general lookup endpoints if matching a specific ID parameter
        url = f"https://api.spotify.com/v1/tracks/{song_id}"
        # Direct raw public web-player lookups require an anonymous token context 
        # For granular IDs, running track information directly or syncing to youtube_music is standard practice
        return None
  
