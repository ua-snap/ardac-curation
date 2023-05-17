"""Configuration for shared directories and objects"""

import os
import calendar
import numpy as np
from pathlib import Path

# path to Sergey's directory containing the most recent .zip files of IEM GIPL outputs
SOURCE_DIR = Path(os.getenv("SOURCE_DIR") or "/atlas_scratch/ssmarchenko/ssmarchenko_home/2022_IEM_proj")

# path to target directory for data extraction
TARGET_DIR = Path(os.getenv("TARGET_DIR") or "/atlas_scratch/cparr4/GIPL_IEM")
TARGET_DIR.mkdir(exist_ok=True, parents=True)

extracted_monthly_dir = TARGET_DIR.joinpath("extracted_monthly")
extracted_monthly_dir.mkdir(exist_ok=True)

# need this extra directory to deconflict extracted filenames
extracted_renamed_monthly_dir = extracted_monthly_dir.joinpath("renamed")
extracted_renamed_monthly_dir.mkdir(exist_ok=True)

extracted_annual_dir = TARGET_DIR.joinpath("extracted_annual")
extracted_annual_dir.mkdir(exist_ok=True)

# path to output directory for processed data
output_dir = TARGET_DIR.joinpath("outputs")
output_dir.mkdir(exist_ok=True)

# models, scenarios, month numbers and abbreviations
scenarios = ["rcp45", "rcp85"]
models = [
    "NCAR-CCSM4",
    "MRI-CGCM3",
]
months = list(range(1, 13))
mo_names = [x.lower() for x in calendar.month_abbr]


# # for the 3338 geotiffs
# reprojected_dir = OUTPUT_DIR.joinpath("reprojected_geotiffs")
# reprojected_dir.mkdir(exist_ok=True)

# # for one-off or limited use outputs
# aux_dir = OUTPUT_DIR.joinpath("auxiliary_content")
# aux_dir.mkdir(exist_ok=True)

# # for the zipped goods. zippy longstocking
# zip_dir = OUTPUT_DIR.joinpath("zipped")
# zip_dir.mkdir(exist_ok=True)
