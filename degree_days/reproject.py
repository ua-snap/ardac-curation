"""Module for raster I/O and reprojection tasks."""

import rasterio as rio
from rasterio.warp import (
    Resampling,
    aligned_target,
)
from rasterio.transform import array_bounds
from config import reprojected_dir, unit_tag

# hard coding some experimentally derived output dimensions
# based on results of `gdalwarp -tap -tr 12000 12000`
dst_crs = rio.crs.CRS.from_epsg(3338)
tr = 12000
t_width = 317
t_height = 224


def reproject_raster(file, name_prefix):
    with rio.open(file) as src:

        # compute the new affine transformation, width and height
        warp_transform, width, height = rio.warp.calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds, resolution=(tr, tr)
        )
        tap_transform, tap_width, tap_height = aligned_target(
            warp_transform, t_width - 1, t_height - 1, tr
        )  # the -1 might just be an indexing thing
        # but without the offset, the output height and width are too large (by 1) when compared to what is created by gdalwarp -tap

        # define the output raster profile
        out_profile = src.profile.copy()
        out_profile.update(
            {
                "crs": dst_crs,
                "transform": tap_transform,
                "width": t_width,
                "height": t_height,
                "bounds": array_bounds(tap_height, tap_width, tap_transform),
            }
        )

        # create the new raster file
        out_file = reprojected_dir / f"{name_prefix}_{file.name[:-4]}_{unit_tag}.tif"
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


def write_raster_to_disk(out_filename, raster_profile, raster_data):
    """
    Args:
        out_filename (str): name of the output GeoTIFF.
        raster_profile (dict): raster profile parameters used to create the output GeoTIFF.
        raster_data (ndarray): raster data to be written to disk.

    Returns:
        None
    """
    with rio.open(out_filename, "w", **raster_profile) as dst:
        dst.write(raster_data, 1)
