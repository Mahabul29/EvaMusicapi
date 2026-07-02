import requests
from .base import MusicProvider

class HearthisProvider(MusicProvider):
    name = "hearthis"

    def _format_song(self, track: dict) -> dict:
        if not track:
            return {}

        return {
            "id":       str(track.get("id", "")),
            "title":    track.get("title", "Unknown Title"),
            "artist":   track.get("user", {}).get("username", "Unknown Artist"),
            "album":    "HearThis Stream",
            "image":    track.get("thumb", "/static/images/default-album.png"),
            "url":      track.get("stream_url", ""),  # Full-length MP3 URL direct from server!
            "duration": int(track.get("duration", 0)),
            "year":     track.get("date", "")[:4] if track.get("date") else "",
            "source":   "hearthis",
        }

    def search(self, query: str, limit: int = 20):
        try:
            url = f"https://api-v2.hearthis.at/search?t={requests.utils.quote(query)}&count={limit}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                # HearThis can return a single dict if only 1 result is found
                if isinstance(data, dict):
                    data = [data]
                return [self._format_song(t) for t in data if isinstance(t, dict)]
        except Exception as e:
            print(f"[HEARTHIS ERROR] Search failed: {e}")
        return []

    def song(self, song_id: str):
        # Fallback metadata lookup using a search string strategy
        return None

    def trending(self, limit: int = 20):
        try:
            url = f"https://api-v2.hearthis.at/feed/?type=popular&count={limit}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                return [self._format_song(t) for t in r.json() if isinstance(t, dict)]
        except Exception as e:
            print(f"[HEARTHIS ERROR] Trending failed: {e}")
        return []
        
