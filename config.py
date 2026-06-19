import os

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000").rstrip("/")

# No API keys needed anywhere!
ENABLED_PROVIDERS = os.environ.get("ENABLED_PROVIDERS", "jiosaavn,deezer,jamendo").split(",")

ENDPOINTS = {
    "health":   f"{API_BASE_URL}/",
    "search":   f"{API_BASE_URL}/api/search",
    "trending": f"{API_BASE_URL}/api/trending",
    "song":     f"{API_BASE_URL}/api/song",
    "debug":    f"{API_BASE_URL}/api/debug",
}

def song_url(source: str, song_id: str) -> str:
    return f"{ENDPOINTS['song']}/{source}/{song_id}"

def search_url(query: str, limit: int = 20, sources: list | None = None) -> str:
    from urllib.parse import urlencode
    params = {"q": query, "limit": limit}
    if sources:
        params["sources"] = ",".join(sources)
    return f"{ENDPOINTS['search']}?{urlencode(params)}"
    
