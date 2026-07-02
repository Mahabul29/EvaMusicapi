import requests
from .base import MusicProvider

class SoundcloudProvider(MusicProvider):
    name = "soundcloud"

    def __init__(self):
        # Publicly accessible client ID used by federated scrapers
        self.client_id = "02gUJC0hH2ct1EGOcYXQIzRFU914352V"
        self.base_url = "https://api-v2.soundcloud.com"

    def _format_song(self, track: dict) -> dict:
        if not track:
            return {}

        track_id = track.get("id", "")
        artwork = track.get("artwork_url", "") or track.get("user", {}).get("avatar_url", "/static/images/default-album.png")
        high_res_artwork = artwork.replace("-large.jpg", "-t500x500.jpg") if artwork else artwork

        return {
            "id":       str(track_id),
            "title":    track.get("title", "Unknown Title"),
            "artist":   track.get("user", {}).get("username", "Unknown Artist"),
            "album":    "SoundCloud Single",
            "image":    high_res_artwork,
            "url":      f"placeholder_for_soundcloud_{track_id}", # Route to app.py/yt-dlp for direct decoding
            "duration": int(track.get("duration", 0) / 1000),
            "year":     track.get("created_at", "")[:4] if track.get("created_at") else "",
            "source":   "soundcloud",
        }

    def search(self, query: str, limit: int = 20):
        try:
            url = f"{self.base_url}/search/tracks"
            params = {"q": query, "client_id": self.client_id, "limit": limit}
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                collection = r.json().get("collection", [])
                return [self._format_song(t) for t in collection]
        except Exception as e:
            print(f"[SOUNDCLOUD ERROR] Search failed: {e}")
        return []

    def song(self, song_id: str):
        try:
            url = f"{self.base_url}/tracks/{song_id}"
            params = {"client_id": self.client_id}
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                return self._format_song(r.json())
        except Exception as e:
            print(f"[SOUNDCLOUD ERROR] Song lookup failed: {e}")
        return None

    def trending(self, limit: int = 20):
        try:
            # Pull top charts
            url = f"{self.base_url}/charts"
            params = {"kind": "top", "genre": "soundcloud:all-music", "client_id": self.client_id, "limit": limit}
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                collection = [item.get("track") for item in r.json().get("collection", []) if item.get("track")]
                return [self._format_song(t) for t in collection]
        except Exception as e:
            print(f"[SOUNDCLOUD ERROR] Trending failed: {e}")
        return []
          
