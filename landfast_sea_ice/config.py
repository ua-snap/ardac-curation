"""Configuration for curating Einhorn/Mahoney 2024 Landfast Sea Ice Data."""

import os
from pathlib import Path

# path to directory of compressed data
INPUT_ZIP_DIR = Path(os.getenv("INPUT_ZIP_DIR"))
INPUT_ZIP_DIR.mkdir(exist_ok=True, parents=True)

# path to flat directory of extracted data
INPUT_FLAT_DIR = Path(os.getenv("INPUT_FLAT_DIR"))
INPUT_FLAT_DIR.mkdir(exist_ok=True, parents=True)

# path to directory for intermediate files
#SCRATCH_DIR = Path(os.getenv("SCRATCH_DIR"))
#SCRATCH_DIR.mkdir(exist_ok=True, parents=True)

# path to a directory for output data
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR"))
OUTPUT_DIR.mkdir(exist_ok=True)
# one directory for Beaufort
BEAUFORT_DIR = OUTPUT_DIR / "Beaufort"
BEAUFORT_DIR.mkdir(exist_ok=True)
# and one for Chukchi
CHUKCHI_DIR = OUTPUT_DIR / "Chukchi"
CHUKCHI_DIR.mkdir(exist_ok=True)


# path to an archival directory for the pot-o-gold output data
# ARCHIVE_DIR = Path(os.getenv("ARCHIVE_DIR"))
# ARCHIVE_DIR.mkdir(exist_ok=True)
