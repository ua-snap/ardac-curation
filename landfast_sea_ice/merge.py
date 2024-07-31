import re

import rasterio as rio
import xarray as xr
import numpy as np
import pandas as pd
import tqdm
import dask.array as da
from dask.diagnostics import ProgressBar
from datetime import datetime

from eda import list_geotiffs
from config import DAILY_BEAUFORT_DIR, DAILY_CHUKCHI_DIR

# the first step is to list all the GeoTIFFs in the target directory
for target_directory in [DAILY_CHUKCHI_DIR]:

    tiffs_to_merge = list_geotiffs(target_directory)
    # get the projected x and y coordinates from a single geotiff
    with rio.open(tiffs_to_merge[0]) as src:
        cols, rows = np.meshgrid(np.arange(src.width), np.arange(src.height))
        xarr, yarr = rio.transform.xy(src.transform, rows, cols)
        xcoords = xarr[0]
        ycoords = np.array([a[0] for a in yarr])

    # sort GeoTIFFs by date to ensure correct order
    tiffs_to_merge.sort(key=lambda x: re.search(r'(\d{8})', x.name).group(1))

    data_arrays = []
    dates = []

    for file in tqdm.tqdm(tiffs_to_merge):
        with rio.open(file) as src:
            data = src.read(1)
            date = re.search(r'(\d{4})(\d{2})(\d{2})', file.name).groups()
        
        data_arrays.append(da.from_array(data))

        dates.append(datetime(int(date[0]), int(date[1]), int(date[2])))

    # convert the list of data arrays into a stacked 3D numpy array
    slie_data_stack = da.stack(data_arrays, axis=0)
    # convert list of datetime objects to pandas datetime index
    time_index = pd.to_datetime(dates)

    # create the xarray Dataset
    ds = xr.Dataset(
        {
            "slie": (("time", "y", "x"), slie_data_stack)
        },
        coords={
            "time": time_index,
            "y": ycoords,
            "x": xcoords,
        }
    )

    # Define the CRS as EPSG:3338
    crs_dict = {"crs": "EPSG:3338"}
    # Add the CRS as an attribute to the dataset
    ds.attrs.update(crs_dict)
        # Write to a netCDF file using Dask
    with ProgressBar():
        ds.to_netcdf(target_directory/"daily_slie.nc", engine='netcdf4')

    print(f"Created netCDF file in {target_directory}")
