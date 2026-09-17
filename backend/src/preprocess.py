"""
Data preprocessing, cleaning, and normalization pipeline for Vibelnyc audio tracks.
Handles deduplication, missing values, and min-max scaling of continuous audio features.
"""

from pathlib import Path
from typing import Optional, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

RAW_FEATURE_COLS = [
    'danceability',
    'energy',
    'loudness',
    'speechiness',
    'acousticness',
    'instrumentalness',
    'valence',
    'tempo',
]

SCALED_FEATURE_COLS = [
    'danceability',
    'energy',
    'norm_loudness',
    'speechiness',
    'acousticness',
    'instrumentalness',
    'valence',
    'norm_tempo',
]

COLS_TO_SCALE = ['loudness', 'tempo']


def get_default_paths() -> Tuple[Path, Path]:
    """
    Resolves the canonical paths for dataset input and model artifact storage.

    Returns:
        Tuple[Path, Path]: Path to the spotify_tracks.csv dataset and models directory.
    """
    src_dir = Path(__file__).resolve().parent
    backend_dir = src_dir.parent
    csv_path = backend_dir / 'data' / 'spotify_tracks.csv'
    models_dir = backend_dir / 'models'
    return csv_path, models_dir


def preprocess_data(
    csv_path: Optional[Path] = None,
    models_dir: Optional[Path] = None,
    save_artifacts: bool = True,
) -> Tuple[pd.DataFrame, MinMaxScaler]:
    """
    Loads, cleans, and normalizes the Spotify tracks dataset.
    - Drops null rows across essential attributes.
    - Drops duplicate track_id entries.
    - Performs case-insensitive deduplication on (track_name, artists).
    - Fits MinMaxScaler on loudness and tempo to bring all dimensions to [0.0, 1.0].
    - Clips standard unit audio dimensions strictly to [0.0, 1.0].
    - Saves fitted scaler to models/ directory when requested.

    Args:
        csv_path (Optional[Path]): Custom path to raw dataset CSV file.
        models_dir (Optional[Path]): Destination directory for serialized scaler.
        save_artifacts (bool): Whether to persist scaler.joblib to disk.

    Returns:
        Tuple[pd.DataFrame, MinMaxScaler]: Cleaned DataFrame and fitted MinMaxScaler.

    Raises:
        FileNotFoundError: If the source CSV dataset does not exist on disk.
    """
    default_csv, default_models = get_default_paths()
    csv_file = Path(csv_path) if csv_path else default_csv
    target_models_dir = Path(models_dir) if models_dir else default_models

    if not csv_file.exists():
        fallback = csv_file.parent / 'dataset.csv'
        if fallback.exists():
            csv_file = fallback
        else:
            raise FileNotFoundError(f"Spotify dataset not found at {csv_file}")

    print(f"[Preprocessing] Loading dataset from: {csv_file}")
    df = pd.read_csv(csv_file)
    initial_count = len(df)

    # Clean nulls
    essential_cols = ['track_id', 'track_name', 'artists'] + RAW_FEATURE_COLS
    df = df.dropna(subset=essential_cols)

    # Drop duplicates by track_id
    df = df.drop_duplicates(subset=['track_id'])

    # Drop duplicates by track_name and artists (case-insensitive deduplication)
    df['name_artist_key'] = (
        df['track_name'].str.lower().str.strip()
        + '||'
        + df['artists'].str.lower().str.strip()
    )
    df = df.drop_duplicates(subset=['name_artist_key'])
    df = df.drop(columns=['name_artist_key'])

    # Ensure native bounded audio dimensions are strictly in [0.0, 1.0]
    unit_cols = [
        'danceability',
        'energy',
        'speechiness',
        'acousticness',
        'instrumentalness',
        'valence',
    ]
    for col in unit_cols:
        df[col] = df[col].astype(float).clip(lower=0.0, upper=1.0)

    # Fit MinMaxScaler strictly for loudness and tempo
    scaler = MinMaxScaler(feature_range=(0.0, 1.0))
    scaled_vals = scaler.fit_transform(df[COLS_TO_SCALE])
    df['norm_loudness'] = scaled_vals[:, 0].clip(0.0, 1.0)
    df['norm_tempo'] = scaled_vals[:, 1].clip(0.0, 1.0)

    # Reset index for continuous row mapping
    df = df.reset_index(drop=True)

    print(
        f"[Preprocessing] Cleaned {initial_count:,} tracks -> {len(df):,} unique tracks."
    )

    if save_artifacts:
        target_models_dir.mkdir(parents=True, exist_ok=True)
        scaler_path = target_models_dir / 'scaler.joblib'
        joblib.dump(scaler, scaler_path)
        print(f"[Preprocessing] Scaler saved to: {scaler_path}")

    return df, scaler


def extract_feature_vector(
    track_row: pd.Series,
) -> np.ndarray:
    """
    Extracts the 8-dimensional normalized feature vector for a given track row.

    Args:
        track_row (pd.Series): Single track record containing scaled audio columns.

    Returns:
        np.ndarray: 1D float64 array representing the track in 8D audio space.
    """
    return track_row[SCALED_FEATURE_COLS].values.astype(np.float64)


if __name__ == '__main__':
    df, scaler = preprocess_data()
    print("Preprocessing test completed successfully.")
