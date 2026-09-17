"""
Vibelnyc Recommendation Engine FastAPI Server
Production backend exposing audio feature recommendations, mood matching, and autocomplete.
"""

import logging
import sys
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from fastapi import FastAPI, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Configure structured logging for backend operations
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(name)s: %(message)s",
)
logger = logging.getLogger("vibelnyc.api")

# Add backend/src to path for clean package imports
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from recommender import VibeRecommender

# Global recommender engine cached in memory
recommender: Optional[VibeRecommender] = None


class InMemoryRateLimiter:
    """
    Sliding window in-memory rate limiter per client IP address.
    Tracks request timestamps within a configurable window and purges expired entries.
    """

    def __init__(self, window_seconds: int = 60, max_tracked_keys: int = 10000):
        """
        Initialize the rate limiter.

        Args:
            window_seconds (int): Duration of the sliding window in seconds (default: 60).
            max_tracked_keys (int): Maximum unique keys to retain before pruning stale records.
        """
        self.window_seconds = window_seconds
        self.max_tracked_keys = max_tracked_keys
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str, route_bucket: str, max_requests: int) -> bool:
        """
        Check if an incoming request from a client IP within a route bucket is allowed.

        Args:
            client_ip (str): Client IP address or host string.
            route_bucket (str): Route category identifier (e.g. 'search', 'recommend').
            max_requests (int): Maximum allowed requests within the sliding window.

        Returns:
            bool: True if allowed, False if the client has exceeded the limit.
        """
        now = time.time()
        key = f"{client_ip}:{route_bucket}"
        cutoff = now - self.window_seconds

        # Prune memory if cache exceeds capacity threshold
        if len(self.requests) > self.max_tracked_keys:
            stale_keys = [k for k, v in self.requests.items() if not v or v[-1] < cutoff]
            for sk in stale_keys:
                self.requests.pop(sk, None)

        valid_timestamps = [t for t in self.requests[key] if t > cutoff]

        if len(valid_timestamps) >= max_requests:
            self.requests[key] = valid_timestamps
            return False

        valid_timestamps.append(now)
        self.requests[key] = valid_timestamps
        return True


