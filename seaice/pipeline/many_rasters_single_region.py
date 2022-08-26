"""This script creates a unified Chukchi + Beaufort dataset for cases where one region has data from multiple rasters, but the other region does not have any data. The output is merged raster using the maximum of the data and the mask from the region without data. This is considered Case C: many raster, single region."""

import argparse
import pickle
import rasterio as rio
import pandas as pd
import numpy as np
from pathlib import Path
from rasterio.merge import merge

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute raster unification Case C.")
    parser.add_argument(
        "-dt",
        "--datetime_dict",
        action="store",
        dest="dt",
    )
    parser.add_argument(
        "-ts",
        "--timestamp",
        action="store",
        dest="ts",
    )
    parser.add_argument(
        "-m",
        "--mask-dir",
        action="store",
        dest="mask_dir",
        type=str,
    )
    parser.add_argument(
        "-mx",
        "--max-dir",
        action="store",
        dest="max_dir",
        type=str,
    )
    parser.add_argument(
        "-src",
        "--src-dir",
        action="store",
        dest="src_dir",
        type=str,
    )
    parser.add_argument(
        "-o",
        "--out-dir",
        action="store",
        dest="out_dir",
        type=str,
    )

    args = parser.parse_args()
    k = pd.Timestamp(args.ts)
    mask_dir = Path(args.mask_dir)
    max_dir = Path(args.max_dir)
    src_dir = Path(args.src_dir)
    out_dir = Path(args.out_dir)

    with open(args.dt, "rb") as handle:
        dt_di = pickle.load(handle)

    if dt_di[k]["chukchi_count"] > dt_di[k]["beaufort_count"]:
        mask_fp = mask_dir.joinpath("beaufort_mask.tif")
    else:
        mask_fp = mask_dir.joinpath("chukchi_mask.tif")

    data_arrs = []
    for src in dt_di[k]["matching data"]:
        data_file = f"arrfix_{src}"
        fp = src_dir.joinpath(data_file)
        with rio.open(fp) as data_src:
            data_arrs.append(data_src.read(1))
            data_profile = data_src.profile

    stack = np.dstack(data_arrs)
    time_max = np.nanmax(stack, axis=2)
    time_max_fp = max_dir.joinpath("time_max_of_" + str(k).split(" ")[0] + ".tif")
    with rio.open(time_max_fp, "w", **data_profile) as dst:
        dst.write(time_max, 1)

    print(f"Maximum of time range written to {time_max_fp}")

    time_max_data_src = rio.open(time_max_fp)
    mask_src = rio.open(mask_fp)
    out_arr, out_aff = merge([time_max_data_src, mask_src])
    time_max_data_src.close()
    mask_src.close()

    out_merged_fp = out_dir.joinpath("ak_landfast_ice" + str(k).split(" ")[0] + ".tif")

    with open(mask_dir / "both_region_profile.pickle", "rb") as handle:
        new_profile = pickle.load(handle)

    new_profile["nodata"] = 0
    with rio.open(out_merged_fp, "w", **new_profile) as dst:
        dst.write(out_arr[0], 1)

    print(f"Results written to {out_merged_fp}")
