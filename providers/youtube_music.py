import random
from ytmusicapi import YTMusic
from .base import MusicProvider


class YouTubeMusicProvider(MusicProvider):
    name = "youtube_music"

    def __init__(self):
        # Initializing without authentication files for public scraping.
        # If you ever need user-specific features, pass 'oauth.json' or 'browser.json' here.
        self.yt = YTMusic()
        self._last_good_trending = []

    def _format_song(self, song: dict) -> dict:
        """
        Normalizes YouTube Music's native dictionary schema into your standardized format.
        """
        if not song:
            return {}

        # 1. Parse Extraction of Artists
        artists_list = song.get("artists", [])
        if isinstance(artists_list, list):
            artist_name = ", ".join(a.get("name", "") for a in artists_list if isinstance(a, dict))
        else:
            artist_name = str(artists_list)

        # 2. Parse Album
        album_data = song.get("album", "Unknown Album")
        if isinstance(album_data, dict):
            album_name = album_data.get("name", "Unknown Album")
        else:
            album_name = album_data

        # 3. Parse Highest Resolution Thumbnail
        thumbnails = song.get("thumbnails", [])
        image_url = ""
        if isinstance(thumbnails, list) and thumbnails:
            image_url = thumbnails[-1].get("url", "")

        # 4. Handle Duration Parsing safely
        duration = song.get("duration", 0)
        if isinstance(duration, str) and ":" in duration:
            # Converts "MM:SS" strings to absolute integer seconds
            try:
                parts = list(map(int, duration.split(":")))
                duration = sum(x * 60**i for i, x in enumerate(reversed(parts)))
            except ValueError:
                duration = 0

        # Note: ytmusicapi does not natively expose direct streaming audio URLs 
        # (like downloadUrl). You will need a backend utility like `yt-dlp` to resolve 
        # the streaming link using the videoId on your playing state.
        video_id = song.get("videoId", "")
        stream_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else ""

        return {
            "id":       str(video_id),
            "title":    song.get("title", "Unknown Title"),
            "artist":   artist_name or "Unknown Artist",
            "album":    album_name,
            "image":    image_url or "/static/images/default-album.png",
            "url":      stream_url,
            "duration": duration,
            "year":     song.get("year", ""),
            "source":   "youtube_music",
        }

    def search(self, query: str, limit: int = 20):
        """
        Searches the public YouTube Music catalog, targeting specifically 'songs' results.
        """
        try:
            # Filtering by 'songs' guarantees the response structure strictly maps to track schemes
            raw_results = self.yt.search(query=query, filter="songs", limit=limit)
            return [self._format_song(s) for s in raw_results if s.get("resultType") == "song" or "videoId" in s]
        except Exception as e:
            print(f"[YT MUSIC API ERROR] Search failed for '{query}': {e}")
            return []

    def song(self, song_id: str):
        """
        Retrieves specific song metadata using its video/song ID.
        """
        try:
            raw_song = self.yt.get_song(videoId=song_id)
            if raw_song and "videoDetails" in raw_song:
                details = raw_song["videoDetails"]
                
                # Normalize get_song schema to fit our standard parser expectations
                normalized_song = {
                    "videoId": details.get("videoId"),
                    "title": details.get("title"),
                    "artists": [{"name": details.get("author", "")}],
                    "album": "Single",
                    "thumbnails": details.get("thumbnail", {}).get("thumbnails", []),
                    "duration": int(details.get("lengthSeconds", 0)),
                }
                return self._format_song(normalized_song)
        except Exception as e:
            print(f"[YT MUSIC API ERROR] Song lookup failed for ID {song_id}: {e}")
        return None

    def trending(self, limit: int = 20):
        """
        Simulates trending via top queries matching JioSaavn's rotation design pattern.
        """
        queries = [
            "trending songs billboard",
            "top global music hits",
            "viral tracks global",
            "new pop releases",
            "lofi music trending",
        ]
        for q in random.sample(queries, k=3):
            songs = self.search(q, limit)
            if songs:
                self._last_good_trending = songs
                return songs
        return self._last_good_trending or []
