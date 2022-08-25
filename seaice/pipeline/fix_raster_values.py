"""Map and consolidate raster values to a 0 to 255 range."""

import argparse
import pickle
import numpy as np
import rasterio as rio
from pathlib import Path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Execute raster value correction."
    )
    parser.add_argument(
        "-d",
        "--data-file",
        action="store",
        dest="data_fp",
        type=str,
    )
    parser.add_argument(
        "-p",
        "--profile",
        action="store",
        dest="profile",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        action="store",
        dest="out_dir",
        type=str,
    )
    args = parser.parse_args()
    fp = Path(args.data_fp)
    profile = args.profile
    out_dir = Path(args.out_dir)
    
    """Writes a GeoTIFF of conditionally set 0 or 1 values"""
    
    with open(profile, 'rb') as handle:
        profile = pickle.load(handle)
    
    with rio.open(fp) as src:
        arr = src.read(1)
    
    arr[arr != 255] = 0
    arr[arr == 255] = 1
    
    arrfix_fp = out_dir.joinpath(f"arrfix_{fp.name}")
    
    with rio.open(arrfix_fp, 'w', **profile) as dst:
        dst.write(arr, 1)
    
    print(f"Results written to {arrfix_fp}")
    