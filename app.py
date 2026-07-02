import os
import subprocess
from flask import Flask, jsonify, request
from flask_cors import CORS
from providers import search_all, get_song, trending_all, ALL_PROVIDERS

app = Flask(__name__)
CORS(app)


def resolve_youtube_stream_url(video_id: str) -> str | None:
    """
    Executes yt-dlp to extract the absolute best direct audio-only stream link
    from a YouTube video ID.
    """
    try:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        cmd = [
            "yt-dlp",
            "-g",                 # Get direct stream URL flag
            "-f", "bestaudio",    # Grab best audio stream track
            video_url
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=12)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"[YT-DLP EXTRACTION ERROR]: {e}")
    return None


@app.route("/")
def health():
    return jsonify({
        "status": "ok",
        "message": "EvaMusic Engine Core running successfully",
        "active_providers": [p.name for p in ALL_PROVIDERS]
    })


@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    limit = request.args.get("limit", 20, type=int)
    sources = request.args.get("sources")

    if not query:
        return jsonify({"error": "Missing mandatory query parameter 'q'"}), 400

    source_list = [s.strip() for s in sources.split(",")] if sources else None
    results = search_all(query, limit, sources=source_list)

    # Allow entries that have valid media links or internal placeholder flags
    valid = [s for s in results if s.get("url")]
    return jsonify(valid)


@app.route("/api/trending")
def api_trending():
    limit = request.args.get("limit", 20, type=int)
    results = trending_all(limit)
    valid = [s for s in results if s.get("url")]
    return jsonify(valid)


@app.route("/api/song/<song_id>")
@app.route("/api/song/<source>/<song_id>")
def api_song(song_id, source=None):
    # 1. Clean parameters safely
    song_id = str(song_id).strip()
    if source:
        source = str(source).lower().strip()

    # 2. Contextual detector if source path parameter wasn't supplied explicitly
    if not source:
        if song_id.startswith("lastfm_"):
            source = "lastfm"
        elif song_id.startswith("audiomack_"):
            source = "audiomack"
        else:
            source = "youtube_music" if len(song_id) == 11 else "jiosaavn"

    # 3. Pull structural dictionary metadata out of your provider class
    song = get_song(song_id, source=source)
    if not song:
        return jsonify({"error": f"Track could not be resolved from provider: {source}"}), 404

    # 4. CRITICAL INTERCEPTOR FORCE-PLAY PIPELINE
    # If the source belongs to a metadata engine or preview-limited service,
    # we intercept it and immediately convert it to a full YouTube stream.
    if source in ["itunes", "lastfm", "audiomack"]:
        search_target = f"{song['title']} {song['artist']}"
        print(f"[RESOLVER] Intercepted {source} track. Searching YouTube for full stream: '{search_target}'")
        
        yt_provider = next((p for p in ALL_PROVIDERS if p.name == "youtube_music"), None)
        if yt_provider:
            try:
                # Query YouTube Music background index
                matches = yt_provider.search(search_target, limit=1)
                if matches and matches[0].get("id"):
                    target_video_id = matches[0]["id"]
                    
                    # Run it through your yt-dlp direct extractor
                    resolved_stream = resolve_youtube_stream_url(target_video_id)
                    if resolved_stream:
                        print(f"[RESOLVER] Successfully found match! Video ID: {target_video_id}")
                        song["url"] = resolved_stream
                        # Swap out the 30-sec limit layout for the real track duration
                        song["duration"] = matches[0].get("duration", song["duration"])
                        return jsonify(song)
            except Exception as search_err:
                print(f"[RESOLVER ERROR] Background matching failed: {search_err}")
                    
        # If background lookup fails completely, send the data as-is (last resort snippet)
        print("[RESOLVER ALERT] Fallback search failed. Defaulting back to snippet link.")
        return jsonify(song)

    # 5. STANDARD STREAM PROCESSING: For direct YouTube Music selections
    if source == "youtube_music":
        direct_stream = resolve_youtube_stream_url(song_id)
        if direct_stream:
            song["url"] = direct_stream
            return jsonify(song)
        else:
            return jsonify({"error": "Failed to extract direct audio from YouTube asset"}), 404

    # Return directly for stable native streaming setups (like JioSaavn)
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
        
