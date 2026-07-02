import os
import subprocess
from flask import Flask, jsonify, request
from flask_cors import CORS
from providers import search_all, get_song, trending_all, ALL_PROVIDERS

app = Flask(__name__)
CORS(app)


def resolve_youtube_stream_url(video_id: str) -> str | None:
    """
    Executes an advanced yt-dlp layer that includes client emulation arguments
    and drops cache profiles to permanently prevent '403 Forbidden' streaming blockages.
    """
    try:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Build strict parameters forcing standard consumer media application handshakes
        cmd = [
            "yt-dlp",
            "--rm-cache-dir",     # Explicitly clear stale response cookies/challenges
            "-g",                 # Get direct stream URL layout
            "-f", "bestaudio",    # Grab absolute best available audio
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "--extractor-args", "youtube:player_client=tv_downgraded,mweb", # Emulate robust mobile/TV environments
            video_url
        ]
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
        
        if result.returncode == 0 and result.stdout:
            extracted_url = result.stdout.strip()
            # Double check that we didn't receive an empty line configuration
            if extracted_url.startswith("http"):
                return extracted_url
        else:
            print(f"[YT-DLP CLI CRITICAL FAIL] Code: {result.returncode} | Err: {result.stderr.strip()}")
            
    except Exception as e:
        print(f"[YT-DLP RUNTIME EXCEPTION ERROR]: {e}")
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

    # Filter entries that have valid media links or placeholder tags
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
        if song_id.startswith("lastfm_"): source = "lastfm"
        elif song_id.startswith("audiomack_"): source = "audiomack"
        elif song_id.startswith("deezer_"): source = "deezer"
        else: source = "youtube_music" if len(song_id) == 11 else "jiosaavn"

    # 3. Pull structural dictionary metadata out of your provider class
    song = get_song(song_id, source=source)
    if not song:
        return jsonify({"error": f"Track could not be resolved from provider: {source}"}), 404

    # 4. CRITICAL THIRD-PARTY INTERCEPTOR FORCE-PLAY PIPELINE
    # If the source belongs to a 30-sec restricted or metadata provider,
    # we intercept it and immediately convert it to a full-length YouTube stream.
    if source in ["itunes", "lastfm", "audiomack", "deezer"]:
        search_target = f"{song['title']} {song['artist']}"
        print(f"[RESOLVER] Intercepted 3rd-party {source} track. Resolving full stream for: '{search_target}'")
        
        yt_provider = next((p for p in ALL_PROVIDERS if p.name == "youtube_music"), None)
        if yt_provider:
            try:
                # Query YouTube Music background index
                matches = yt_provider.search(search_target, limit=1)
                if matches and matches[0].get("id"):
                    target_video_id = matches[0]["id"]
                    
                    # Run it through our new armored browser emulator
                    resolved_stream = resolve_youtube_stream_url(target_video_id)
                    if resolved_stream:
                        print(f"[RESOLVER] Successfully matched and extracted full stream! ID: {target_video_id}")
                        song["url"] = resolved_stream
                        song["duration"] = matches[0].get("duration", song["duration"])
                        return jsonify(song)
            except Exception as search_err:
                print(f"[RESOLVER ERROR] Background matching failed: {search_err}")
                    
        # Fallback if extractor breaks completely
        print("[RESOLVER ALERT] Stream matching collapsed. Sending metadata object as-is.")
        return jsonify(song)

    # 5. STANDARD STREAM PROCESSING: For direct YouTube Music selections
    if source == "youtube_music":
        direct_stream = resolve_youtube_stream_url(song_id)
        if direct_stream:
            song["url"] = direct_stream
            return jsonify(song)
        else:
            return jsonify({"error": "Failed to extract direct audio from YouTube asset"}), 404

    # Return directly for stable native streaming setups (like JioSaavn, SoundCloud, Hearthis, Jamendo)
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
                             
