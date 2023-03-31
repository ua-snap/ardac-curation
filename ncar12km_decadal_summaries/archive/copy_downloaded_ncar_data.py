"""Script to copy replacement data downloaded from NCAR into the shared Atlas Base_Data directory"""

import shutil
from pathlib import Path
import glob

vic_hydro_dst_trunk = "/atlas_scratch/Base_Data/AK_NCAR_12km/vic_hydro/daily/BCSD"
met_dst_trunk = "/atlas_scratch/Base_Data/AK_NCAR_12km/met"
paths = [Path(x) for x in glob.glob("*.nc")]

for fp in paths:
    model = fp.name.split("_")[0]
    scenario = fp.name.split("_")[1]
    if "met" in fp.name:
        dst_directory = f"{met_dst_trunk}/{model}/{scenario}"
    else:
        dst_directory = f"{vic_hydro_dst_trunk}/{model}/{scenario}"
    
    print(f"Copying {fp} to {dst_directory}")
    shutil.copy(fp, dst_directory)
