"""Module for projecting source input data to WRF grid and preparing daily average temperature (F) variable.
"""

import xarray as xr
import numpy as np
import rasterio as rio
from pyproj import Proj, Transformer, CRS
from wrf import PolarStereographic


def project_datacube(datacube):
    """
    Projects an xarray datacube to a polar stereographic grid with a 12 km resolution.

    Parameters
    ----------
    datacube : xarray.Dataset
        The input datacube to be projected. It should have the latitude and longitude dimensions.

    Returns
    -------
    projected_datacube : xarray.Dataset
        The projected datacube with the y and x dimensions.
    wrf_raster_profile : dict
        A dictionary containing parameters for the output raster such as the transform and the
        dimensions of the raster. This will be used to write summarized slices of the projected datacube to a GeoTIFF file.
    """
    wrf_proj_str = PolarStereographic(**{"TRUELAT1": 64, "STAND_LON": -150}).proj4()
    wrf_proj = Proj(wrf_proj_str)
    wgs_proj = Proj(proj="latlong", datum="WGS84")

    transformer = Transformer.from_proj(wgs_proj, wrf_proj)
    e, n = transformer.transform(-150, 64)
    # Grid parameters
    dx, dy = 12000, 12000

    try:
        ny, nx = datacube.longitude.shape[1:]
    except:
        ny, nx = datacube.longitude.shape  # met case has a little different structure

    # Down left corner of the domain
    x0 = -(nx - 1) / 2.0 * dx + e
    y0 = -(ny - 1) / 2.0 * dy + n
    # 2d grid
    x = np.arange(nx) * dx + x0
    y = np.arange(ny) * dy + y0

    projected_datacube = datacube.assign_coords({"y": ("y", y), "x": ("x", x)})

    # Output geotiff creation profile params
    width = datacube.x.shape[0]
    height = datacube.y.shape[0]

    # west and north
    west = x0 - dx / 2
    north = y[-1] + dy / 2
    out_transform = rio.transform.from_origin(west, north, dx, dy)

    wrf_raster_profile = {
        "driver": "GTiff",
        "crs": CRS.from_proj4(wrf_proj_str),
        "transform": out_transform,
        "width": width,
        "height": height,
        "count": 1,
        "dtype": np.float32,
        "nodata": -9999,
        "tiled": False,
        "compress": "lzw",
        "interleave": "band",
    }

    datacube.close()

    return projected_datacube, wrf_raster_profile


def prep_ds(fp):
    with xr.open_dataset(fp) as ds:

        ds["tavg"] = (ds["tmin"] + ds["tmax"]) / 2
        ds["tavg_F"] = ds["tavg"] * 9 / 5 + 32
        ds = ds.drop_vars(["tmin", "tmax", "tavg", "pcp"])
        proj_ds, out_profile = project_datacube(ds)

    return proj_ds, out_profile
