"""Configuration for shared directories and objects"""

import os
import calendar
import numpy as np
from pathlib import Path

# path to directory containing input NCAR met and VIC hydro datasets
DATA_DIR = Path(os.getenv("DATA_DIR") or "/atlas_scratch/cparr4/ncar_replacement_data")
# path to directory containing where outputs will be writtene
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR") or "/atlas_scratch/cparr4/AK_NCAR_12km_decadal_means_of_monthly_summaries")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# for one-off or limited use outputs
aux_dir = OUTPUT_DIR.joinpath("auxiliary_content")
aux_dir.mkdir(exist_ok=True)

# models, scenarios, month numbers and abbreviations
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
months = list(range(1, 13))  # xr indexes months 1 to 12 after `groupby('time.month')`
mo_names = [x.lower() for x in calendar.month_abbr]

# monthly summary functions for each variable
variable_di = {
    "met": {"pcp": np.sum, "tmax": np.mean, "tmin": np.mean},
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

# monthly summary type tags for output filenames
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
