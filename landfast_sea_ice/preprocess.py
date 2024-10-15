import warnings

import rasterio as rio
from rasterio.warp import Resampling, aligned_target
from rasterio.transform import array_bounds

from luts import data_sources
from config import CHUKCHI_DIR, BEAUFORT_DIR, DAILY_CHUKCHI_DIR, DAILY_BEAUFORT_DIR

# set target resolution and crs globally for all outputs
tr = 100
dst_crs = rio.crs.CRS.from_epsg(3338)


def mmm_rename(fp):
    """Rename the MMM summary files to a more descriptive name.
    Args:
        fp (Path): Path to the file to be renamed.
    Returns:
        (Path): Path for the renamed output file.
    """
    if "Chuk" == fp.parent.parent.parent.name:
        zone = "Chukchi"
        out_dir = CHUKCHI_DIR
    elif "Beau" == fp.parent.parent.parent.name:
        zone = "Beaufort"
        out_dir = BEAUFORT_DIR
    else:
        print(f"{fp} not in Beaufort or Chukchi, this is unexpected!")
    fname = fp.name
    month = fname.split("_")[1]

    if "1996-05" in fname:
        era = "1996-2005"
    elif "2005-14" in fname:
        era = "2005-2014"
    elif "2014-23" in fname:
        era = "2014-2023"
    else:
        print(f"{fp} does not have a valid era, this is unexpected!")

    new_name = f"{zone}_{month}_{era}_SLIE_MMM_summary.tif"
    new_fp = out_dir / new_name
    return new_fp


def tap_reproject_mmm_raster(file):
    """Reprojects a raster file to a new coordinate reference system (CRS) and aligns it to a target resolution.
    1. Opens the input raster file.
    2. Computes the new affine transformation, width, and height for the target CRS and resolution.
    3. Aligns the target affine transformation to the specified resolution.
    4. Updates the raster profile with the new CRS, transformation, dimensions, and compression settings.
    5. Creates a new raster file name based on the input file name.
    6. Reprojects the input raster data to the new CRS and writes it to the output file.
    The output raster file is saved with LZW compression.

    Args:
        file (str): The path to the input raster file.
    Returns:
        None
    """
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
                "compress": "lzw",
            }
        )

        # create the new raster file name
        out_file = mmm_rename(file)

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


def daily_slie_rename(fp):
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


def tap_reproject_daily_slie_raster(file):
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
                "compress": "lzw",
            }
        )

        # create the new raster file name
        out_file = daily_slie_rename(file)
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
