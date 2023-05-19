"""Config file for setting shared paths, imports, etc"""

import os
from pathlib import Path


out_dir = Path(os.getev("OUTPUT_DIR") or "/atlas_scratch/kmredilla/")
# path to directory containing CORDEX data
ncar_dir = Path(os.getenv("DATA_DIR") or "/atlas_scratch/cparr4/ncar_replacement_data")

# path to dataset of yearly indicators to be computed using the process_indicators.ipynb notebook
indicators_fp = out_dir.joinpath("ncar12km_indicators.nc")

# path to dataset of era-based indicators, intended to be imported into Rasdaman
era_summary_out_dir = Path("/atlas_scratch/kmredilla/ncar12km_indicators")
era_summary_out_dir.mkdir(exist_ok=True)

# leaving other models available in this dataset in case of expansion of this dataset
models = [
    # "ACCESS1-3",
    # "CanESM2",
    "CCSM4",
    # "CSIRO-Mk3-6-0",
    # "GFDL-ESM2M",
    # "HadGEM2-ES",
    # "inmcm4",
    # "MIROC5",
    "MRI-CGCM3"
]

scenarios = ["rcp45", "rcp85"]

varnames = ["pcp", "tmin", "tmax"]

# map from model variable names to possible index variable names
indicator_varname_lu = {
    'rx1day': 'pcp',
    'rx5day': 'pcp',
    'r10mm': 'pcp',
    'cwd': 'pcp',
    'cdd': 'pcp',
    'hd': 'tmax',
    'su': 'tmax',
    'wsdi': 'tmax',
    'cd': 'tmin',
    'dw': 'tmin',
    'csdi': 'tmin'
}

indicators = list(indicator_varname_lu.keys())

# template filename
temp_fn = "{}_{}_BCSD_met_{}.nc"
