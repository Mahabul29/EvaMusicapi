import os
import random
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow your main app to call this API

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


def _get_path(path, params=None):
    for _ in range(MAX_ROUNDS):
        for base in API_BASES:
            data = _get(f"{base}{path}", params)
            if data:
                return data
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
        # Pick highest quality available
        for quality in ["320kbps", "160kbps", "96kbps"]:
            for item in download_url:
                if isinstance(item, dict) and item.get("quality") == quality:
                    return item.get("url", "")
        last = download_url[-1]
        return last.get("url", "") if isinstance(last, dict) else str(last)
    return ""


def format_song(song):
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
    }


def fetch_songs(query, limit=20):
    for _ in range(MAX_ROUNDS):
        for base, path, key in SEARCH_CONFIGS:
            data = _get(f"{base}{path}", {key: query, "limit": limit})
            if data:
                songs = _extract_songs(data)
                if songs:
                    return songs
    return []


def fetch_trending(limit=20):
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
        songs = fetch_songs(q, limit)
        if songs:
            _LAST_GOOD_TRENDING = songs
            return songs
    return _LAST_GOOD_TRENDING or []


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def health():
    return jsonify({"status": "ok", "message": "JioSaavn API is running"})


@app.route("/api/search")
def api_search():
    query = request.args.get("q", "")
    limit = request.args.get("limit", 20, type=int)
    if not query:
        return jsonify([])
    results = fetch_songs(query, limit)
    songs = [s for s in [format_song(x) for x in results] if s.get("url")]
    return jsonify(songs)


@app.route("/api/trending")
def api_trending():
    limit = request.args.get("limit", 20, type=int)
    results = fetch_trending(limit)
    songs = [s for s in [format_song(x) for x in results] if s.get("url")]
    return jsonify(songs)


@app.route("/api/song/<song_id>")
def api_song(song_id):
    data = _get_path(f"/songs/{song_id}")
    try:
        if data and isinstance(data.get("data"), list):
            song_data = data["data"][0]
        elif data and isinstance(data.get("data"), dict):
            song_data = data["data"]
        else:
            song_data = data or {}
        song = format_song(song_data)
        if not song.get("url"):
            return jsonify({"error": "No stream URL found"}), 404
        return jsonify(song)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/debug")
def api_debug():
    query = request.args.get("q", "arijit singh")
    results = []
    for base, path, key in SEARCH_CONFIGS:
        url = f"{base}{path}"
        data = _get(url, {key: query, "limit": 2})
        results.append({
            "url": url,
            "ok": bool(data),
            "songs": len(_extract_songs(data)) if data else 0,
        })
    return jsonify(results)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
