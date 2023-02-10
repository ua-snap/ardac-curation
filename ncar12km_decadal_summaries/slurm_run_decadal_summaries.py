import argparse
import glob
import xarray as xr
import numpy as np
import rasterio as rio
import pickle

# import logging
import warnings
from pathlib import Path
from wrf_raster_profile import create_wrf_raster_profile
from generate_decadal_summaries import create_decadal_averages
import dask.distributed
from dask_jobqueue import SLURMCluster
from config import (
    mo_names,
    months,
    unit_di,
    summary_di,
    variable_di,
    precision_di,
    target_dirs,
)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", help="directory to save output GeoTIFF files")
    args = parser.parse_args()

    client = dask.distributed.Client(n_workers=32)
    for target in target_dirs:
        create_decadal_averages(target, output_dir=args.output_dir, dry_run=False)
    client.close()
