import requests
from .base import MusicProvider

class ItunesProvider(MusicProvider):
    name = "itunes"

    def _format_song(self, track: dict) -> dict:
        if not track:
            return {}

        # Upgrade artwork resolution from 100x100 to 500x500
        artwork = track.get("artworkUrl100", "/static/images/default-album.png")
        high_res_artwork = artwork.replace("100x100bb.jpg", "500x500bb.jpg")

        track_id = track.get("trackId", "")

        return {
            "id":       str(track_id),
            "title":    track.get("trackName", "Unknown Title"),
            "artist":   track.get("artistName", "Unknown Artist"),
            "album":    track.get("collectionName", "Unknown Album"),
            "image":    high_res_artwork,
            "url":      track.get("previewUrl", f"placeholder_for_itunes_{track_id}"),
            "duration": int(track.get("trackTimeMillis", 0) / 1000),
            "year":     track.get("releaseDate", "")[:4] if track.get("releaseDate") else "",
            "source":   "itunes",
        }

    def search(self, query: str, limit: int = 20):
        try:
            url = f"https://itunes.apple.com/search?term={requests.utils.quote(query)}&limit={limit}&entity=song"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                results = r.json().get("results", [])
                return [self._format_song(t) for t in results]
        except Exception as e:
            print(f"[ITUNES ERROR] Search failed: {e}")
        return []

    def song(self, song_id: str):
        try:
            url = f"https://itunes.apple.com/lookup?id={song_id}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                results = r.json().get("results", [])
                if results:
                    return self._format_song(results[0])
        except Exception as e:
            print(f"[ITUNES ERROR] Song lookup failed: {e}")
        return None

    def trending(self, limit: int = 20):
        # Fallback to a popular search phrase since iTunes doesn't expose a clean trending endpoint easily
        return self.search("Top Hits", limit=limit)
                
