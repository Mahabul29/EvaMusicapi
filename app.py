import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from providers import search_all, get_song, trending_all, ALL_PROVIDERS

app = Flask(__name__)
CORS(app)


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


@app.route("/api/song/<source>/<song_id>")
def api_song(source, song_id):
    song = get_song(song_id, source=source)
    if not song:
        return jsonify({"error": "Song not found"}), 404
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
            
