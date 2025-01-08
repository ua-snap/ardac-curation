"""Configuration for curating Einhorn/Mahoney 2024 Landfast Sea Ice Data."""

import os
from pathlib import Path

# path to directory of compressed data
# if not set, use the default
if "INPUT_ZIP_DIR" not in os.environ:
    INPUT_ZIP_DIR = None
else:
    INPUT_ZIP_DIR = Path(os.getenv("INPU_ZIP_DIR"))

# path to flat directory of extracted data
INPUT_DIR = Path(os.getenv("INPUT_DIR"))
INPUT_DIR.mkdir(exist_ok=True, parents=True)

# path to directory for intermediate files
SCRATCH_DIR = Path(os.getenv("SCRATCH_DIR"))
SCRATCH_DIR.mkdir(exist_ok=True, parents=True)

# path to a directory for output data
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR"))
OUTPUT_DIR.mkdir(exist_ok=True)

# one directory for Beaufort MMM
BEAUFORT_DIR = OUTPUT_DIR / "Beaufort_MMM"
BEAUFORT_DIR.mkdir(exist_ok=True)
# and one for Chukchi MMM
CHUKCHI_DIR = OUTPUT_DIR / "Chukchi_MMM"
CHUKCHI_DIR.mkdir(exist_ok=True)
# one directory for Beaufort Daily SLIE, + netCDFS
DAILY_BEAUFORT_DIR = OUTPUT_DIR / "Beaufort_Daily"
DAILY_BEAUFORT_DIR.mkdir(exist_ok=True)
BEAUFORT_NETCDF_DIR = OUTPUT_DIR / "Beaufort_NetCDFs"
BEAUFORT_NETCDF_DIR.mkdir(exist_ok=True)
# one directory for Chukchi Daily SLIE, + netCDFS
DAILY_CHUKCHI_DIR = OUTPUT_DIR / "Chukchi_Daily"
DAILY_CHUKCHI_DIR.mkdir(exist_ok=True)
CHUKCHI_NETCDF_DIR = OUTPUT_DIR / "Chukchi_NetCDFs"
CHUKCHI_NETCDF_DIR.mkdir(exist_ok=True)
