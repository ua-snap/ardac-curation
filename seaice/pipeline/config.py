"""This config file is used to ensure the correct GDAL and PROJ libraries are used. We set the GDAL_DATA and PROJ_LIB environment variables. The behavior of anaconda-project with regards to these variables is a known issue: https://github.com/Anaconda-Platform/anaconda-project/issues/349. Import this config file before other geospatial imports (rasterio, pyproj, etc.)."""

import os

if os.getenv("GDAL_DATA") != "":
    os.environ["GDAL_DATA"] = f"{os.getenv('CONDA_DEFAULT_ENV')}/share/gdal"
if os.getenv("PROJ_LIB") != "":
    os.environ["PROJ_LIB"] = f"{os.getenv('CONDA_DEFAULT_ENV')}/share/proj"
