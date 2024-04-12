"""Module for computing various metrics from degree days."""

import numpy as np
import xarray as xr
from dask import delayed

from config import metrics


@delayed
def summarize_year_dd(temp_ds, temp_threshold, count_days_below_threshold):
    """Summarize the degree days for a year.

    Parameters
    ----------
    temp_ds : xarray.Dataset
        The dataset containing the daily average temperature.
    temp_threshold : int
        The temperature threshold for the degree day computation.
    count_days_below_threshold : bool
        A boolean variable indicating whether to count the days below the threshold.

    Returns
    -------
    degree_day_arr : xarray.DataArray
        The array containing the summarized degree days for the year.
    """

    if count_days_below_threshold:
        #  Use a bool variable (below) to specify that the DD
        #  below the threshold should be counted. This
        #  will be the case for heating DD, DD below 0, and freezing index
        degree_delta_arr = temp_threshold - temp_ds.tavg_F
    else:
        # Otherwise, count degree days above some threshold
        degree_delta_arr = temp_ds.tavg_F - temp_threshold

    # replace negative values with 0 prior to summing, but retain initial `np.nan` no data values
    degree_delta_arr = degree_delta_arr.where(
        (degree_delta_arr >= 0) | np.isnan(degree_delta_arr), 0
    )

    # total sum of degree days for the year
    sum_arr = np.nansum(degree_delta_arr, axis=0)
    # Replace sums that are 0 with `nan` if all values in the original stack were `nan`
    sum_arr = np.where(np.all(np.isnan(degree_delta_arr), axis=0), np.nan, sum_arr)

    # Create a new xarray.DataArray using sum_arr, and copy over the 'y' and 'x' coordinates and attributes
    degree_day_arr = xr.DataArray(
        np.round(sum_arr),
        coords={"y": temp_ds.tavg_F.coords["y"], "x": temp_ds.tavg_F.coords["x"]},
        dims=["y", "x"],
        attrs=temp_ds.tavg_F.attrs,
    )

    degree_day_arr = degree_day_arr.where(~np.isnan(degree_day_arr), -9999)
    return degree_day_arr


def compute_cumulative_freezing_index(temp_ds):
    air_freezing_index = summarize_year_dd(temp_ds, 32, True)
    return air_freezing_index


def compute_cumulative_heating_degree_days(temp_ds):
    heating_degree_days = summarize_year_dd(temp_ds, 65, True)
    return heating_degree_days


def compute_cumulative_degree_days_below_0F(temp_ds):
    degree_days_below0F = summarize_year_dd(temp_ds, 0, True)
    return degree_days_below0F


def compute_cumulative_thawing_index(temp_ds):
    air_thawing_index = summarize_year_dd(temp_ds, 32, False)
    return air_thawing_index
