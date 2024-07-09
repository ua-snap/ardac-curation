"""Exploratory data analysis utilities for Einhorn/Mahoney 2024 Landfast Sea Ice Data."""
import os
import random
from pathlib import Path

import numpy as np
import rasterio as rio
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd

from luts import data_sources, pixel_values

# for MMM data
colors = [
    [255, 255, 255],  # 0: non-fast ice or ocean (white)
    [204, 204, 255],  # 1: maximum fast ice extent (light blue)
    [102, 102, 255],  # 2: median fast ice extent (mid-blue)
    [0, 0, 255],      # 3: minimum fast ice extent (dark blue)
    [0, 0, 0],        # 4: mean fast ice edge (black)
    [204, 230, 204],  # 5: land (pale green)
    [230, 230, 230],  # 6: out of domain (light gray)
    [191, 212, 212]   # 7: shadow zone (gray-green)
]
# Normalize the RGB values to the range [0, 1] as required by Matplotlib
colors_normalized = [(r/255, g/255, b/255) for r, g, b in colors]
mmm_cmap = mcolors.ListedColormap(colors_normalized)

def list_geotiffs(directory, str_to_match=None):
    """Count list of GeoTIFF files in a directory.
    
    Args: 
        directory (pathlib.PosixPath): The directory to search for GeoTIFF files.
    Returns:
        list: A list of GeoTIFF files in the directory.
    """
    geotiffs = [f for f in directory.glob("*.tif")]
    if str_to_match:
        geotiffs = [f for f in geotiffs if str_to_match in f.name]
    return geotiffs


def plot_random_sample(directory):
    """Plot a random sample of GeoTIFF files in a directory."""
    geotiffs = list_geotiffs(directory)
    random_geotiff = random.choice(geotiffs)
    with rio.open(random_geotiff) as src:
        plt.figure(figsize=(10, 5))
        plt.imshow(src.read(1), cmap=mmm_cmap, interpolation="none")
        plt.colorbar()
        plt.title(random_geotiff.name)
        plt.show()


def inspect_geotiff_metadata(directory):
    """Inspect metadata of a random GeoTIFF file in a directory."""
    geotiffs = list_geotiffs(directory)
    random_geotiff = random.choice(geotiffs)
    with rio.open(os.path.join(directory, random_geotiff)) as src:
        print(src.profile)


def fetch_all_geotiff_metadata(directory, str_to_match=None):
    """Fetch metadata of all GeoTIFF files in a directory."""
    geotiffs = list_geotiffs(directory, str_to_match)
    geotiff_meta = []
    filenames = []
    for geotiff in geotiffs:
        filenames.append(geotiff)
        with rio.open(geotiff) as src:
            geotiff_meta.append(src.profile)
    return filenames, geotiff_meta


# choose a random geotiff metadata object and assert all other metadata objects are the same
def test_geotiff_metadata_for_conformity(directory, geotiff_metadata=None, str_to_match=None):
    if geotiff_metadata is None:
        filenames, meta = fetch_all_geotiff_metadata(directory, str_to_match)
    else:
        filenames, meta = geotiff_metadata
    
    random_meta = random.choice(meta)
    
    # create dict of metadata objects that do not conform to the random metadata object using the filename as the key
    noncoforming_meta = {filenames[i]: meta[i] for i in range(len(meta)) if meta[i] != random_meta}

    if noncoforming_meta not in [{}]:
        print("Nonconforming metadata found:")
        for k, v in noncoforming_meta.items():
            print(f"{k}: {v}")
        return noncoforming_meta
    else:
        print("All metadata conforms.")
        return None

def get_geotiff_unique_value_counts(fp):
    with rio.open(fp) as src:
        return np.unique(src.read(1), return_counts=True)


def determine_data_source(fp):
    """Determine the data source of a GeoTIFF file."""
    return data_sources[os.path.basename(fp)[0]]


def describe_in_dataframe(directory):
    geotiffs = list_geotiffs(directory, "daily")
    unique_values = []
    for geotiff in geotiffs:
        unique_values, value_counts = get_geotiff_unique_value_counts(os.path.join(directory, geotiff))
        unique_values.append(get_geotiff_unique_value_counts(os.path.join(directory, geotiff)))
    # file name as the index
    # a column for each unique value with the count as the unique_values as a column
    df = pd.DataFrame(unique_values, index=geotiffs).T
    # add column for data source
    df["data_source"] = df.index.map(determine_data_source)
    return df
