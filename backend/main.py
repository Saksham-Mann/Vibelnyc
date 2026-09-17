"""
Vibelnyc Recommendation Engine FastAPI Server
Production backend exposing audio feature recommendations, mood matching, and autocomplete.
"""

from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import sys
from pathlib import Path

# Add backend/src to path for clean package imports
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from recommender import VibeRecommender

# Global recommender engine cached in memory
recommender: Optional[VibeRecommender] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Loads trained ML models and dataset into memory on startup."""
    global recommender
    print("[Server] Initializing Vibelnyc ML Recommender Engine...")
    try:
        recommender = VibeRecommender()
        print("[Server] ML Engine loaded and ready for queries.")
    except Exception as e:
        print(f"[Server Warning] Could not load pre-trained models: {e}")
        print("[Server Warning] Run `python src/train_engine.py` to generate model artifacts.")
        recommender = None
    yield
    print("[Server] Shutting down Vibelnyc Server.")


app = FastAPI(
    title="Vibelnyc Recommendation API",
    description="Production Machine Learning Audio Recommender for Neo-Brutalist Sonic Matching.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for Next.js frontend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Schemas ---
class RecommendRequest(BaseModel):
    track_name: str = Field(..., description="Name of the seed track to match", min_length=1)
    artist_name: Optional[str] = Field(None, description="Optional artist name to narrow down seed track")
    n_results: int = Field(3, description="Number of recommendations to return", ge=1, le=20)


class MoodRecommendRequest(BaseModel):
    mood: str = Field(..., description="Mood preset: 'melancholy', 'high-energy', 'chill', or 'pop'")
    n_results: int = Field(3, description="Number of recommendations to return", ge=1, le=20)


# --- API Routes ---
@app.get("/", tags=["General"])
async def root():
    return {
        "name": "Vibelnyc API",
        "status": "online",
        "engine_ready": recommender is not None,
        "endpoints": {
            "search": "/api/search?q={query}",
            "recommend_track": "POST /api/recommend",
            "recommend_mood": "POST /api/recommend/mood",
            "docs": "/docs",
        },
    }


@app.get("/health", tags=["General"])
async def health_check():
    return {
        "status": "healthy",
        "engine_loaded": recommender is not None,
        "total_tracks": len(recommender.df) if recommender is not None else 0,
    }


@app.get("/api/search", tags=["Search"])
async def search_tracks(
    q: str = Query(..., min_length=1, description="Track title or artist query for autocomplete"),
    limit: int = Query(5, ge=1, le=20, description="Max results to return"),
):
    """Returns top matching track titles and artists for the frontend search bar."""
    if recommender is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML Engine models not loaded. Please ensure models are trained.",
        )

    results = recommender.search_tracks(q, limit=limit)
    return {
        "query": q,
        "count": len(results),
        "results": results,
    }


@app.post("/api/recommend", tags=["Recommendation"])
async def recommend_tracks(payload: RecommendRequest):
    """
    Recommends top N tracks closest in 8D audio feature space to the given seed track.
    Computes exact cosine similarity and feature deltas.
    """
    if recommender is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML Engine models not loaded. Please ensure models are trained.",
        )

    try:
        results = recommender.recommend_by_track(
            track_name=payload.track_name,
            artist_name=payload.artist_name,
            n_results=payload.n_results,
        )
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation engine error: {str(e)}",
        )


@app.post("/api/recommend/mood", tags=["Recommendation"])
async def recommend_mood(payload: MoodRecommendRequest):
    """
    Recommends top tracks matching sonic archetype vectors for
    'melancholy', 'high-energy', 'chill', or 'pop'.
    """
    if recommender is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML Engine models not loaded. Please ensure models are trained.",
        )

    try:
        results = recommender.recommend_by_mood(
            mood=payload.mood,
            n_results=payload.n_results,
        )
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Mood recommendation error: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
