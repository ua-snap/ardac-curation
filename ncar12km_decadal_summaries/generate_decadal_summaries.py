"""Generate decadal mean monthly summary GeoTIFFs of climate variables from the NCAR 12km netcdf source data."""

import argparse
import glob
import pickle
import logging
import warnings
from pathlib import Path

import xarray as xr
import numpy as np
import rasterio as rio
import dask.array as da
from tqdm import tqdm

from wrf_raster_profile import create_wrf_raster_profile
from config import (
    mo_names,
    months,
    unit_di,
    summary_di,
    variable_di,
    precision_di,
)


def create_decadal_averages(input_dir, output_dir, dry_run):
    """Create decadal average monthly summaries of daily resolution climate model output variables from the AK NCAR 12 km dataset.

    Arguments:
        input_dir -- (str) leaf directory of netcdf data
        output_dir -- (str) write-access directory where GeoTIFFs will be written to disk
        dry_run -- (bool, default=False) only log the input files and exit. do not process or write data
    """
    # A valid WRF projection can trigger this warning so I've hushed it
    warnings.filterwarnings(
        "ignore",
        message="You will likely lose important projection information when converting to a PROJ string",
    )
    # there are two variable groupings
    if "met" in input_dir:
        src_type = "met"  # temps and total precip
    else:
        src_type = "vic_hydro"  # all other variables
    # met vars are in 'met' files, but vic_hydro vars can be in 'wf' and 'ws' files
    for met_or_wf_or_ws in variable_di[src_type].keys():

        paths = [Path(x) for x in glob.glob(f"{input_dir}*") if met_or_wf_or_ws in x]
        scenario = paths[0].parent.name
        model = paths[0].parent.parent.name

        log_tag = f"{model}_{scenario}_{src_type}_{met_or_wf_or_ws}"
        logging.basicConfig(filename=f"{log_tag}.log", level=logging.INFO)
        logging.info("Input directory: %s", input_dir)
        logging.info("Output directory: %s", output_dir)
        logging.info("Input files: %s", [x.name for x in paths])
        # a pre-baked WRF raster profile can be used
        try:
            with open("wrf_profile.pickle", "rb") as handle:
                wrf_profile = pickle.load(handle)
        except:
            # or generate it from the first file in the list to be processed
            wrf_profile = create_wrf_raster_profile(paths[0])

        if dry_run:
            logging.info("Dry run: no data will be written to disk.")
        else:
            data_di = {}
            for file in tqdm(paths, desc="Loading Files"):
                ds = xr.open_mfdataset(file) # try this style indices_ds = xr.open_mfdataset(fps, combine="nested", concat_dim=[intervals])

                year = int(file.name.split("_")[-1].split(".")[0])
                data_di[year] = ds

            for i in tqdm(range(1950, 2100, 10), desc=f"Processing Decades"):
                start_year = i
                end_year = i + 9
                ds_decadal = xr.concat(
                    [data_di[j] for j in range(start_year, end_year + 1)], dim="time"
                )
                logging.info(f"Processing data between {start_year} and {end_year}...")
                logging.info(f"Processing data for {met_or_wf_or_ws}...")
                for climvar in tqdm(variable_di[src_type][met_or_wf_or_ws].keys(),  desc=f"Processing variables for {i}s"):
                    logging.info(f"Processing data for variable {climvar}...")
                    # climate vars are summarized over the month with different funcs
                    summary_func = variable_di[src_type][met_or_wf_or_ws][climvar]
                    out = (
                        ds_decadal[climvar]
                        .resample(time="1M")
                        .reduce(summary_func)
                        .groupby("time.month")
                        .reduce(np.mean)  # but the decadal summary is always a mean
                    )
                    dec_mean_monthly_summary = out.compute()

                    for mo in months:
                        # we lose the orientation from xr and it flips upside down
                        data = np.flipud(dec_mean_monthly_summary.sel(month=mo).data)
                        # round to sensible precision levels
                        # is this messing with our no data values?
                        data = data.round(precision_di[climvar])
                        # blast the no data values pew pew pew booooooom
                        data = np.nan_to_num(data, nan=-9999.0)
                        # set output filename
                        units = unit_di[climvar]
                        mo_summary_func = summary_di[climvar]
                        out_filename = f"{climvar.lower()}_{units}_{model}_{scenario}_{mo_names[mo]}_{mo_summary_func}_{start_year}-{end_year}_mean.tif"
                        logging.info("Output file: %s", out_filename)
                        # reproject data to EPSG:3338 before writing to disk
                        out_crs = rio.crs.CRS.from_epsg(3338).to_proj4()

                        (
                            out_transform,
                            out_width,
                            out_height,
                        ) = rio.warp.calculate_default_transform(
                            wrf_profile["crs"].to_proj4(),
                            out_crs,
                            data.shape[1],
                            data.shape[0],
                            left=-1794000.000,
                            bottom=-4046424.205,
                            right=1794000.000,
                            top=-1538424.205,
                        )
                        # init new array to reproject the data into
                        # check here to see if using np.full(nodata) changes rounding
                        dst_arr = np.empty((out_height, out_width), dtype=data.dtype)
                        reprojected_data, _ = rio.warp.reproject(
                            data,
                            destination=dst_arr,
                            src_transform=wrf_profile["transform"],
                            src_crs=wrf_profile["crs"],
                            src_nodata=wrf_profile["nodata"],
                            dst_crs=out_crs,
                            dst_transform=out_transform,
                            dst_nodata=wrf_profile["nodata"],
                            height=out_height,
                            width=out_width,
                        )
                        ak_albers_profile = wrf_profile.copy()
                        ak_albers_profile["crs"] = out_crs
                        ak_albers_profile["transform"] = out_transform
                        ak_albers_profile["height"] = out_height
                        ak_albers_profile["width"] = out_width

                        # write to disk
                        with rio.open(
                            Path(output_dir) / out_filename, "w", **ak_albers_profile
                        ) as dst:
                            dst.write(reprojected_data, 1)
            for k in data_di:
                data_di[k].close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="directory containing input netCDF files")
    parser.add_argument("output_dir", help="directory to save output GeoTIFF files")
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Dry run mode, no data will be written to disk.",
    )
    args = parser.parse_args()

    create_decadal_averages(args.input_dir, args.output_dir, args.dry_run)
