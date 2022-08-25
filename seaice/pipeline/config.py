"""This is a config file"""

# These lines have the sole prupose of making sure
# the GDAL_DATA and PROJ_LIB vars have the correct value!
# if these are set in the parent conda env, those variables
# will not be overwritten by anaconda-project as of now
# track issue https://github.com/Anaconda-Platform/anaconda-project/issues/349
# This needs to be imported before rasterio/pyproj imports
import os

if os.getenv("GDAL_DATA") != "":
    os.environ["GDAL_DATA"] = f"{os.getenv('CONDA_DEFAULT_ENV')}/share/gdal"
if os.getenv("PROJ_LIB") != "":
    os.environ["PROJ_LIB"] = f"{os.getenv('CONDA_DEFAULT_ENV')}/share/proj"