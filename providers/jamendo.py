import requests
from .base import MusicProvider

class JamendoProvider(MusicProvider):
    name = "jamendo"
    BASE = "https://api.jamendo.com/v3.0"
    CLIENT_ID = "8b1b0ea3"

    def search(self, query: str, limit: int = 20):
        try:
            r = requests.get(f"{self.BASE}/tracks", params={
                "client_id": self.CLIENT_ID,
                "format": "json",
                "search": query,
                "limit": limit,
                "audioformat": "mp32",
            }, timeout=15)
            if r.status_code != 200:
                return []
            return [self._format(t) for t in r.json().get("results", [])]
        except Exception as e:
            print(f"[Jamendo ERROR] {e}")
            return []

    def song(self, track_id: str):
        try:
            r = requests.get(f"{self.BASE}/tracks", params={
                "client_id": self.CLIENT_ID,
                "format": "json",
                "id": track_id,
            }, timeout=15)
            if r.status_code != 200:
                return None
            results = r.json().get("results", [])
            return self._format(results[0]) if results else None
        except Exception as e:
            print(f"[Jamendo ERROR] {e}")
            return None

    def trending(self, limit: int = 20):
        try:
            r = requests.get(f"{self.BASE}/tracks", params={
                "client_id": self.CLIENT_ID,
                "format": "json",
                "order": "popularity_week",
                "limit": limit,
                "audioformat": "mp32",
            }, timeout=15)
            if r.status_code != 200:
                return []
            return [self._format(t) for t in r.json().get("results", [])]
        except Exception as e:
            print(f"[Jamendo ERROR] {e}")
            return []

    def _format(self, track):
        if not track:
            return {}
        return {
            "id": str(track.get("id", "")),
            "title": track.get("name", "Unknown Title"),
            "artist": track.get("artist_name", "Unknown Artist"),
            "album": track.get("album_name", "Jamendo"),
            "image": track.get("image", "") or track.get("album_image", ""),
            "url": track.get("audio", "") or track.get("audio_download", ""),
            "duration": track.get("duration", 0),
            "year": str(track.get("releasedate", ""))[:4] if track.get("releasedate") else "",
            "source": "jamendo",
          }
                             
