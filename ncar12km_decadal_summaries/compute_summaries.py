"""Module for loading, projecting, slicing, and summarizing climate data into GeoTIFFs from a set of netCDF files."""


def mfload_all_netcdf_data(paths):
    """
    Load and combine all netCDF files specified in `paths` into a single xarray DataArray.

    Args:
        paths (list): A list of PosixPath pathlib objects pointing to netCDF files.

    Returns:
        datacube (xarray.DataArray): A single, combined xarray DataArray of all data from the netCDF files.
    """
    with xr.open_mfdataset(paths, combine="nested", concat_dim=["time"]) as datacube:
        return datacube
    

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
    wgs_proj = Proj(proj='latlong', datum='WGS84')
    
    transformer = Transformer.from_proj(wgs_proj, wrf_proj)
    e, n = transformer.transform(-150, 64)
    # Grid parameters
    dx, dy = 12000, 12000
    ny, nx = datacube.longitude.shape[1:]
    
    # Down left corner of the domain
    x0 = -(nx-1) / 2. * dx + e
    y0 = -(ny-1) / 2. * dy + n
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


def list_years_in_decade(start_year):
    """
    Given a starting year, return a list of ten consecutive years representing a decade.

    Args:
        start_year (int): starting year of the decade

    Returns:
        list: A list of ten consecutive years
    """
    return list(range(start_year, start_year + 10))


def slice_by_decade(datacube, decade_start_year):
    """
    Given a xarray datacube and a starting year, slice the datacube to select only
    the data from the decade corresponding to the starting year.

    Args:
        datacube (xarray.Dataset): multidimensional datacube
        decade_start_year (int): starting year of the decade to be sliced

    Returns:
        decade_slice (xarray.Dataset): A sliced xarray datacube containing only the data from the
        specified decade (e.g. 2030 through 2039)
    """
    years = list_years_in_decade(decade_start_year)
    decade_slice = datacube.isel(time=datacube.time.dt.year.isin(years))
    return decade_slice


def compute_monthly_summaries(decade_slice, vargroup, climvar):
    """
    Compute monthly summaries like mean, total, etc. of a climatological variable over a decadal slice of data.
    
    Args:
        decade_slice (xarray.Dataset): a slice of data corresponding to a decade.
        vargroup (str): category of variables to summarize (one of wf, ws, eb, or met)
        climvar (str): name of the climatological variable to summarize.
    
    Returns:
        dec_mean_monthly_summary (xr.DataArray): a dataset containing the decadal monthly summaries of the given climatological variable.
    """
    
    summary_func = variable_di[vargroup][climvar]
    out = (
        decade_slice[climvar]
        .resample(time="1M")
        .reduce(summary_func)
        .groupby("time.month")
        .reduce(np.mean)  # decadal summary is always a mean
    )
    dec_mean_monthly_summary = out.compute()
    return dec_mean_monthly_summary


def make_output_filename(climvar, model, scenario, month, start_year):
    """
    Constructs an output filename for a climatic variable summary.
    
    Args:
        climvar (str): name of the physical variable
        model (str): name of the climate model
        scenario (str): name of the emissions scenario
        month (int): month number (1-12)
        start_year (int): first year of the decade for the summary period.
        
    Returns:
        str: A string representing the output filename in the format of "<climvar>_<units>_<model>_<scenario>_<month_abbrev>_<summary_func>_<start_year>-<end_year>_mean.tif".

    """
    units = unit_di[climvar]
    mo_summary_func = summary_di[climvar]
    out_filename = f"{climvar.lower()}_{units}_{model}_{scenario}_{mo_names[month]}_{mo_summary_func}_{start_year}-{start_year + 10}_mean.tif"
    return out_filename


def write_raster_to_disk(out_filename, raster_profile, raster_data):
    """
    Args:
        out_filename (str): name of the output GeoTIFF.
        raster_profile (dict): raster profile parameters used to create the output GeoTIFF.
        raster_data (ndarray): raster data to be written to disk.

    Returns:
        None
    """
    with rio.open(
        OUTPUT_DIR / out_filename, "w", **raster_profile
    ) as dst:
        dst.write(raster_data, 1)