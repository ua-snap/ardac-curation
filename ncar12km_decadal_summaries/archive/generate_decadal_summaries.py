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
from tqdm import tqdm

# local
from wrf_raster_profile import create_wrf_raster_profile
from config import (
    mo_names,
    months,
    unit_di,
    summary_di,
    variable_di,
    precision_di,
)

# A valid WRF projection can trigger this warning so I've hushed it
warnings.filterwarnings(
    "ignore",
    message="You will likely lose important projection information when converting to a PROJ string",
)

def determine_variable_group(input_dir):
    if "met" in input_dir:
        var_group = "met"  # temps, total precip
    else:
        var_group = "vic_hydro"  # all other variables
    return var_group


def get_file_paths(subgroup, input_dir):
    paths = [Path(x) for x in glob.glob(f"{input_dir}*") if subgroup in x]
    return paths


def parse_model(paths):
    model = paths[0].parent.parent.name
    return model


def parse_scenario(paths):
    scenario = paths[0].parent.name
    return scenario


def load_wrf_profile(paths=None):
    try:
        with open("wrf_profile.pickle", "rb") as handle:
            wrf_profile = pickle.load(handle)
    except:
        # or generate it
        wrf_profile = create_wrf_raster_profile(paths[0])
    return wrf_profile


def mfload_all_netcdf_data(paths):
    datacube = xr.open_mfdataset(paths, combine="nested", concat_dim=["time"])
    return datacube


def list_years_in_decade(start_year):
    return list(range(start_year, start_year + 10))


def slice_by_decade(datacube, decade_start_year):
    years = list_years_in_decade(decade_start_year)
    decade_slice = datacube.isel(time=datacube.time.dt.year.isin(years))
    return decade_slice


def compute_monthly_summaries(var_group, decade_slice, met_or_wf_or_ws, climvar):
    
    summary_func = variable_di[var_group][met_or_wf_or_ws][climvar]
    out = (
        decade_slice[climvar].sortby("time")
        .resample(time="1M")
        .reduce(summary_func)
        .groupby("time.month")
        .reduce(np.mean)  # decadal summary is always a mean
    )
    dec_mean_monthly_summary = out.compute()
    return dec_mean_monthly_summary


def prep_monthly_output_data(dec_mean_monthly_summary, climvar, mo):
    # we lose the orientation from xr and it flips upside down
    data = np.flipud(dec_mean_monthly_summary.sel(month=mo).data)
    # round to sensible precision levels
    data = data.round(precision_di[climvar])
    # set nodata values to -9999
    data = np.nan_to_num(data, nan=-9999.0)
    return data


def reproject_to_3338(data):
    wrf_profile = load_wrf_profile()
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
    
    return reprojected_data, ak_albers_profile


def make_output_filename(climvar, model, scenario, mo, start_year, end_year):
    units = unit_di[climvar]
    mo_summary_func = summary_di[climvar]
    out_filename = f"{climvar.lower()}_{units}_{model}_{scenario}_{mo_names[mo]}_{mo_summary_func}_{start_year}-{end_year}_mean.tif"
    return out_filename


def write_raster_to_disk(output_dir, out_filename, ak_albers_profile, reprojected_data):
    with rio.open(
        Path(output_dir) / out_filename, "w", **ak_albers_profile
    ) as dst:
        dst.write(reprojected_data, 1)


def create_decadal_averages(input_dir, output_dir):
    var_group = determine_variable_group(input_dir)
    for subgroup in variable_di[var_group].keys():
        paths = get_file_paths(subgroup, input_dir)
        model = parse_model(paths)
        scenario = parse_scenario(paths)
        datacube = mfload_all_netcdf_data(paths)

        for decade_start in tqdm(range(1950, 2100, 10), desc=f"Processing decades for {model} {scenario} {subgroup} data..."):
            decade_slice = slice_by_decade(datacube, decade_start)
            
            for climvar in tqdm(variable_di[var_group][subgroup].keys(),  desc=f"Processing variables for {decade_start}s"):
                
                decadal_mean_of_monthly_summary = compute_monthly_summaries(var_group, decade_slice, subgroup, climvar)
                
                for mo in months:
                    single_month_output_data = prep_monthly_output_data(decadal_mean_of_monthly_summary, climvar, mo)
                    reprojected_data, raster_creation_profile = reproject_to_3338(single_month_output_data)
                    
                    output_filename = make_output_filename(climvar, model, scenario, mo, decade_start, decade_start + 9)
                    write_raster_to_disk(output_dir, output_filename, raster_creation_profile, reprojected_data)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="directory containing input netCDF files")
    parser.add_argument("output_dir", help="directory to save output GeoTIFF files")
    args = parser.parse_args()

    create_decadal_averages(args.input_dir, args.output_dir)
