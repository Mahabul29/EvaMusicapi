import os

# ─── API FQDN Configuration ───────────────────────────────────────────────────
# Set the API_BASE_URL environment variable in your deployment (Render, Railway,
# Vercel, etc.) to point to wherever this Flask app is hosted.
#
# Example:
#   export API_BASE_URL=https://your-app.onrender.com
#
# Falls back to localhost for local development.

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000").rstrip("/")

# ─── Endpoint helpers (import these in your other repos) ──────────────────────

ENDPOINTS = {
    "health":   f"{API_BASE_URL}/",
    "search":   f"{API_BASE_URL}/api/search",
    "trending": f"{API_BASE_URL}/api/trending",
    "song":     f"{API_BASE_URL}/api/song",   # append /<song_id>
    "debug":    f"{API_BASE_URL}/api/debug",
}


def song_url(song_id: str) -> str:
    """Return the full URL for a single song lookup."""
    return f"{ENDPOINTS['song']}/{song_id}"


def search_url(query: str, limit: int = 20) -> str:
    """Return the full search URL with query params."""
    from urllib.parse import urlencode
    return f"{ENDPOINTS['search']}?{urlencode({'q': query, 'limit': limit})}"


def trending_url(limit: int = 20) -> str:
    """Return the full trending URL with query params."""
    from urllib.parse import urlencode
    return f"{ENDPOINTS['trending']}?{urlencode({'limit': limit})}"
  
