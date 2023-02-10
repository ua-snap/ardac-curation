import calendar
import numpy as np
from itertools import product


months = list(range(1, 13))  # xr indexes months 1 to 12 after `groupby('time.month')`
mo_names = [x.lower() for x in calendar.month_abbr]

# generate list of target directories
met_base = "/atlas_scratch/Base_Data/AK_NCAR_12km/met/"
vic_hydro_base = "/atlas_scratch/Base_Data/AK_NCAR_12km/vic_hydro/daily/BCSD/"
scenarios = ["rcp45", "rcp85"]
models = [
    "ACCESS1-3",
    "CanESM2",
    "CCSM4",
    "CSIRO-Mk3-6-0",
    "GFDL-ESM2M",
    "HadGEM2-ES",
    "inmcm4",
    "MIROC5",
    "MPI-ESM-MR",
    "MRI-CGCM3",
]
target_dirs = []
for src_group in list(product(models, scenarios)):
    target_dirs.append(f"{met_base}{src_group[0]}/{src_group[1]}/")
    target_dirs.append(f"{vic_hydro_base}{src_group[0]}/{src_group[1]}/")


variable_di = {
    "met": {"met": {"pcp": np.sum, "tmax": np.mean, "tmin": np.mean}},
    "vic_hydro": {
        "wf": {
            "SNOW_MELT": np.sum,
            "EVAP": np.sum,
            "GLACIER_MELT": np.sum,
            "RUNOFF": np.sum,
        },
        "ws": {
            "IWE": np.max,
            "SWE": np.max,
            "SM1": np.mean,
            "SM2": np.mean,
            "SM3": np.mean,
        },
    },
}
# unit tags for output filenames
unit_di = {
    "pcp": "mm",
    "tmax": "degC",
    "tmin": "degC",
    "SNOW_MELT": "mm",
    "EVAP": "mm",
    "GLACIER_MELT": "mm",
    "RUNOFF": "mm",
    "IWE": "mm",
    "SWE": "mm",
    "SM1": "mm",
    "SM2": "mm",
    "SM3": "mm",
}
# summary tags for output filenames
summary_di = {
    "pcp": "total",
    "tmax": "mean",
    "tmin": "mean",
    "SNOW_MELT": "total",
    "EVAP": "total",
    "GLACIER_MELT": "total",
    "RUNOFF": "total",
    "IWE": "max",
    "SWE": "max",
    "SM1": "mean",
    "SM2": "mean",
    "SM3": "mean",
}
# float precision for output rasters
precision_di = {
    "pcp": 0,
    "tmax": 1,
    "tmin": 1,
    "SNOW_MELT": 0,
    "EVAP": 0,
    "GLACIER_MELT": 0,
    "RUNOFF": 0,
    "IWE": 0,
    "SWE": 0,
    "SM1": 0,
    "SM2": 0,
    "SM3": 0,
}
