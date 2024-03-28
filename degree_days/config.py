"""Configuration for executing the degree day metric computations. Mostly directory configurations with some sane Atlas defaults. Also where output filenames are tweaked."""
import os
from pathlib import Path

# path to directory containing source input data
DATA_DIR = Path(os.getenv("DATA_DIR") or "/atlas_scratch/Base_Data/AK_NCAR_12km/met")

# path to directory where outputs will be written
if os.getenv("OUTPUT_DIR") is not None:
    OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR"))
else:
    USER = os.getenv("USER")
    OUTPUT_DIR = Path(f"/atlas_scratch/{USER}/degree_days_ncar_12km")

OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


# for the Daymet data (historical)
# this is a 'special' dir because it does not have rcp45/85 subdirectories
daymet_dir = DATA_DIR.joinpath("daymet")
daymet_dir.mkdir(exist_ok=True)

# for the 3338 geotiffs
reprojected_dir = OUTPUT_DIR.joinpath("reprojected_geotiffs")
reprojected_dir.mkdir(exist_ok=True)

# for one-off or limited use outputs
aux_dir = OUTPUT_DIR.joinpath("auxiliary_content")
aux_dir.mkdir(exist_ok=True)

# for reference climatology outputs
climo_dir = OUTPUT_DIR.joinpath("climatologies")
climo_dir.mkdir(exist_ok=True)


# for the zipped goods. zippy longstocking
zip_dir = OUTPUT_DIR.joinpath("zipped")
zip_dir.mkdir(exist_ok=True)

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

# metrics to process, strings will be used in output file names
metrics = [
    "air_freezing_index",
    "air_thawing_index",
    "heating_degree_days",
    "degree_days_below_zero",
]

# appended to output file names
unit_tag = "Fdays"
