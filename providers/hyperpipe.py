import requests
from .base import MusicProvider

class HyperpipeProvider(MusicProvider):
    name = "hyperpipe"

    # Hyperpipe API instances (public, no auth)
    INSTANCES = [
        "https://api.hyperpipe.app",
        "https://hyperapi.fly.dev",
    ]

    def _get(self, endpoint, params=None):
        for base in self.INSTANCES:
            try:
                url = f"{base}{endpoint}"
                r = requests.get(url, params=params, timeout=15, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                if r.status_code == 200:
                    return r.json()
            except Exception as e:
                print(f"[Hyperpipe ERROR] {base}: {e}")
        return None

    def search(self, query: str, limit: int = 20):
        data = self._get("/search", {"q": query, "filter": "songs"})
        if not data or "content" not in data:
            return []
        
        songs = []
        for item in data.get("content", [])[:limit]:
            if item.get("type") != "song":
                continue
            songs.append(self._format(item))
        return songs

    def song(self, song_id: str):
        data = self._get(f"/song/{song_id}")
        if not data:
            return None
        return self._format(data)

    def trending(self, limit: int = 20):
        # Hyperpipe trending/home
        data = self._get("/trending")
        if not data or "content" not in data:
            return []
        songs = [self._format(item) for item in data.get("content", [])[:limit] if item.get("type") == "song"]
        return songs

    def _format(self, item):
        if not item:
            return {}

        thumbnails = item.get("thumbnails", [])
        image = thumbnails[-1].get("url", "") if thumbnails else ""

        return {
            "id": item.get("videoId", ""),
            "title": item.get("title", "Unknown Title"),
            "artist": ", ".join(a.get("name", "") for a in item.get("artists", [])) if item.get("artists") else "Unknown Artist",
            "album": item.get("album", {}).get("name", "Unknown Album") if item.get("album") else "Unknown Album",
            "image": image,
            "url": item.get("url", "") or f"https://music.youtube.com/watch?v={item.get('videoId', '')}",
            "duration": item.get("duration", 0),
            "year": "",
            "source": "hyperpipe",
  }
  
