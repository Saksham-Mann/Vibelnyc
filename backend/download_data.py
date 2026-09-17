"""
Spotify Tracks Dataset Downloader.
Downloads the dataset using kagglehub and saves it directly into backend/data/spotify_tracks.csv.
Credits: Maharshi Pandya on Kaggle.
"""

import os
import shutil
from pathlib import Path
import kagglehub


def main() -> None:
    """
    Downloads the latest version of 'maharshipandya/-spotify-tracks-dataset' from KaggleHub
    and copies the CSV file to backend/data/spotify_tracks.csv.

    Returns:
        None
    """
    print("Downloading dataset 'maharshipandya/-spotify-tracks-dataset' via kagglehub...")
    download_path = kagglehub.dataset_download("maharshipandya/-spotify-tracks-dataset")
    print(f"Dataset downloaded to cache at: {download_path}")

    # Destination data directory
    target_dir = Path(__file__).parent / "data"
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"Copying dataset files to: {target_dir}...")
    source_dir = Path(download_path)
    copied_files = []

    for item in source_dir.iterdir():
        if item.is_file():
            # Save canonical file as spotify_tracks.csv
            dest_name = "spotify_tracks.csv" if item.name == "dataset.csv" else item.name
            dest = target_dir / dest_name
            shutil.copy2(item, dest)
            size_mb = item.stat().st_size / (1024 * 1024)
            copied_files.append((dest_name, f"{size_mb:.2f} MB"))
            print(f" -> Copied {dest_name} ({size_mb:.2f} MB)")
        elif item.is_dir():
            dest = target_dir / item.name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
            copied_files.append((item.name, "directory"))
            print(f" -> Copied directory {item.name}")

    print("\nDataset ready in backend/data:")
    for fname, size in copied_files:
        print(f" - {fname} ({size})")


if __name__ == "__main__":
    main()
