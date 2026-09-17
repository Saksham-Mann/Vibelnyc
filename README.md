# Vibelnyc — Sonic DNA Music Recommendation Engine

**Vibelnyc** is an AI-powered music recommendation platform featuring an unsupervised Machine Learning recommendation engine, a FastAPI backend, and a Neo-Brutalist Next.js web application.

Discover tracks that match your exact sonic DNA through multidimensional audio vector matching and acoustic vibe clustering.

---

## Architecture Overview

```
Vibelnyc/
├── backend/
│   ├── data/
│   │   ├── spotify_tracks.csv       # Cleaned source dataset (~114k tracks)
│   │   └── dataset.csv
│   ├── models/                      # Trained model artifacts & Parquet cache
│   │   ├── cluster_metadata.json    # Human-readable vibe cluster definitions
│   │   ├── kmeans.joblib            # KMeans (k=8) vibe segmentation model
│   │   ├── nearest_neighbors.joblib # Exact cosine distance NearestNeighbors model
│   │   ├── processed_tracks.parquet # Normalized 81k+ deduplicated audio tracks
│   │   └── scaler.joblib            # Fitted MinMaxScaler for loudness & tempo
│   ├── src/
│   │   ├── preprocess.py            # Data cleaning, deduplication & normalization
│   │   ├── train_engine.py          # NearestNeighbors & KMeans training pipeline
│   │   └── recommender.py           # In-memory inference engine with feature deltas
│   ├── main.py                      # FastAPI server with CORS & REST endpoints
│   ├── download_data.py             # KaggleHub dataset fetcher
│   └── requirements.txt             # Version-locked Python dependencies
└── frontend/
    ├── app/                         # Next.js App Router (layout, styles, page)
    ├── components/
    │   ├── features/                # Modular UI (Header, Hero, AlbumArt, Waveform, TrackCard, AlgorithmPanel)
    │   └── ui/                      # Base UI primitives (Button)
    ├── data/                        # Mood presets & fallback mock data
    ├── types/                       # TypeScript interfaces (Mood, Track, Metric)
    └── package.json                 # Frontend dependencies (vibelnyc)
```

---

## Machine Learning Engine

The core ML pipeline analyzes 8 primary acoustic dimensions:
- `danceability` (0.0 to 1.0)
- `energy` (0.0 to 1.0)
- `norm_loudness` (normalized to 0.0 to 1.0 via `MinMaxScaler`)
- `speechiness` (0.0 to 1.0)
- `acousticness` (0.0 to 1.0)
- `instrumentalness` (0.0 to 1.0)
- `valence` (musical positiveness, 0.0 to 1.0)
- `norm_tempo` (normalized to 0.0 to 1.0 via `MinMaxScaler`)

### 1. Unsupervised Similarity Matching
- **Algorithm**: `sklearn.neighbors.NearestNeighbors(metric='cosine', algorithm='brute')`
- **Metric**: Exact cosine distance in the 8D normalized space.
- **Match Percentage**:
  $$\text{similarity\_percentage} = \text{round}((1.0 - \text{cosine\_distance}) \times 100, 1)$$

### 2. Vibe Clustering
- **Algorithm**: `sklearn.cluster.KMeans(n_clusters=8, random_state=42)`
- Automatically classifies tracks into 8 distinct sonic archetypes:
  - *Late Night Melancholic*
  - *High Energy Club & Dance*
  - *Mainstream Pop & Anthems*
  - *Acoustic Lo-Fi & Coffeehouse*
  - *Chill Downtempo & Groove*
  - *Dynamic Indie & Alternative*
  - *Deep Focus & Ambient*
  - *Atmospheric Eclectic*

### 3. Mood Presets
Target vectors for instant vibe calibration:
- **Melancholy**: Low valence (0.15), low energy (0.30), high acousticness (0.70).
- **High Energy**: High valence (0.80), high energy (0.90), high danceability (0.80).
- **Chill**: Moderate valence (0.50), low energy (0.30), high acousticness (0.80).
- **Pop**: High valence (0.85), high energy (0.80), high danceability (0.85).

---

## Quickstart & Setup Guide

### 1. Backend Setup

#### Step 1: Create Virtual Environment
```bash
cd backend
python -m venv .venv

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# On macOS/Linux:
source .venv/bin/activate
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Run the Training Pipeline Once
Train the `NearestNeighbors` and `KMeans` models and generate the Parquet cache:
```bash
python src/train_engine.py
```
*This processes `backend/data/spotify_tracks.csv`, trains both models, and exports the artifacts into `backend/models/`.*

#### Step 4: Start the FastAPI Server
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Interactive API documentation will be accessible at:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### 2. Frontend Setup

```bash
cd frontend
pnpm install
pnpm dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## API Endpoints

### 1. Autocomplete Search
`GET /api/search?q={query}&limit=5`
```json
{
  "query": "Radiohead",
  "count": 2,
  "results": [
    {
      "track_id": "70LcF31zb1H0PyJoS1Sx1r",
      "track_name": "Creep",
      "artists": "Radiohead",
      "album_name": "Pablo Honey",
      "popularity": 85
    },
    {
      "track_id": "10nyNJ6zNy2YVYLrcwLccB",
      "track_name": "No Surprises",
      "artists": "Radiohead",
      "album_name": "OK Computer",
      "popularity": 82
    }
  ]
}
```

### 2. Track Recommendation
`POST /api/recommend`
```json
{
  "track_name": "Weird Fishes",
  "artist_name": "Radiohead",
  "n_results": 3
}
```
**Response**:
```json
{
  "seed_track": {
    "track_name": "Weird Fishes/ Arpeggi",
    "artist": "Radiohead",
    "spotify_id": "4wajJ1o7jWIg62YqpkHC7S",
    "cluster_id": 0,
    "raw_features": {
      "energy": 61.0,
      "valence": 19.9,
      "danceability": 53.1,
      "acousticness": 77.2,
      "tempo": 153.0,
      "loudness": -8.0
    }
  },
  "cluster_info": {
    "cluster_id": 0,
    "cluster_name": "Deep Focus & Ambient"
  },
  "recommendations": [
    {
      "track_name": "Between (feat. Eli Teplin)",
      "artist": "Seven Lions;Eli Teplin",
      "spotify_id": "3rkB29gfzjboamcQNo5tSS",
      "match_percentage": 99.7,
      "cluster_id": 0,
      "cluster_name": "Deep Focus & Ambient",
      "features": { "energy": 50.2, "valence": 18.2, "danceability": 41.7 },
      "deltas": { "energy": -10.8, "valence": -1.7, "danceability": -11.4 }
    }
  ]
}
```

### 3. Mood Recommendation
`POST /api/recommend/mood`
```json
{
  "mood": "melancholy",
  "n_results": 3
}
```

---

## Dataset Attribution & Credits

Special thanks and credit to **Maharshi Pandya** for curating and publishing the [Spotify Tracks Dataset](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset) on Kaggle.

The dataset includes 114,000 Spotify tracks spanning 125 genres with rich acoustic features extracted via the Spotify Web API.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
