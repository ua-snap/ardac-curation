"""This script creates a unified Chukchi + Beaufort dataset for cases where one region has data from a single raster, but the other region does not have any data. The output is a merged raster using the data and the mask from the region without data. This is considered Case B: single raster, single region."""

import argparse
import pickle
import rasterio as rio
import pandas as pd
from pathlib import Path
from rasterio.merge import merge

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute raster unification Case B.")
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
    src_dir = Path(args.src_dir)
    out_dir = Path(args.out_dir)

    with open(args.dt, "rb") as handle:
        dt_di = pickle.load(handle)

    if dt_di[k]["chukchi_count"] > dt_di[k]["beaufort_count"]:
        mask_fp = mask_dir.joinpath("beaufort_mask.tif")
    else:
        mask_fp = mask_dir.joinpath("chukchi_mask.tif")

    data_match = dt_di[k]["matching data"][0]
    data_file = f"arrfix_{data_match}"
    fp = src_dir.joinpath(data_file)

    data_src = rio.open(fp)
    mask_src = rio.open(mask_fp)
    out_arr, out_aff = merge([data_src, mask_src])
    data_src.close()
    mask_src.close()

    out_merged_fp = out_dir.joinpath("ak_landfast_ice_" + str(k).split(" ")[0].replace("-", "_") + ".tif")

    with open(mask_dir / "both_region_profile.pickle", "rb") as handle:
        new_profile = pickle.load(handle)

    new_profile["nodata"] = 0
    with rio.open(out_merged_fp, "w", **new_profile) as dst:
        dst.write(out_arr[0], 1)

    print(f"Results written to {out_merged_fp}")
