# NCAR VIC Curation: Met + Hydro

## Background
The purpose of this effort is to curate the NCAR Alaska Near Surface Meteorology Daily Averages and the Alaska VIC Hydro Model Output (1950-2099) Daily Averages [dataset](https://www.earthsystemgrid.org/dataset/ucar.ral.hydro.predictions.html) for ARDAC and for integration with tools such as Northern Climate Reports and the Arctic-EDS. Source data are available for download from the Climate Data Gateway at NCAR. Per the NCAR blurb about this dataset, high resolution ensembles of hydroclimate projections are useful for climate and water resources adaptation planning. Very few century-long, high-resolution hydroclimate projections exist over Alaska and none are statewide. This motivated developmean of a dataset consisting of multiple statistically downscaled climate model projections and corresponding off-line hydrologic model simulations to obtain hydrologic simulations from 1950 to 2099 over Alaska, which fills a critical gap in hydroclimate projection capabilities. Robust warming and increases in precipitation produce runoff increases for most of Alaska. However, runoff is likely to decrease in current glacierized areas in southeast Alaska.

Approach:
1) select climate model outputs based on CMIP5 RCPs 4.5 and 8.5
2) perform statistical downscaling to generate high-resolution climate input data for hydrologic models (12-km grid-spacing for Alaska
3) perform off-line hydrologic model simulations, using the Variable Infiltration Capacity (VIC) model. A full water-energy balance computation with a simple glacier model for Alaska is used.

The source data are annual netCDF files (with a daily frequency time step) that contain the data for a single model and scenario. There are 10 models and 2 scenarios. Within each model-scenario combination there are files of a few different types.

The Alaska Near Surface Meteorology Daily Averages have files names like `ACCESS1-3_rcp45_BCSD_met_1958.nc` and the `met` tag indicates that these files contain the following climate variables:

 - tmax (Maximum Daily 2-m air temperature, degrees C)
 - tmin (Minimum Daily 2-m air temperature, degrees C)
 - pcp (Daily precipitation, mm per day)
 
These variables are downscaled climate model output - they are not created by the VIC hydrologic model. The VIC outputs have filenames like `MRI-CGCM3_rcp85_BCSD_ws_2094.nc`, `GFDL-ESM2M_rcp85_BCSD_wf_2035.nc` and `CSIRO-Mk3-6-0_rcp85_BCSD_eb_2044.nc` where the tags `wf`, `ws` and `eb` are a shorthand that indicate what types of variables exist within thos file sets. The scheme is as follows:

 - `ws` (water state)
   - SWE (Snow water equivalent, mm)
   - IWE (Ice water equivalent, mm)
   - SM1 (Soil moisture layer1, mm)
   - SM2 (Soil moisture layer1, mm)
   - SM3 (Soil moisture layer3, mm)
   - WATER_ERROR (water balance error, mm)
   
 - `wf` (water flux)
   - RUNOFF (surface runoff, mm per day)
   - BASEFLOW (baseflow, mm per day)
   - EVAP (actual evapotranspiration, mm per day)
   - PRCP (precipitation, mm per day)
   - SNOW_MELT (snow melt, mm per day)
   - GLACER_MELT (ice melt, mm per day)
   
 - `eb` (energy balance)
   - NET_SHORT (net shortwave radiation, W/m<sup>2</sup>)
   - NET_LONG (net longwave radiation, W/m<sup>2</sup>)
   - SENSIBLE (sensible heat flux, W/m<sup>2</sup>)
   - LATENT (latent heat flux, W/m<sup>2</sup>)
   - GRND_FLUX (ground heat flux, W/m<sup>2</sup>)
   - SOIL_TEMP1 (soil temperature layer 1, degrees C)
   - SOIL_TEMP2 (soil temperature layer 2, degrees C)
   - SOIL_TEMP3 (soil temperature layer 3, degrees C)
   - ENERGY_ERROR (energy balance error, W/m<sup>2</sup>)
   
 
Note that our initial scope of work for this dataset does not include the energy balance (`eb`) portion of the VIC model outputs.


## Structure
The module `compute_summaries.py` contains the functions that are used to to execute the creation of the decadal averages of monthly summarized (means, totals, and maximum values) of various climate variables from input sets of NetCDF files and for writing the decadal averages to output GeoTIFFs on a model / scenario / variable / month / decade basis. The functions are imported into the notebooks that orchestrate the processing of each variable group (`wf`, `ws`, or `met`) using a Dask local cluster. The exploratory data analysis (EDA) notebook sets the stage for our expectations about the data and is used to craft some assertions during processing. The processing of each variable group is done within a notebook specific for that variable group, but the core logic and configuration is shared across notebooks.

## Usage

Use the `snap-geo` conda environment on an Atlas compute node for this work. You'll need to set the following environment variables: `DATA_DIR` and `OUTPUT_DIR` - these are the directories for the source and output datasets. Set these:
```sh
export DATA_DIR=path_to_source_dataset
export DATA_DIR=path_to_write_outputs
```
or they will default to some directories in cparr4's scratch space (see `config.py`).

If you only want to process certain models, scenarios, months, or variables, you can edit `config.py` to reduce the scope of processing as well.

Also note that if you want to monitor the Dask client it defaults to port 8787 (http://127.0.0.1:8787/status) so you'll need to forward that as well.

## References

These data should be cited as:

Mizukami, N., A. J. Newman, A. W. Wood, E. D. Gutmann, and J. J. Hamman, 2022: 21 st century
hydrologic projections for Alaska and Hawai’i. Boulder, CO: UCAR/NCAR/RAL. DOI:
https://doi.org/10.5065/c3kn-2y77

