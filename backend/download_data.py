"""
Spotify Tracks Dataset Downloader
Downloads the dataset using kagglehub and saves it into backend/data/
"""

import os
import shutil
from pathlib import Path
import kagglehub

def main():
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
        dest = target_dir / item.name
        if item.is_file():
            shutil.copy2(item, dest)
            size_mb = item.stat().st_size / (1024 * 1024)
            copied_files.append((item.name, f"{size_mb:.2f} MB"))
            print(f" -> Copied {item.name} ({size_mb:.2f} MB)")
        elif item.is_dir():
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
