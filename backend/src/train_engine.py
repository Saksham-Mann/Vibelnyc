"""
Model training and artifact persistence engine for Vibelnyc.
Trains NearestNeighbors for cosine similarity and KMeans for vibe clustering.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors

from preprocess import (
    SCALED_FEATURE_COLS,
    get_default_paths,
    preprocess_data,
)


def derive_cluster_names(
    kmeans: KMeans,
    feature_cols: List[str],
) -> Dict[int, Dict[str, Any]]:
    """
    Analyzes KMeans cluster centroids to assign intuitive, human-readable vibe labels
    and descriptive text based on relative levels of energy, valence, and acousticness.

    Args:
        kmeans (KMeans): Fitted KMeans clustering model.
        feature_cols (List[str]): List of normalized feature column names.

    Returns:
        Dict[int, Dict[str, Any]]: Mapping of cluster IDs to dictionary containing
            'name', 'description', and centroid coordinate attributes.
    """
    centroids = kmeans.cluster_centers_
    cluster_meta: Dict[int, Dict[str, Any]] = {}

    for idx, center in enumerate(centroids):
        c_dict = dict(zip(feature_cols, center))
        energy = c_dict.get('energy', 0.5)
        valence = c_dict.get('valence', 0.5)
        acoustic = c_dict.get('acousticness', 0.5)
        dance = c_dict.get('danceability', 0.5)
        instrumental = c_dict.get('instrumentalness', 0.5)

        if instrumental > 0.5:
            name = "Deep Focus & Ambient"
            desc = "Atmospheric, instrumental soundscapes and contemplative textures."
        elif energy > 0.75 and dance > 0.7:
            name = "High Energy Club & Dance"
            desc = "Peak-time electronic, upbeat dance, and pulse-raising rhythms."
        elif energy > 0.7 and valence > 0.6:
            name = "Mainstream Pop & Anthems"
            desc = "Euphoric, feel-good hits with bright melodies and infectious hooks."
        elif acoustic > 0.65 and energy < 0.4:
            name = "Acoustic Lo-Fi & Coffeehouse"
            desc = "Warm analog acoustics, gentle organic instrumentation, and chill warmth."
        elif valence < 0.35 and energy < 0.45:
            name = "Late Night Melancholic"
            desc = "Brooding, nocturnal, emotionally raw tracks for introspective hours."
        elif dance > 0.6 and energy < 0.6:
            name = "Chill Downtempo & Groove"
            desc = "Relaxed beats, smooth basslines, and effortless melodic flow."
        elif energy > 0.6:
            name = "Dynamic Indie & Alternative"
            desc = "Electric guitars, bold dynamics, and rhythmic indie vibrations."
        else:
            name = "Atmospheric Eclectic"
            desc = "Balanced sonic profile with multifaceted harmonic depth."

        cluster_meta[idx] = {
            "name": name,
            "description": desc,
            "centroid_energy": round(float(energy), 3),
            "centroid_valence": round(float(valence), 3),
            "centroid_danceability": round(float(dance), 3),
            "centroid_acousticness": round(float(acoustic), 3),
        }

    return cluster_meta


def train_and_persist_models(
    csv_path: Optional[Path] = None,
    models_dir: Optional[Path] = None,
) -> None:
    """
    Executes the end-to-end unsupervised training pipeline:
    1. Preprocesses and deduplicates raw tracks via preprocess_data.
    2. Trains brute-force NearestNeighbors using cosine metric for exact similarity.
    3. Segments the audio space into 8 vibe clusters using KMeans.
    4. Computes centroid metadata and assigns human-readable cluster labels.
    5. Serializes models, scaler, cluster metadata, and Parquet data store.

    Args:
        csv_path (Optional[Path]): Optional path to input dataset CSV file.
        models_dir (Optional[Path]): Destination directory to store trained models.

    Returns:
        None
    """
    default_csv, default_models = get_default_paths()
    models_target = Path(models_dir) if models_dir else default_models
    models_target.mkdir(parents=True, exist_ok=True)

    print("==================================================")
    print("        VIBELNYC ML ENGINE - TRAINING PIPELINE   ")
    print("==================================================")

    # 1. Preprocess Data
    df, scaler = preprocess_data(csv_path=csv_path, models_dir=models_target)
    X = df[SCALED_FEATURE_COLS].values.astype(np.float64)

    # 2. Train NearestNeighbors
    print("\n[Training] Fitting NearestNeighbors (metric='cosine', algorithm='brute')...")
    nn_model = NearestNeighbors(
        n_neighbors=25,
        metric='cosine',
        algorithm='brute',
        n_jobs=-1,
    )
    nn_model.fit(X)
    nn_path = models_target / 'nearest_neighbors.joblib'
    joblib.dump(nn_model, nn_path)
    print(f" -> NearestNeighbors saved to: {nn_path}")

    # 3. Train KMeans Clustering
    print("\n[Training] Fitting KMeans (k=8 vibe clusters, random_state=42)...")
    kmeans = KMeans(
        n_clusters=8,
        random_state=42,
        n_init=10,
        max_iter=300,
    )
    cluster_labels = kmeans.fit_predict(X)
    df['cluster_id'] = cluster_labels

    kmeans_path = models_target / 'kmeans.joblib'
    joblib.dump(kmeans, kmeans_path)
    print(f" -> KMeans model saved to: {kmeans_path}")

    # 4. Derive and save Cluster Names & Metadata
    cluster_metadata = derive_cluster_names(kmeans, SCALED_FEATURE_COLS)
    df['cluster_name'] = df['cluster_id'].map(
        lambda cid: cluster_metadata[cid]['name']
    )

    meta_path = models_target / 'cluster_metadata.json'
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(cluster_metadata, f, indent=2)
    print(f" -> Cluster metadata saved to: {meta_path}")

    # 5. Persist Processed DataFrame as Parquet
    parquet_path = models_target / 'processed_tracks.parquet'
    print(f"\n[Export] Saving {len(df):,} processed tracks to: {parquet_path}")
    df.to_parquet(parquet_path, engine='pyarrow', index=False)
    print(" -> Processed tracks Parquet saved successfully.")

    # 6. Compute Cryptographic SHA-256 Checksums for Integrity Verification
    import hashlib

    artifacts_to_hash = [
        'scaler.joblib',
        'nearest_neighbors.joblib',
        'kmeans.joblib',
        'processed_tracks.parquet',
        'cluster_metadata.json',
    ]

    checksums = {}
    for filename in artifacts_to_hash:
        target_file = models_target / filename
        if target_file.exists():
            hasher = hashlib.sha256()
            with open(target_file, 'rb') as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            checksums[filename] = hasher.hexdigest()

    checksum_path = models_target / 'checksums.json'
    with open(checksum_path, 'w', encoding='utf-8') as f:
        json.dump(checksums, f, indent=2)
    print(f" -> Artifact checksums saved to: {checksum_path}")

    print("\n[Summary] Vibelnyc model training completed successfully!")
    print(f"Artifacts generated in: {models_target}")


if __name__ == '__main__':
    train_and_persist_models()
