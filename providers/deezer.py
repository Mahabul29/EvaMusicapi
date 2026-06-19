import requests
from .base import MusicProvider

class DeezerProvider(MusicProvider):
    name = "deezer"

    BASE = "https://api.deezer.com"

    def search(self, query: str, limit: int = 20):
        url = f"{self.BASE}/search/track"
        params = {"q": query, "limit": limit}
        try:
            r = requests.get(url, params=params, timeout=15)
            if r.status_code != 200:
                return []
            items = r.json().get("data", [])
            return [self._format(t) for t in items]
        except Exception as e:
            print(f"[Deezer ERROR] {e}")
            return []

    def song(self, track_id: str):
        url = f"{self.BASE}/track/{track_id}"
        try:
            r = requests.get(url, timeout=15)
            if r.status_code != 200:
                return None
            return self._format(r.json())
        except Exception as e:
            print(f"[Deezer ERROR] {e}")
            return None

    def trending(self, limit: int = 20):
        # Deezer editorial charts
        url = f"{self.BASE}/chart/0/tracks"
        params = {"limit": limit}
        try:
            r = requests.get(url, params=params, timeout=15)
            if r.status_code != 200:
                return []
            items = r.json().get("data", [])
            return [self._format(t) for t in items]
        except Exception as e:
            print(f"[Deezer ERROR] {e}")
            return []

    def _format(self, track):
        if not track:
            return {}

        album = track.get("album", {})
        artist = track.get("artist", {})

        return {
            "id": str(track.get("id", "")),
            "title": track.get("title", "Unknown Title"),
            "artist": artist.get("name", "Unknown Artist"),
            "album": album.get("title", "Unknown Album"),
            "image": album.get("cover_xl") or album.get("cover_big") or album.get("cover") or "",
            "url": track.get("preview", ""),  # 30-sec preview MP3
            "duration": track.get("duration", 0),
            "year": str(track.get("release_date", ""))[:4] if track.get("release_date") else "",
            "source": "deezer",
      }
      
