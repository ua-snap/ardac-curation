"""Exploratory data analysis utilities for Einhorn/Mahoney 2024 Landfast Sea Ice Data."""

import os
import random
import re
from datetime import datetime

import numpy as np
import rasterio as rio
import matplotlib.pyplot as plt

from luts import pixel_values, daily_slie_norm, daily_slie_cmap, mmm_cmap


def list_geotiffs(directory, str_to_match=None):
    """List GeoTIFF files in a directory.

    Args:
        directory (pathlib.PosixPath): The directory to search for GeoTIFF files.
        str_to_match (str, optional): A string to match in the file name. Defaults to None.
    Returns:
        list: A list of GeoTIFF files in the directory.
    """
    geotiffs = [f for f in directory.glob("*.tif")]
    if str_to_match:
        geotiffs = [f for f in geotiffs if str_to_match in f.name]
    return geotiffs


def inspect_random_sample_metadata(directory):
    """Inspect metadata of a random GeoTIFF file in a directory.

    Args:
        directory (pathlib.PosixPath): The directory containing GeoTIFF files.
    Returns:
        None
    """
    geotiffs = list_geotiffs(directory)
    random_geotiff = random.choice(geotiffs)
    with rio.open(os.path.join(directory, random_geotiff)) as src:
        print(src.profile)


def fetch_all_geotiff_metadata(directory, str_to_match=None):
    """Fetch metadata of all GeoTIFF files in a directory.

    Args:
        directory (pathlib.PosixPath): The directory containing GeoTIFF files.
        str_to_match (str, optional): A string to match in the file name. Defaults to None.
    Returns:
        tuple: A tuple containing a list of GeoTIFF file names and a list of metadata objects.
    """
    geotiffs = list_geotiffs(directory, str_to_match)
    geotiff_meta = []
    filenames = []
    for geotiff in geotiffs:
        filenames.append(geotiff)
        with rio.open(geotiff) as src:
            geotiff_meta.append(src.profile)
    return filenames, geotiff_meta


def test_geotiff_metadata_for_conformity(
    directory, geotiff_metadata=None, str_to_match=None
):
    """Test metadata of GeoTIFF files in a directory for conformity.
    Args:
        directory (pathlib.PosixPath): The directory containing GeoTIFF files.
        geotiff_metadata (tuple, optional): A tuple containing a list of GeoTIFF file names and a list of metadata objects. Defaults to None.
        str_to_match (str, optional): A string to match in the file name. Defaults to None.
    Returns:
        dict: A dictionary of metadata objects that do not conform to the random metadata object using the filename as the key.
    """
    if geotiff_metadata is None:
        filenames, meta = fetch_all_geotiff_metadata(directory, str_to_match)
    else:
        filenames, meta = geotiff_metadata

    random_meta = random.choice(meta)

    # create dict of metadata objects that do not conform to the random metadata object using the filename as the key
    noncoforming_meta = {
        filenames[i]: meta[i] for i in range(len(meta)) if meta[i] != random_meta
    }
    if noncoforming_meta not in [{}]:
        print("Nonconforming metadata found:")
        for k, v in noncoforming_meta.items():
            print(f"{k}: {v}")
        return noncoforming_meta
    else:
        print(f"All GeoTIFF metadata in {directory} is identical.")
        return None


def get_geotiff_unique_value_counts(fp):
    """Get unique values and their counts from a GeoTIFF file.
    Args:
        fp (pathlib.PosixPath): The path to the GeoTIFF file.
    Returns:
        tuple: A tuple containing a numpy array of unique values and a numpy array of their counts.
    """
    with rio.open(fp) as src:
        return np.unique(src.read(1), return_counts=True)


def validate_values(fp, expected_values):
    """Validate that a GeoTIFF contains only expected values.
    Args:
        fp (pathlib.PosixPath): The path to the GeoTIFF file.
        expected_values (list): A list of expected values.
    Returns:
        bool: True if the array contains only expected values, False otherwise."""
    with rio.open(fp) as src:
        array = src.read(1)
        if not np.isin(array, expected_values).all():
            return False
        else:
            return True


def plot_random_sample(directory):
    """Plot a single random sample of a GeoTIFF file from a directory.

    Args:
        directory (pathlib.PosixPath): The directory containing GeoTIFF files.
    Returns:
        None
    """
    geotiffs = list_geotiffs(directory)
    random_geotiff = random.choice(geotiffs)
    with rio.open(random_geotiff) as src:
        plt.figure(figsize=(10, 5))
        plt.imshow(src.read(1), cmap=mmm_cmap, interpolation="none")
        plt.colorbar()
        plt.title(random_geotiff.name)
        plt.show()


def get_dates(target_directory):
    dates = []
    geotiffs = list_geotiffs(target_directory, "dailyslie")

    for file in geotiffs:
        date = re.search(r"(\d{4})(\d{2})(\d{2})", file.name).groups()
        dates.append(datetime(int(date[0]), int(date[1]), int(date[2])))
    return dates


def plot_daily_slie_array(arr_to_plot):
    fig, ax = plt.subplots()
    cax = ax.imshow(arr_to_plot, cmap=daily_slie_cmap, norm=daily_slie_norm)
    cbar = fig.colorbar(cax, ticks=list(pixel_values.keys()), orientation="vertical")
    cbar.set_ticklabels(list(pixel_values.values()))
    plt.show()
