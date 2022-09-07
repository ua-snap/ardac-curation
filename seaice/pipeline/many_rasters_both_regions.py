"""The script creates a unified Chukchi + Beaufort dataset for cases where both regions have data from one or more rasters. The output is a merged raster that uses the time series maximum of the data from each region. This is considered Case D: many rasters, both regions."""

import argparse
import pickle
import rasterio as rio
import pandas as pd
import numpy as np
from pathlib import Path
from rasterio.merge import merge

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute raster unification Case D.")
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

    beauf_srcs = [x for x in dt_di[k]["matching data"] if "beauf" in x]
    chuk_srcs = [x for x in dt_di[k]["matching data"] if "chuk" in x]

    # for beaufort data
    if len(beauf_srcs) == 1:
        src = f"arrfix_{beauf_srcs[0]}"
        beauf_to_merge_src = src_dir.joinpath(src)
    else:
        data_arrs = []
        for src in beauf_srcs:
            data_file = f"arrfix_{src}"
            fp = src_dir.joinpath(data_file)
            with rio.open(fp) as data_src:
                data_arrs.append(data_src.read(1))
                data_profile = data_src.profile

        stack = np.dstack(data_arrs)
        time_max = np.nanmax(stack, axis=2)
        beauf_to_merge_src = max_dir.joinpath(
            "beaufort_time_max_of_" + str(k).split(" ")[0] + ".tif"
        )
        with rio.open(beauf_to_merge_src, "w", **data_profile) as dst:
            dst.write(time_max, 1)

        print(f"Maximum of Beaufort time range written to {beauf_to_merge_src}")

    # for chukchi data
    if len(chuk_srcs) == 1:
        src = f"arrfix_{chuk_srcs[0]}"
        chuk_to_merge_src = src_dir.joinpath(src)
    else:
        data_arrs = []
        for src in chuk_srcs:
            data_file = f"arrfix_{src}"
            fp = src_dir.joinpath(data_file)
            with rio.open(fp) as data_src:
                data_arrs.append(data_src.read(1))
                data_profile = data_src.profile

        stack = np.dstack(data_arrs)
        time_max = np.nanmax(stack, axis=2)
        chuk_to_merge_src = max_dir.joinpath(
            "chukchi_time_max_of_" + str(k).split(" ")[0] + ".tif"
        )
        with rio.open(chuk_to_merge_src, "w", **data_profile) as dst:
            dst.write(time_max, 1)

        print(f"Maximum of Chukchi time range written to {chuk_to_merge_src}")

    with rio.open(chuk_to_merge_src) as a, rio.open(beauf_to_merge_src) as b:
        out_arr, out_aff = merge([a, b])
    out_merged_fp = out_dir.joinpath("ak_landfast_ice_" + str(k).split(" ")[0].replace("-", "_") + ".tif")
    
    with open(mask_dir / "both_region_profile.pickle", "rb") as handle:
        new_profile = pickle.load(handle)
    new_profile["nodata"] = 0
    with rio.open(out_merged_fp, "w", **new_profile) as dst:
        dst.write(out_arr[0], 1)

    print(f"Results written to {out_merged_fp}")
