import warnings

import rasterio as rio
from rasterio.warp import Resampling, aligned_target
from rasterio.transform import array_bounds

from luts import data_sources
from config import DAILY_CHUKCHI_DIR, DAILY_BEAUFORT_DIR

# set target resolution and crs
tr = 100
dst_crs = rio.crs.CRS.from_epsg(3338)


def rename(fp):
    if "Chuk" == fp.parent.parent.name:
        zone = "Chukchi"
        out_dir = DAILY_CHUKCHI_DIR
    elif "Beau" == fp.parent.parent.name:
        zone = "Beaufort"
        out_dir = DAILY_BEAUFORT_DIR
    else:
        print(fp)
    
    fname = fp.name
    yyyymmdd = fname.split("_")[0][1:]

    data_source_indicator = fname[0]
    source_str = data_sources[data_source_indicator].lower().replace(" ", "_")

    new_name = f"{zone.lower()}_{yyyymmdd}_{source_str}_slie.tif"
    new_fp = out_dir / new_name
    return new_fp


def tap_reproject_raster(file):
    with rio.open(file) as src:
        # compute the new affine transformation, width and height
        warp_transform, width, height = rio.warp.calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds, resolution=(tr, tr)
        )
        tap_transform, tap_width, tap_height = aligned_target(
            warp_transform, width, height, tr
        )
        
        # define the output raster profile
        out_profile = src.profile.copy()
        out_profile.update(
            {
                "crs": dst_crs,
                "transform": tap_transform,
                "width": tap_width,
                "height": tap_height,
                "bounds": array_bounds(tap_height, tap_width, tap_transform),
                "nodata": 111,
            }
        )

        # create the new raster file name
        out_file = rename(file)
        warnings.filterwarnings("ignore")

        with rio.open(out_file, "w", **out_profile) as dst:
            # reproject the input raster data
            rio.warp.reproject(
                source=src.read(1),
                destination=rio.band(dst, 1),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=tap_transform,
                dst_crs=dst_crs,
                resampling=Resampling.nearest,  # NN is default, but explicit here for easy change or experimentation later
            )