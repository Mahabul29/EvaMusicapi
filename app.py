import subprocess
import json

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
    
