import re
import time
from datetime import datetime

import rasterio
import xarray as xr
import rioxarray
import dask
import pandas as pd
import dask.distributed as dd
from dask_jobqueue import SLURMCluster

from eda import list_geotiffs
from config import (
    DAILY_BEAUFORT_DIR,
    BEAUFORT_NETCDF_DIR,
    DAILY_CHUKCHI_DIR,
    CHUKCHI_NETCDF_DIR,
    SCRATCH_DIR,
)
from luts import ice_years


def extract_date_from_filename(geotiff):
    """Extract datetime object from a GeoTIFF filename.

    Args:
        geotiff (str): filename of the GeoTIFF
    Returns:
        date (pd.Timestamp): the date extracted from the filename
    """
    # file names will be like: beaufort_20230726_asip_slie.tif
    date = re.search(r"(\d{4})(\d{2})(\d{2})", geotiff).groups()
    date = datetime(int(date[0]), int(date[1]), int(date[2]))
    return pd.to_datetime(date, format="%Y%m%d")


def select_by_ice_year(geotiff_list, ice_year):
    """Select GeoTIFFs by ice year. An ice year begins in October of one calendar year and ends in July of the following year.

    Args:
        geotiff_list (list): list of GeoTIFF filenames
        ice_year (str): the ice year to select data for, e.g., '2010-11'
    Returns:
        selected_geotiffs (list): list of GeoTIFF filenames for specified ice year
    """
    start_year, _ = ice_year.split("-")
    start_year = int(start_year)
    end_year = start_year + 1
    ice_year_start = datetime(start_year, 10, 1)  # October 1 of start_year
    ice_year_end = datetime(end_year, 7, 31)  # July 31 of end_year

    selected_geotiffs = []

    for geotiff in geotiff_list:
        # geotiff name format like beaufort_20230726_asip_slie.tif
        match = re.search(r"(\d{4})(\d{2})(\d{2})", geotiff.name)
        if match:
            year, month, day = map(int, match.groups())
            file_date = datetime(year, month, day)

            if ice_year_start <= file_date <= ice_year_end:
                selected_geotiffs.append(geotiff)

    return selected_geotiffs


def load_geotiff_as_dataarray(geotiff):
    """Load a GeoTIFF file as a DataArray using rioxarray.

    Args:
        geotiff (pathlib.PosixPath): path to the GeoTIFF file
    Returns:
        xr_da (xarray.DataArray): the GeoTIFF data as an xarray DataArray
    """
    xr_da = rioxarray.open_rasterio(
        geotiff,
        chunks={"x": 4096, "y": 4096},  # chunk size seems OK for t2small
        lock=False,
    )
    # drop the "band" dimension because these are all single band GeoTIFFs
    # rioxarray adds a "band" dimension by default
    xr_da = xr_da.squeeze(drop=True)
    xr_da = xr_da.fillna(111).astype("int16")
    return xr_da


def write_netcdf(dataset, output_nc_file):
    encoding = {"slie": {"dtype": "int16"}}
    dataset.to_netcdf(output_nc_file, encoding=encoding)


if __name__ == "__main__":
    cluster = SLURMCluster(
        cores=24,
        memory="128GB",
        queue="t2small",
        walltime="23:00:00",
        log_directory=SCRATCH_DIR,
        local_directory=SCRATCH_DIR,
        account="cmip6",
        interface="ib0",
    )
    client = dd.Client(cluster)
    print(client.dashboard_link)
    cluster.scale(100)

    for daily_geotiff_dir in [DAILY_BEAUFORT_DIR, DAILY_CHUKCHI_DIR]:
        for ice_season in ice_years:
            geotiff_files = list_geotiffs(daily_geotiff_dir)
            ice_year_geotiffs = sorted(select_by_ice_year(geotiff_files, ice_season))
            data_arrays = []
            dates = []

            for file in ice_year_geotiffs:
                date = extract_date_from_filename(file.name)
                dates.append(date)
                # dask to load the data lazily
                data_array = dask.delayed(load_geotiff_as_dataarray)(file)
                data_arrays.append(data_array)

            # compute and stack data arrays to xr dataset with time dim
            data_arrays = dask.compute(*data_arrays)
            dataset = xr.concat(data_arrays, dim="time").to_dataset(name="slie")
            dataset["slie"] = dataset["slie"].astype("int16")

            dataset = dataset.assign_coords(time=("time", dates))
            dataset.attrs["crs"] = rasterio.open(geotiff_files[0]).crs.to_string()

            if daily_geotiff_dir == DAILY_BEAUFORT_DIR:
                nc_prefix = "beaufort"
                nc_output_dir = BEAUFORT_NETCDF_DIR
            else:
                nc_prefix = "chukchi"
                nc_output_dir = CHUKCHI_NETCDF_DIR

            output_nc_file = (
                nc_output_dir / f"{nc_prefix}_sea_daily_slie_{ice_season}.nc"
            )
            write_netcdf(dataset, output_nc_file)

            print(f"NetCDF successfully written to {output_nc_file}")

    time.sleep(10)
    client.close()
    cluster.scale(0)
    cluster.close()
