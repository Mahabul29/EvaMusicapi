import requests
from .base import MusicProvider

class LastfmProvider(MusicProvider):
    name = "lastfm"

    def __init__(self):
        # We use a public community API key configuration to avoid requiring local setups
        self.api_key = "2c2193b216999a4e4142f1cf1d931792"
        self.base_url = "http://ws.audioscrobbler.com/2.0/"

    def _format_song(self, track: dict) -> dict:
        if not track:
            return {}

        # Safely parse track title and artist metadata
        title = track.get("name", "Unknown Title")
        
        artist_data = track.get("artist", {})
        if isinstance(artist_data, dict):
            artist_name = artist_data.get("name", "Unknown Artist")
        else:
            artist_name = str(artist_data)

        # Safely parse image maps
        image_list = track.get("image", [])
        image_url = ""
        if isinstance(image_list, list) and image_list:
            # Grab the extra-large thumbnail variant
            image_url = image_list[-1].get("#text", "")

        # Create a combined identifier so app.py knows exactly how to query the fallback stream
        combined_slug = f"{title} - {artist_name}".replace(" ", "+")

        return {
            "id":       f"lastfm_{combined_slug}",
            "title":    title,
            "artist":   artist_name,
            "album":    "Last.fm Hit Chart",
            "image":    image_url or "/static/images/default-album.png",
            "url":      f"placeholder_for_lastfm_{combined_slug}",
            "duration": int(track.get("duration", 0)),
            "year":     "",
            "source":   "lastfm",
        }

    def search(self, query: str, limit: int = 20):
        try:
            params = {
                "method": "track.search",
                "track": query,
                "api_key": self.api_key,
                "limit": limit,
                "format": "json"
            }
            r = requests.get(self.base_url, params=params, timeout=10)
            if r.status_code == 200:
                tracks = r.json().get("results", {}).get("trackmatches", {}).get("track", [])
                # If a structural list returns, wrap it
                if isinstance(tracks, dict):
                    tracks = [tracks]
                return [self._format_song(t) for t in tracks]
        except Exception as e:
            print(f"[LAST.FM ERROR] Search failed: {e}")
        return []

    def song(self, song_id: str):
        # Because Last.fm doesn't use standard track IDs natively without an artist string context,
        # we decode our custom query slug structure back into text
        try:
            if song_id.startswith("lastfm_"):
                song_id = song_id.replace("lastfm_", "")
            
            clean_query = song_id.replace("+", " ")
            return {
                "id":       f"lastfm_{song_id}",
                "title":    clean_query.split(" - ")[0] if " - " in clean_query else clean_query,
                "artist":   clean_query.split(" - ")[1] if " - " in clean_query else "Unknown Artist",
                "album":    "Last.fm Hit Chart",
                "image":    "/static/images/default-album.png",
                "url":      f"placeholder_for_lastfm_{song_id}",
                "duration": 0,
                "year":     "",
                "source":   "lastfm",
            }
        except Exception as e:
            print(f"[LAST.FM ERROR] Track parsing failed: {e}")
        return None

    def trending(self, limit: int = 20):
        """
        Pulls down the absolute real-time top charts tracking globally across Last.fm!
        """
        try:
            params = {
                "method": "chart.gettoptracks",
                "api_key": self.api_key,
                "limit": limit,
                "format": "json"
            }
            r = requests.get(self.base_url, params=params, timeout=10)
            if r.status_code == 200:
                tracks = r.json().get("tracks", {}).get("track", [])
                return [self._format_song(t) for t in tracks]
        except Exception as e:
            print(f"[LAST.FM ERROR] Trending calculation failed: {e}")
        return []
      
