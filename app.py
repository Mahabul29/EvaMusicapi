import os
import subprocess
from flask import Flask, jsonify, request
from flask_cors import CORS
from providers import search_all, get_song, trending_all, ALL_PROVIDERS

# Initialize the Flask application instance
app = Flask(__name__)
CORS(app)


# Helper function to extract a direct streaming audio URL via yt-dlp
def resolve_youtube_stream_url(video_id: str) -> str | None:
    try:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        # Execute yt-dlp command to extract the absolute best audio-only stream link
        cmd = [
            "yt-dlp",
            "-g",                 # Get URL flag
            "-f", "bestaudio",    # Grab best audio stream track
            video_url
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"[YT-DLP STREAM RESOLVE ERROR]: {e}")
    return None


@app.route("/")
def health():
    return jsonify({
        "status": "ok",
        "message": "EvaMusic API is running",
        "providers": [p.name for p in ALL_PROVIDERS]
    })


@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    limit = request.args.get("limit", 20, type=int)
    sources = request.args.get("sources")

    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    source_list = [s.strip() for s in sources.split(",")] if sources else None
    results = search_all(query, limit, sources=source_list)

    # Filter out songs with no stream URL
    valid = [s for s in results if s.get("url")]
    return jsonify(valid)


@app.route("/api/trending")
def api_trending():
    limit = request.args.get("limit", 20, type=int)
    results = trending_all(limit)

    # Filter out songs with no stream URL
    valid = [s for s in results if s.get("url")]
    return jsonify(valid)


@app.route("/api/song/<song_id>")
@app.route("/api/song/<source>/<song_id>")
def api_song(song_id, source=None):
    # If source is missing from the URL path, detect if it's a YouTube ID (length 11)
    if not source:
        source = "youtube_music" if len(song_id) == 11 else "jiosaavn"

    song = get_song(song_id, source=source)
    if not song:
        return jsonify({"error": f"Song not found in provider: {source}"}), 404

    # On-demand conversion: If the source is YouTube, resolve the stream URL using yt-dlp right now
    if source == "youtube_music" or song.get("source") == "youtube_music":
        direct_stream_url = resolve_youtube_stream_url(song_id)
        if direct_stream_url:
            song["url"] = direct_stream_url
        else:
            return jsonify({"error": "Failed to extract playable stream from YouTube"}), 404

    if not song.get("url"):
        return jsonify({"error": "No stream URL found"}), 404

    return jsonify(song)


@app.route("/api/debug")
def api_debug():
    query = request.args.get("q", "arijit singh")
    results = []

    for provider in ALL_PROVIDERS:
        try:
            songs = provider.search(query, limit=2)
            results.append({
                "provider": provider.name,
                "ok": len(songs) > 0,
                "songs_found": len(songs),
            })
        except Exception as e:
            results.append({
                "provider": provider.name,
                "ok": False,
                "error": str(e),
            })

    return jsonify(results)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
    
