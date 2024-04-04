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
        # Use a bool variable (below) to specify that the DD
        #  below the threshold should be counted. This
        #  will be the case for heating DD, DD below 0, and freezing index
        degree_day_arr = temp_threshold - temp_ds.tavg_F
    else:
        # Otherwise, count degree days above some threshold
        degree_day_arr = temp_ds.tavg_F - temp_threshold

    # replace negative values with 0
    degree_day_arr = degree_day_arr.where(degree_day_arr >= 0, 0)
    # total sum of degree days for the year
    degree_day_arr = np.round(degree_day_arr.sum(axis=0))

    return degree_day_arr


def compute_cumulative_freezing_index(temp_ds):
    air_freezing_index = summarize_year_dd(temp_ds, 32, True)
    # 0 values will be no data
    air_freezing_index = air_freezing_index.where(air_freezing_index != 0, -9999)
    return air_freezing_index


def compute_cumulative_heating_degree_days(temp_ds):
    heating_degree_days = summarize_year_dd(temp_ds, 65, True)
    heating_degree_days = heating_degree_days.where(heating_degree_days != 0, -9999)
    return heating_degree_days


def compute_cumulative_degree_days_below_0F(temp_ds):
    degree_days_below0F = summarize_year_dd(temp_ds, 0, True)
    degree_days_below0F = degree_days_below0F.where(degree_days_below0F != 0, -9999)
    return degree_days_below0F


def compute_cumulative_thawing_index(temp_ds):
    air_thawing_index = summarize_year_dd(temp_ds, 32, False)
    air_thawing_index = air_thawing_index.where(air_thawing_index != 0, -9999)
    return air_thawing_index