rate_limiter = InMemoryRateLimiter(window_seconds=60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager that loads pre-trained ML artifacts into memory
    upon server startup and gracefully cleans up resources upon shutdown.

    Args:
        app (FastAPI): The running FastAPI instance.

    Yields:
        None: Yields execution back to the FastAPI runtime.
    """
    global recommender
    logger.info("Initializing Vibelnyc ML Recommender Engine...")
    try:
        recommender = VibeRecommender()
        logger.info("ML Engine loaded and ready for queries.")
    except Exception as e:
        logger.error("Could not load pre-trained models: %s", e)
        logger.warning("Run `python src/train_engine.py` to generate model artifacts.")
        recommender = None
    yield
    logger.info("Shutting down Vibelnyc Server.")


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


@app.middleware("http")
async def security_and_rate_limit_middleware(request: Request, call_next):
    """
    HTTP Middleware enforcing sliding-window client IP rate limiting and
    injecting hardened HTTP security response headers.

    Args:
        request (Request): Incoming HTTP request.
        call_next: Next request handler in the ASGI pipeline.

    Returns:
        Response: HTTP response decorated with security headers or 429 error payload.
    """
    # Allow CORS preflight requests without rate consumption
    if request.method == "OPTIONS":
        return await call_next(request)

    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    elif request.client:
        client_ip = request.client.host
    else:
        client_ip = "unknown"

    path = request.url.path

    # Define rate limit tiers
    if path.startswith("/api/recommend"):
        limit = 30  # 30 requests per minute for recommendation calculation
        bucket = "recommend"
    elif path.startswith("/api/search"):
        limit = 60  # 60 requests per minute for autocomplete searches
        bucket = "search"
    else:
        limit = 120  # 120 requests per minute for general routes
        bucket = "general"

    if not rate_limiter.is_allowed(client_ip, bucket, limit):
        logger.warning("Rate limit exceeded for IP %s on path %s", client_ip, path)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded. Please try again later."},
            headers={"Retry-After": "60"},
        )

    response: Response = await call_next(request)

    # Inject baseline HTTP security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"

    return response


# --- Pydantic Schemas ---
class RecommendRequest(BaseModel):
    """Request payload for track-to-track recommendation with input length constraints."""
    track_name: str = Field(
        ...,
        description="Name of the seed track to match",
        min_length=1,
        max_length=128,
    )
    artist_name: Optional[str] = Field(
        None,
        description="Optional artist name to narrow down seed track",
        max_length=128,
    )
    n_results: int = Field(3, description="Number of recommendations to return", ge=1, le=20)


class MoodRecommendRequest(BaseModel):
    """Request payload for mood archetype recommendation with strict enum validation."""
    mood: Literal["melancholy", "high-energy", "chill", "pop"] = Field(
        ...,
        description="Mood preset: 'melancholy', 'high-energy', 'chill', or 'pop'",
        max_length=32,
    )
    n_results: int = Field(3, description="Number of recommendations to return", ge=1, le=20)


# --- API Routes ---
@app.get("/", tags=["General"])
async def root() -> Dict[str, Any]:
    """
    Root endpoint providing service metadata and API directory links.

    Returns:
        Dict[str, Any]: API name, online status, engine readiness, and endpoint links.
    """
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
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint reporting engine status and indexed track volume.

    Returns:
        Dict[str, Any]: Health status ('healthy'), engine_loaded flag, and total_tracks count.
    """
    return {
        "status": "healthy",
        "engine_loaded": recommender is not None,
        "total_tracks": len(recommender.df) if recommender is not None else 0,
    }


@app.get("/api/search", tags=["Search"])
async def search_tracks(
    q: str = Query(..., min_length=1, max_length=64, description="Track title or artist query for autocomplete"),
    limit: int = Query(5, ge=1, le=20, description="Max results to return"),
) -> Dict[str, Any]:
    """
    Performs fast substring search on track titles and artist names for frontend autocomplete combobox.

    Args:
        q (str): Case-insensitive search query string (max 64 chars).
        limit (int): Maximum number of search candidates to return (1-20).

    Returns:
        Dict[str, Any]: Query metadata and list of matching track items with popularity.

    Raises:
        HTTPException: 503 if ML Engine models are not yet loaded.
    """
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
async def recommend_tracks(payload: RecommendRequest) -> Dict[str, Any]:
    """
    Recommends top N tracks closest in 8D audio feature space to the requested seed track.
    Computes exact cosine similarity and feature deltas for energy, valence, and danceability.

    Args:
        payload (RecommendRequest): Request body containing track_name, artist_name, and n_results.

    Returns:
        Dict[str, Any]: Complete recommendation envelope with seed track, cluster info, and candidate list.

    Raises:
        HTTPException: 503 if models not loaded, 404 if seed track not found, 500 on internal errors.
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
        logger.warning("Seed track lookup failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.exception("Unexpected error occurred in recommend_tracks: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while generating track recommendations.",
        )


@app.post("/api/recommend/mood", tags=["Recommendation"])
async def recommend_mood(payload: MoodRecommendRequest) -> Dict[str, Any]:
    """
    Recommends top tracks matching predefined sonic archetype vectors for
    'melancholy', 'high-energy', 'chill', or 'pop'.

    Args:
        payload (MoodRecommendRequest): Request body containing mood string and n_results.

    Returns:
        Dict[str, Any]: Complete recommendation envelope formatted identically to track recommendations.

    Raises:
        HTTPException: 503 if models not loaded, 400 if mood identifier invalid, 500 on internal errors.
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
        logger.warning("Invalid mood specified: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.exception("Unexpected error occurred in recommend_mood: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while generating mood recommendations.",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
