"""
Security Audit Verification Suite for Vibelnyc Backend & ML Engine
Tests input bounds, deserialization checksum verification, rate limiting, and opaque error responses.
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient

from main import app, rate_limiter
from recommender import VibeRecommender, compute_sha256

client = TestClient(app)


def test_security_headers(client: TestClient):
    """Verify standard HTTP security headers are injected into API responses."""
    response = client.get("/health")
    assert response.status_code == 200
    headers = response.headers
    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") == "DENY"
    assert "max-age=" in headers.get("strict-transport-security", "")
    assert headers.get("referrer-policy") == "strict-origin-when-cross-origin"
    print("[PASS] Security headers verified.")


def test_input_validation_search(client: TestClient):
    """Verify input length bounds on search endpoint."""
    # 1. Valid short query
    res = client.get("/api/search?q=radiohead")
    assert res.status_code == 200
    data = res.json()
    assert "results" in data

    # 2. Oversized query (> 64 characters)
    oversized = "a" * 65
    res_oversized = client.get(f"/api/search?q={oversized}")
    assert res_oversized.status_code == 422
    print("[PASS] Search query bounds verified (rejects > 64 chars).")


def test_input_validation_recommend(client: TestClient):
    """Verify input length bounds on track recommendation endpoint."""
    # 1. Oversized track name (> 128 characters)
    oversized_track = "x" * 129
    res = client.post("/api/recommend", json={"track_name": oversized_track, "n_results": 3})
    assert res.status_code == 422

    # 2. Oversized artist name (> 128 characters)
    res_artist = client.post("/api/recommend", json={"track_name": "Creep", "artist_name": "x" * 129})
    assert res_artist.status_code == 422

    # 3. Non-existent track returns 404
    res_404 = client.post("/api/recommend", json={"track_name": "NonExistentTrack12345XYZ", "n_results": 3})
    assert res_404.status_code == 404
    print("[PASS] Track recommendation bounds and 404 handling verified.")


def test_input_validation_mood(client: TestClient):
    """Verify strict enum validation on mood recommendation endpoint."""
    # 1. Valid mood
    res_valid = client.post("/api/recommend/mood", json={"mood": "chill", "n_results": 2})
    assert res_valid.status_code == 200
    assert len(res_valid.json()["recommendations"]) == 2

    # 2. Invalid mood
    res_invalid = client.post("/api/recommend/mood", json={"mood": "rage-core-metal", "n_results": 2})
    assert res_invalid.status_code == 422
    print("[PASS] Mood enum validation verified (rejects arbitrary strings).")


def test_rate_limiting(client: TestClient):
    """Verify in-memory sliding window rate limiter returns 429 when threshold exceeded."""
    # Reset limiter for clean testing
    rate_limiter.requests.clear()

    # Route limit for /api/recommend is 30 requests per minute
    # Send 31 requests with the same simulated client
    blocked = False
    for i in range(32):
        res = client.post(
            "/api/recommend/mood",
            json={"mood": "pop", "n_results": 1},
            headers={"x-forwarded-for": "192.168.1.50"}
        )
        if res.status_code == 429:
            blocked = True
            break

    assert blocked, "Expected rate limiter to return 429 after exceeding limit."
    print("[PASS] Rate limiting verified (429 Too Many Requests enforced).")


def test_tampered_model_artifact_detection():
    """Verify that tampering with an artifact or checksum triggers security rejection."""
    models_dir = Path(__file__).resolve().parent / "models"
    checksums_file = models_dir / "checksums.json"
    assert checksums_file.exists()

    with open(checksums_file, "r") as f:
        original_checksums = json.load(f)

    # Create temporary copy of models dir
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_models_path = Path(tmpdir)
        for item in models_dir.iterdir():
            if item.is_file():
                shutil.copy(item, tmp_models_path / item.name)

        # Tamper with one file
        tampered_file = tmp_models_path / "scaler.joblib"
        with open(tampered_file, "ab") as f:
            f.write(b"MALICIOUS_APPENDED_BYTECODE")

        # Attempt to load using VibeRecommender
        recommender = VibeRecommender.__new__(VibeRecommender)
        recommender.models_dir = tmp_models_path

        tamper_detected = False
        try:
            recommender.load_artifacts()
        except RuntimeError as e:
            if "integrity verification failed" in str(e).lower():
                tamper_detected = True

        assert tamper_detected, "Tampered artifact was loaded without detecting checksum mismatch!"
        print("[PASS] ML Artifact tamper detection verified (RuntimeError on modified byte content).")


def run_all_tests():
    with TestClient(app) as client:
        print("Running Vibelnyc Security Audit Test Suite...")
        test_security_headers(client)
        test_input_validation_search(client)
        test_input_validation_recommend(client)
        test_input_validation_mood(client)
        test_rate_limiting(client)
        test_tampered_model_artifact_detection()
        print("\nAll security tests passed successfully!")


if __name__ == "__main__":
    run_all_tests()
