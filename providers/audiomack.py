import requests
from .base import MusicProvider

class AudiomackProvider(MusicProvider):
    name = "audiomack"

    def _format_song(self, song: dict) -> dict:
        if not song:
            return {}

        # Parse artist and stream info safely
        artist_name = song.get("uploader", {}).get("name", song.get("artist", "Unknown Artist"))
        
        # Audiomack tracks usually allow streaming access via their direct web links
        # or we flag it as a placeholder to resolve via yt-dlp/fallback
        track_id = song.get("id", "")
        stream_url = song.get("streaming_url", f"placeholder_for_audiomack_{track_id}")

        return {
            "id":       str(track_id),
            "title":    song.get("title", "Unknown Title"),
            "artist":   artist_name,
            "album":    song.get("album", "Audiomack Release") or "Audiomack Release",
            "image":    song.get("image_url", "/static/images/default-album.png"),
            "url":      stream_url,
            "duration": int(song.get("duration", 0)),
            "year":     song.get("released", "")[:4] if song.get("released") else "",
            "source":   "audiomack",
        }

    def search(self, query: str, limit: int = 20):
        try:
            # Accessing public web endpoint for global query discovery
            url = f"https://v2.audiomack.com/search?q={requests.utils.quote(query)}&limit={limit}&show=tracks"
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                results = r.json().get("results", [])
                return [self._format_song(s) for s in results]
        except Exception as e:
            print(f"[AUDIOMACK ERROR] Search failed: {e}")
        return []

    def song(self, song_id: str):
        try:
            url = f"https://v2.audiomack.com/song/{song_id}"
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                return self._format_song(r.json())
        except Exception as e:
            print(f"[AUDIOMACK ERROR] Track query failed: {e}")
        return None

    def trending(self, limit: int = 20):
        try:
            url = f"https://v2.audiomack.com/featured/music?limit={limit}"
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                results = r.json().get("results", [])
                return [self._format_song(s) for s in results if s.get("type") == "song"]
        except Exception as e:
            print(f"[AUDIOMACK ERROR] Trending failed: {e}")
        return []
      
