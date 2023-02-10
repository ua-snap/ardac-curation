import rasterio as rio
import numpy as np
import xarray as xr
import pickle
from wrf import PolarStereographic
from pyproj import Proj, Transformer, CRS


def create_wrf_raster_profile(sample_netcdf):
    # Grid values provided by NCAR email correspondence
    wrf_proj_str = PolarStereographic(**{"TRUELAT1": 64, "STAND_LON": -150}).proj4()
    wrf_proj = Proj(wrf_proj_str)
    wgs_proj = Proj(proj="latlong", datum="WGS84")
    transformer = Transformer.from_proj(wgs_proj, wrf_proj)
    e, n = transformer.transform(-150, 64)

    # Grid parameters
    dx, dy = 12000, 12000
    with xr.open_dataset(sample_netcdf) as ds:
        ny, nx = ds.longitude.shape
        width = ds.x.shape[0]
        height = ds.y.shape[0]

    # Down left corner of the domain
    x0 = -(nx - 1) / 2.0 * dx + e
    y0 = -(ny - 1) / 2.0 * dy + n
    # 2d grid
    x = np.arange(nx) * dx + x0
    y = np.arange(ny) * dy + y0
    # Define west and north
    west = x0 - dx / 2
    north = y[-1] + dy / 2
    transform = rio.transform.from_origin(west, north, dx, dy)

    wrf_profile = {
        "driver": "GTiff",
        "crs": CRS.from_proj4(wrf_proj_str),
        "transform": transform,
        "width": width,
        "height": height,
        "count": 1,
        "dtype": np.float32,
        "nodata": -9999,
        "tiled": False,
        "compress": "lzw",
        "interleave": "band",
    }

    return wrf_profile


if __name__ == "__main__":

    with open("wrf_profile.pickle", "wb") as handle:
        pickle.dump(
            create_wrf_raster_profile("ncar_sample.nc4"),
            handle,
            protocol=pickle.HIGHEST_PROTOCOL,
        )
