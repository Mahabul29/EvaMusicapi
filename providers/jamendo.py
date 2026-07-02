import requests
from .base import MusicProvider

class JamendoProvider(MusicProvider):
    name = "jamendo"

    def __init__(self):
        # Open community developer client ID
        self.client_id = "56d30c95"

    def _format_song(self, track: dict) -> dict:
        if not track:
            return {}

        return {
            "id":       str(track.get("id", "")),
            "title":    track.get("name", "Unknown Title"),
            "artist":   track.get("artist_name", "Unknown Artist"),
            "album":    track.get("album_name", "Unknown Album"),
            "image":    track.get("album_image", "/static/images/default-album.png"),
            "url":      track.get("audio", ""),  # Full audio track file URL
            "duration": int(track.get("duration", 0)),
            "year":     track.get("releasedate", "")[:4] if track.get("releasedate") else "",
            "source":   "jamendo",
        }

    def search(self, query: str, limit: int = 20):
        try:
            url = f"https://api.jamendo.com/v3.0/tracks/?client_id={self.client_id}&format=json&search={requests.utils.quote(query)}&limit={limit}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                results = r.json().get("results", [])
                return [self._format_song(t) for t in results]
        except Exception as e:
            print(f"[JAMENDO ERROR] Search failed: {e}")
        return []

    def song(self, song_id: str):
        try:
            url = f"https://api.jamendo.com/v3.0/tracks/?client_id={self.client_id}&format=json&id={song_id}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                results = r.json().get("results", [])
                if results:
                    return self._format_song(results[0])
        except Exception as e:
            print(f"[JAMENDO ERROR] Lookup failed: {e}")
        return None

    def trending(self, limit: int = 20):
        try:
            url = f"https://api.jamendo.com/v3.0/tracks/?client_id={self.client_id}&format=json&order=boost&limit={limit}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                results = r.json().get("results", [])
                return [self._format_song(t) for t in results]
        except Exception as e:
            print(f"[JAMENDO ERROR] Trending failed: {e}")
        return []
        
