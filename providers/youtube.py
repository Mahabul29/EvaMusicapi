import yt_dlp
from .base import MusicProvider

class YouTubeProvider(MusicProvider):
    name = "youtube"

    YDL_OPTS = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "skip_download": True,
        "cookiefile": None,
    }

    def _ydl(self):
        return yt_dlp.YoutubeDL(self.YDL_OPTS)

    def search(self, query: str, limit: int = 20):
        with self._ydl() as ydl:
            info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            entries = info.get("entries", []) if info else []
            return [self._format(e) for e in entries if e]

    def song(self, video_id: str):
        with self._ydl() as ydl:
            info = ydl.extract_info(f"https://youtube.com/watch?v={video_id}", download=False)
            return self._format(info) if info else None

    def trending(self, limit: int = 20):
        # YouTube Music trending or popular searches
        queries = [
            "trending music 2024",
            "top songs 2024",
            "viral songs",
            "popular music",
        ]
        import random
        results = []
        for q in random.sample(queries, k=min(3, len(queries))):
            songs = self.search(q, limit // 3 + 1)
            results.extend(songs)
        return results[:limit]

    def _format(self, entry):
        if not entry:
            return {}

        # Get best audio URL
        url = ""
        if "url" in entry and entry.get("url"):
            url = entry["url"]
        elif "formats" in entry:
            audio_formats = [f for f in entry["formats"] if f.get("acodec") != "none" and f.get("vcodec") == "none"]
            if not audio_formats:
                audio_formats = [f for f in entry["formats"] if f.get("acodec") != "none"]
            if audio_formats:
                best = max(audio_formats, key=lambda f: (f.get("abr") or 0))
                url = best.get("url", "")

        thumbnails = entry.get("thumbnails", [])
        thumbnail = ""
        if thumbnails:
            # Get highest resolution thumbnail
            thumbnail = max(thumbnails, key=lambda t: t.get("height", 0) * t.get("width", 0)).get("url", "")
        else:
            thumbnail = entry.get("thumbnail", "")

        duration = entry.get("duration", 0)
        # Skip YouTube Shorts (under 60 seconds)
        if duration and duration < 60:
            return {}

        return {
            "id": entry.get("id", ""),
            "title": entry.get("title", "Unknown Title"),
            "artist": entry.get("uploader", entry.get("channel", "Unknown Artist")),
            "album": entry.get("album") or "YouTube",
            "image": thumbnail,
            "url": url,
            "duration": duration,
            "year": str(entry.get("upload_date", ""))[:4] if entry.get("upload_date") else "",
            "source": "youtube",
          }
          
