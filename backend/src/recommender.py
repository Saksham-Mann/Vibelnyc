"""
Inference engine for Vibelnyc recommendations.
Provides track-to-track similarity search, mood preset matching, and autocomplete.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler

from preprocess import (
    RAW_FEATURE_COLS,
    SCALED_FEATURE_COLS,
    get_default_paths,
)

MOOD_PRESETS: Dict[str, Dict[str, float]] = {
    'melancholy': {
        'valence': 0.15,
        'energy': 0.30,
        'acousticness': 0.70,
        'danceability': 0.40,
        'norm_loudness': 0.35,
        'speechiness': 0.04,
        'instrumentalness': 0.25,
        'norm_tempo': 0.35,
    },
    'high-energy': {
        'valence': 0.80,
        'energy': 0.90,
        'danceability': 0.80,
        'acousticness': 0.10,
        'norm_loudness': 0.85,
        'speechiness': 0.08,
        'instrumentalness': 0.05,
        'norm_tempo': 0.70,
    },
    'chill': {
        'valence': 0.50,
        'energy': 0.30,
        'acousticness': 0.80,
        'danceability': 0.50,
        'norm_loudness': 0.45,
        'speechiness': 0.04,
        'instrumentalness': 0.40,
        'norm_tempo': 0.40,
    },
    'pop': {
        'valence': 0.85,
        'energy': 0.80,
        'danceability': 0.85,
        'acousticness': 0.20,
        'norm_loudness': 0.80,
        'speechiness': 0.07,
        'instrumentalness': 0.02,
        'norm_tempo': 0.60,
    },
}


class VibeRecommender:
    """
    Production recommendation engine caching pre-trained models and feature vectors in memory.
    Supports fast vector cosine similarity, vibe clustering lookup, and popularity-weighted search.
    """

    def __init__(self, models_dir: Optional[Path] = None) -> None:
        """
        Initializes the VibeRecommender instance and loads serialized model artifacts.

        Args:
            models_dir (Optional[Path]): Custom path to folder containing model joblib and parquet files.
        """
        _, default_models = get_default_paths()
        self.models_dir = Path(models_dir) if models_dir else default_models

        self.df: pd.DataFrame = None
        self.scaler: MinMaxScaler = None
        self.nn_model: NearestNeighbors = None
        self.kmeans: KMeans = None
        self.cluster_metadata: Dict[int, Dict[str, Any]] = {}
        self.feature_matrix: np.ndarray = None

        self.load_artifacts()

    def load_artifacts(self) -> None:
        """
        Loads preprocessed parquet dataset, MinMaxScaler, NearestNeighbors model,
        KMeans model, and cluster metadata into memory.

        Raises:
            FileNotFoundError: If required model artifacts are missing from the models directory.
        """
        parquet_path = self.models_dir / 'processed_tracks.parquet'
        scaler_path = self.models_dir / 'scaler.joblib'
        nn_path = self.models_dir / 'nearest_neighbors.joblib'
        kmeans_path = self.models_dir / 'kmeans.joblib'
        meta_path = self.models_dir / 'cluster_metadata.json'

        if not (parquet_path.exists() and nn_path.exists() and kmeans_path.exists()):
            raise FileNotFoundError(
                f"Trained models not found in {self.models_dir}. "
                "Run `python src/train_engine.py` to train and generate artifacts."
            )

        print(f"[Recommender] Loading processed dataset from: {parquet_path}")
        self.df = pd.read_parquet(parquet_path)
        self.feature_matrix = self.df[SCALED_FEATURE_COLS].values.astype(np.float64)

        print("[Recommender] Loading models (scaler, nearest_neighbors, kmeans)...")
        self.scaler = joblib.load(scaler_path)
        self.nn_model = joblib.load(nn_path)
        self.kmeans = joblib.load(kmeans_path)

        if meta_path.exists():
            with open(meta_path, 'r', encoding='utf-8') as f:
                raw_meta = json.load(f)
                self.cluster_metadata = {int(k): v for k, v in raw_meta.items()}

        print(f"[Recommender] Initialized with {len(self.df):,} tracks ready for inference.")

    def search_tracks(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Performs fast autocomplete search for track titles and artists,
        prioritizing more popular songs.

        Args:
            query (str): Substring search text entered by the user.
            limit (int): Maximum number of search candidates to return.

        Returns:
            List[Dict[str, Any]]: List of matching tracks with track_id, track_name, artists, and popularity.
        """
        if not query or not query.strip():
            return []

        q = query.strip().lower()
        mask = (
            self.df['track_name'].str.lower().str.contains(q, na=False, regex=False)
            | self.df['artists'].str.lower().str.contains(q, na=False, regex=False)
        )
        matches = self.df[mask]

        if matches.empty:
            return []

        sorted_matches = matches.sort_values(by='popularity', ascending=False).head(limit)

        results = []
        for _, row in sorted_matches.iterrows():
            results.append({
                'track_id': str(row['track_id']),
                'track_name': str(row['track_name']),
                'artists': str(row['artists']),
                'album_name': str(row.get('album_name', '')),
                'popularity': int(row.get('popularity', 0)),
            })
        return results

    def find_seed_track(
        self,
        track_name: str,
        artist_name: Optional[str] = None,
    ) -> Optional[pd.Series]:
        """
        Locates the best candidate seed track record in the dataset using exact or fuzzy title matching.

        Args:
            track_name (str): Title of the song to search for.
            artist_name (Optional[str]): Optional artist name to disambiguate identical titles.

        Returns:
            Optional[pd.Series]: Matched track row from the DataFrame or None if not found.
        """
        t_clean = track_name.strip().lower()

        if artist_name and artist_name.strip():
            a_clean = artist_name.strip().lower()
            match = self.df[
                (self.df['track_name'].str.lower() == t_clean)
                & (self.df['artists'].str.lower().str.contains(a_clean, na=False, regex=False))
            ]
            if not match.empty:
                return match.sort_values(by='popularity', ascending=False).iloc[0]

        # Exact title match
        match = self.df[self.df['track_name'].str.lower() == t_clean]
        if not match.empty:
            return match.sort_values(by='popularity', ascending=False).iloc[0]

        # Fallback to substring title match
        match = self.df[self.df['track_name'].str.lower().str.contains(t_clean, na=False, regex=False)]
        if not match.empty:
            return match.sort_values(by='popularity', ascending=False).iloc[0]

        return None

    def _format_track_features(self, row: pd.Series) -> Dict[str, Any]:
        """
        Extracts and converts audio dimensions to standardized percentage scale (0-100) for frontend rendering.

        Args:
            row (pd.Series): DataFrame row containing raw acoustic features.

        Returns:
            Dict[str, Any]: Formatted dictionary containing energy, valence, danceability, and tempo.
        """
        return {
            'energy': round(float(row['energy']) * 100, 1),
            'valence': round(float(row['valence']) * 100, 1),
            'danceability': round(float(row['danceability']) * 100, 1),
            'acousticness': round(float(row['acousticness']) * 100, 1),
            'tempo': round(float(row['tempo']), 1),
            'loudness': round(float(row['loudness']), 1),
        }

    def recommend_by_track(
        self,
        track_name: str,
        artist_name: Optional[str] = None,
        n_results: int = 3,
    ) -> Dict[str, Any]:
        """
        Recommends candidate tracks matching the 8D audio profile of a seed track.
        Computes cosine similarity percentage and feature deltas.

        Args:
            track_name (str): Title of the seed track.
            artist_name (Optional[str]): Optional artist name.
            n_results (int): Number of top recommendations to return.

        Returns:
            Dict[str, Any]: Dictionary containing seed_track details, cluster_info, and recommendations list.

        Raises:
            ValueError: If the seed track cannot be found in the dataset.
        """
        seed_row = self.find_seed_track(track_name, artist_name)
        if seed_row is None:
            raise ValueError(
                f"Track '{track_name}'"
                + (f" by '{artist_name}'" if artist_name else "")
                + " was not found in the dataset."
            )

        seed_vector = seed_row[SCALED_FEATURE_COLS].values.astype(np.float64).reshape(1, -1)
        seed_cluster_id = int(seed_row['cluster_id'])
        cluster_name = self.cluster_metadata.get(seed_cluster_id, {}).get(
            'name', f"Cluster #{seed_cluster_id:02d}"
        )

        k_lookup = min(n_results + 10, len(self.df))
        distances, indices = self.nn_model.kneighbors(seed_vector, n_neighbors=k_lookup)

        seed_track_id = str(seed_row['track_id'])
        seed_features = self._format_track_features(seed_row)

        recommendations: List[Dict[str, Any]] = []
        for dist, idx in zip(distances[0], indices[0]):
            cand_row = self.df.iloc[idx]
            cand_track_id = str(cand_row['track_id'])

            if cand_track_id == seed_track_id:
                continue

            similarity_percentage = round((1.0 - float(dist)) * 100, 1)
            cand_features = self._format_track_features(cand_row)

            deltas = {
                'energy': round(cand_features['energy'] - seed_features['energy'], 1),
                'valence': round(cand_features['valence'] - seed_features['valence'], 1),
                'danceability': round(cand_features['danceability'] - seed_features['danceability'], 1),
            }

            recommendations.append({
                'track_name': str(cand_row['track_name']),
                'artist': str(cand_row['artists']),
                'spotify_id': cand_track_id,
                'match_percentage': similarity_percentage,
                'cluster_id': int(cand_row['cluster_id']),
                'cluster_name': str(cand_row.get('cluster_name', '')),
                'features': cand_features,
                'deltas': deltas,
            })

            if len(recommendations) >= n_results:
                break

        return {
            'seed_track': {
                'track_name': str(seed_row['track_name']),
                'artist': str(seed_row['artists']),
                'spotify_id': seed_track_id,
                'cluster_id': seed_cluster_id,
                'raw_features': seed_features,
            },
            'cluster_info': {
                'cluster_id': seed_cluster_id,
                'cluster_name': cluster_name,
            },
            'recommendations': recommendations,
        }

    def recommend_by_mood(
        self,
        mood: str,
        n_results: int = 3,
    ) -> Dict[str, Any]:
        """
        Recommends tracks matching a predefined mood archetype vector
        ('melancholy', 'high-energy', 'chill', 'pop').

        Args:
            mood (str): Mood preset key.
            n_results (int): Number of top candidate recommendations to return.

        Returns:
            Dict[str, Any]: Dictionary containing archetype seed_track, cluster_info, and recommendations.

        Raises:
            ValueError: If the mood key is not recognized in MOOD_PRESETS.
        """
        m_key = mood.strip().lower().replace('_', '-')
        if m_key not in MOOD_PRESETS:
            raise ValueError(
                f"Unknown mood '{mood}'. Available presets: {list(MOOD_PRESETS.keys())}"
            )

        preset_dict = MOOD_PRESETS[m_key]
        vector = np.array([preset_dict[col] for col in SCALED_FEATURE_COLS], dtype=np.float64).reshape(1, -1)

        cluster_id = int(self.kmeans.predict(vector)[0])
        cluster_name = self.cluster_metadata.get(cluster_id, {}).get(
            'name', f"Cluster #{cluster_id:02d}"
        )

        archetype_features = {
            'energy': round(preset_dict['energy'] * 100, 1),
            'valence': round(preset_dict['valence'] * 100, 1),
            'danceability': round(preset_dict['danceability'] * 100, 1),
            'acousticness': round(preset_dict['acousticness'] * 100, 1),
            'tempo': 120.0,
            'loudness': -8.0,
        }

        distances, indices = self.nn_model.kneighbors(vector, n_neighbors=n_results)

        recommendations: List[Dict[str, Any]] = []
        for dist, idx in zip(distances[0], indices[0]):
            cand_row = self.df.iloc[idx]
            similarity_percentage = round((1.0 - float(dist)) * 100, 1)
            cand_features = self._format_track_features(cand_row)

            deltas = {
                'energy': round(cand_features['energy'] - archetype_features['energy'], 1),
                'valence': round(cand_features['valence'] - archetype_features['valence'], 1),
                'danceability': round(cand_features['danceability'] - archetype_features['danceability'], 1),
            }

            recommendations.append({
                'track_name': str(cand_row['track_name']),
                'artist': str(cand_row['artists']),
                'spotify_id': str(cand_row['track_id']),
                'match_percentage': similarity_percentage,
                'cluster_id': int(cand_row['cluster_id']),
                'cluster_name': str(cand_row.get('cluster_name', '')),
                'features': cand_features,
                'deltas': deltas,
            })

        return {
            'seed_track': {
                'track_name': f"Mood Preset: {mood.replace('-', ' ').title()}",
                'artist': "Vibelnyc Sonic Archetype",
                'spotify_id': f"mood-{m_key}",
                'cluster_id': cluster_id,
                'raw_features': archetype_features,
            },
            'cluster_info': {
                'cluster_id': cluster_id,
                'cluster_name': cluster_name,
            },
            'recommendations': recommendations,
        }
