import requests
from .base import MusicProvider

class iTunesProvider(MusicProvider):
    name = "itunes"

    def search(self, query: str, limit: int = 20):
        try:
            r = requests.get(
                "https://itunes.apple.com/search",
                params={"term": query, "media": "music", "entity": "song", "limit": limit},
                timeout=15
            )
            if r.status_code != 200:
                return []
            results = r.json().get("results", [])
            return [self._format(t) for t in results]
        except Exception as e:
            print(f"[iTunes ERROR] {e}")
            return []

    def song(self, track_id: str):
        try:
            r = requests.get(
                "https://itunes.apple.com/lookup",
                params={"id": track_id},
                timeout=15
            )
            if r.status_code != 200:
                return None
            results = r.json().get("results", [])
            return self._format(results[0]) if results else None
        except Exception as e:
            print(f"[iTunes ERROR] {e}")
            return None

    def trending(self, limit: int = 20):
        # iTunes doesn't have a trending endpoint, search popular terms
        return self.search("top hits 2024", limit)

    def _format(self, track):
        if not track:
            return {}
        return {
            "id": str(track.get("trackId", "")),
            "title": track.get("trackName", "Unknown Title"),
            "artist": track.get("artistName", "Unknown Artist"),
            "album": track.get("collectionName", "Unknown Album"),
            "image": track.get("artworkUrl100", "").replace("100x100", "600x600"),
            "url": track.get("previewUrl", ""),  # 30s preview only!
            "duration": track.get("trackTimeMillis", 0) // 1000,
            "year": str(track.get("releaseDate", ""))[:4] if track.get("releaseDate") else "",
            "source": "itunes",
          }
      
