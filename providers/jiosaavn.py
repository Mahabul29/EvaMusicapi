import random
import requests
from .base import MusicProvider

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

SEARCH_CONFIGS = [
    ("https://jiosaavn-api-2.vercel.app",        "/api/search/songs", "query"),
    ("https://saavn.dev",                        "/api/search/songs", "query"),
    ("https://jiosaavn-api-ts.vercel.app",       "/api/search/songs", "query"),
    ("https://jiosaavn-api-sigma.vercel.app",    "/api/search/songs", "query"),
    ("https://jiosaavn-api-tau.vercel.app",      "/api/search/songs", "query"),
    ("https://jiosaavn-api-codewithwilliam.vercel.app", "/api/search/songs", "query"),
    ("https://saavn-api-eight.vercel.app",       "/api/search/songs", "query"),
]

API_BASES = [
    "https://jiosaavn-api-2.vercel.app/api",
    "https://saavn.dev/api",
    "https://jiosaavn-api-ts.vercel.app/api",
    "https://jiosaavn-api-sigma.vercel.app/api",
    "https://jiosaavn-api-tau.vercel.app/api",
    "https://jiosaavn-api-codewithwilliam.vercel.app/api",
    "https://saavn-api-eight.vercel.app/api",
]

MAX_ROUNDS = 2
_LAST_GOOD_TRENDING = []


def _get(url, params=None, timeout=20):
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
        if r.status_code == 200:
            data = r.json()
            if data and data != {} and data != []:
                return data
    except Exception as e:
        print(f"[API ERROR] {url}: {e}")
    return None


def _extract_songs(data):
    if not data:
        return []
    candidates = [
        data.get("data", {}).get("results") if isinstance(data.get("data"), dict) else None,
        data.get("data"),
        data.get("results"),
        data.get("result"),
        data,
    ]
    for c in candidates:
        if isinstance(c, list) and len(c) > 0:
            return c
    return []


def _best_url(download_url):
    if not download_url:
        return ""
    if isinstance(download_url, str):
        return download_url
    if isinstance(download_url, list) and download_url:
        for quality in ["320kbps", "160kbps", "96kbps"]:
            for item in download_url:
                if isinstance(item, dict) and item.get("quality") == quality:
                    return item.get("url", "")
        last = download_url[-1]
        return last.get("url", "") if isinstance(last, dict) else str(last)
    return ""


def _format_song(song):
    if not song:
        return {}

    image = song.get("image", "/static/images/default-album.png")
    if isinstance(image, list) and image:
        image = image[-1].get("url", "")
    elif isinstance(image, dict):
        image = image.get("url", "")

    artists = song.get("artists", {})
    if isinstance(artists, dict):
        primary = artists.get("primary", [])
        artist = ", ".join(a.get("name", "") for a in primary if isinstance(a, dict))
    elif isinstance(artists, list):
        artist = ", ".join(a.get("name", "") for a in artists if isinstance(a, dict))
    else:
        artist = song.get("primaryArtists", song.get("artist", "Unknown Artist"))

    album = song.get("album", "Unknown Album")
    if isinstance(album, dict):
        album = album.get("name", "Unknown Album")

    return {
        "id":       str(song.get("id", "")),
        "title":    song.get("name", song.get("title", "Unknown Title")),
        "artist":   artist or "Unknown Artist",
        "album":    album,
        "image":    image or "",
        "url":      _best_url(song.get("downloadUrl", song.get("download_url", []))),
        "duration": song.get("duration", 0),
        "year":     song.get("year", ""),
        "source":   "jiosaavn",
    }


class JioSaavnProvider(MusicProvider):
    name = "jiosaavn"

    def search(self, query: str, limit: int = 20):
        for _ in range(MAX_ROUNDS):
            for base, path, key in SEARCH_CONFIGS:
                data = _get(f"{base}{path}", {key: query, "limit": limit})
                if data:
                    songs = _extract_songs(data)
                    if songs:
                        return [_format_song(s) for s in songs]
        return []

    def song(self, song_id: str):
        for _ in range(MAX_ROUNDS):
            for base in API_BASES:
                data = _get(f"{base}/songs/{song_id}")
                if data:
                    try:
                        if isinstance(data.get("data"), list):
                            song_data = data["data"][0]
                        elif isinstance(data.get("data"), dict):
                            song_data = data["data"]
                        else:
                            song_data = data or {}
                        return _format_song(song_data)
                    except Exception:
                        continue
        return None

    def trending(self, limit: int = 20):
        global _LAST_GOOD_TRENDING
        queries = [
            "trending bollywood 2024",
            "top hindi songs",
            "arijit singh hits",
            "bollywood new releases",
            "viral songs india",
            "punjabi hits",
            "latest songs",
        ]
        for q in random.sample(queries, k=3):
            songs = self.search(q, limit)
            if songs:
                _LAST_GOOD_TRENDING = songs
                return songs
        return _LAST_GOOD_TRENDING or []
          
