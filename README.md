# JioSaavn Music API

Standalone API server to deploy on Koyeb. Powers your main JioSaavn Music app.

## Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | Health check |
| GET | `/api/trending?limit=20` | Trending songs |
| GET | `/api/search?q=arijit&limit=20` | Search songs |
| GET | `/api/song/<id>` | Single song by ID |
| GET | `/api/debug?q=arijit` | Check which mirrors are alive |

## Deploy on Koyeb

1. Push this folder as a **new GitHub repo** (e.g. `jiosaavn-api`)

2. Go to [koyeb.com](https://koyeb.com) → Create App

3. Choose **GitHub** → select your repo

4. Set these:
   - **Build command:** `pip install -r requirements.txt`
   - **Run command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60`
   - **Port:** `8000`

5. Deploy → you get a URL like:
   ```
   https://jiosaavn-api-yourname.koyeb.app
   ```

## Connect to your main app

In your main app's `app.py`, replace `API_BASES` and `SEARCH_CONFIGS` with your Koyeb URL:

```python
MY_API = "https://jiosaavn-api-yourname.koyeb.app"

@app.route('/api/search')
def api_search():
    q = request.args.get('q', '')
    r = requests.get(f"{MY_API}/api/search", params={"q": q})
    return jsonify(r.json())

@app.route('/api/trending')
def api_trending():
    r = requests.get(f"{MY_API}/api/trending")
    return jsonify(r.json())

@app.route('/api/song/<song_id>')
def api_song(song_id):
    r = requests.get(f"{MY_API}/api/song/{song_id}")
    return jsonify(r.json())
```

Or even simpler — set it as an environment variable:
```
API_BASE_URL=https://jiosaavn-api-yourname.koyeb.app
```
