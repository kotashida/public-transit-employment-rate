import requests
import gzip
import shutil
from pathlib import Path
import config
import zipfile
import io

def download_file(url, dest_path):
    if dest_path.exists():
        print(f"File already exists: {dest_path}")
        return

    print(f"Downloading {url}...")
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded to {dest_path}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def main():
    # 1. Download LODES WAC Data (Employment)
    for year in config.YEARS:
        filename = f"{config.STATE}_wac_S000_JT00_{year}.csv.gz"
        url = f"{config.LODES_BASE_URL}/{config.STATE}/wac/{filename}"
        dest = config.DATA_RAW / filename
        download_file(url, dest)

    # 2. Download Geography (Block Groups Shapefile)
    # Using TIGER 2020 Block Groups for WA to match LODES 8 (2020 Geography)
    geo_filename = f"tl_2020_{config.STATE}_bg.zip"
    # FIPS code for WA is 53
    geo_url = "https://www2.census.gov/geo/tiger/TIGER2020/BG/tl_2020_53_bg.zip"
    geo_dest = config.DATA_RAW / geo_filename
    download_file(geo_url, geo_dest)
    
    # Extract Shapefile
    extract_dir = config.DATA_RAW / "shapefiles"
    if not extract_dir.exists():
        print("Extracting shapefile...")
        try:
            with zipfile.ZipFile(geo_dest, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        except Exception as e:
            print(f"Error extracting shapefile: {e}")

if __name__ == "__main__":
    main()
