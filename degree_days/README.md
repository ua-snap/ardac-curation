# Degree Day Metrics Derived from NCAR 12 km Near-Surface Meteorology Projections and Daymet Baseline

## Purpose
Compute degree day metrics including air freezing index, air thawing index, heating degree days, and degree days below 0F from the NCAR 12 km Alaska Near Surface Meteorology Daily Averages (1950-2099) [dataset](https://www.earthsystemgrid.org/dataset/ucar.ral.hydro.predictions.html) and the associated historical downscaling baseline (Daymet 12 km) for ARDAC and for integration with tools such as the Arctic-EDS. Source data are available for download from the Climate Data Gateway at NCAR.

## Source Data
The spatial resolution of all source data is 12 km.
Projected data represent highly skilled (CMIP5) climate models that have been statistically downnscaled using the Bias Corrected Spatial Disaggregation method (BCSD).
The data extent is primarily the terrestrial area of Alaska exlcuding the Western Aleutians. Portions of Yukon and British Columbia are within the data extent as well.
The historical baseline is Daymet (1980-2017) aggregated to 12 km resolution from the original 1 km resolution Daymet dataset (version 3). 

### Source File Structure
The source data consist of annual netCDF files (with a daily frequency time step) that contain data for a single model and scenario.
The source data file naming convention is like this `CCSM4_rcp45_BCSD_met_2065.nc4`
There are 10 models and 2 scenarios (RCP 4.5 and RCP 8.5). The ten models are:
  - "ACCESS1-3"
  - "CanESM2"
  - "CCSM4"
  - "CSIRO-Mk3-6-0"
  - "GFDL-ESM2M"
  - "HadGEM2-ES"
  - "inmcm4"
  - "MIROC5"
  - "MPI-ESM-MR"
  - "MRI-CGCM3"

Within each model-scenario combination the the `met` climate variables relevant for degree day metrics are:

- tmax (Maximum Daily 2-m air temperature, degrees C)
- tmin (Minimum Daily 2-m air temperature, degrees C)

### Source Directory Structure
Should look like this:
```
├── ACCESS1-3
│   ├── rcp45
│   └── rcp85
├── CanESM2
│   ├── rcp45
│   └── rcp85
├── CCSM4
│   ├── rcp45
│   └── rcp85
├── CSIRO-Mk3-6-0
│   ├── rcp45
│   └── rcp85
├── daymet
├── GFDL-ESM2M
│   ├── rcp45
│   └── rcp85
├── HadGEM2-ES
│   ├── rcp45
│   └── rcp85
├── inmcm4
│   ├── rcp45
│   └── rcp85
├── MIROC5
│   ├── rcp45
│   └── rcp85
├── MPI-ESM-MR
│   ├── rcp45
│   └── rcp85
└── MRI-CGCM3
    ├── rcp45
    └── rcp85
```

## Processing
The exploratory data analysis (EDA) notebook sets expectations about the source data and is used to craft some assertions to check for mistakes during processing. The `config.py` module establishes some directory structures, and lists the models and scenarios, and provides the template for output filenames. The module `prep_dataset.py` will contain the functions to preprocess the dataset prior to computing degree day metrics. The module `compute_degree_days.py` contains the logic used to compute the various degree metrics for each year, model, and scenario.

Output GeoTIFF files will be created on a metric / model / scenario / year basis. Jupyter notebooks orchestrate the processing of each degree day metric using a Dask local cluster. The `reproject` notebook illustrates a few different pathways for reprojecting the data to EPSG:3338 but ultimately uses rasterio and dask to accomplish the task. Finally, there is a quality control (`qc`) notebook and some tools to orchestrate zipping the data up for distribution on a per-metric basis.

## Methods
 - The input data variables of `tmin` and `tmax` will be averaged and converted from Celsius to Fahrenheit prior to computing degree day metrics.
 - The "cumulative" method of computing degree day metrics will be used. This is a simple summation method of daily values below or above a given temmperature (e.g., freezing) threshold.

## Usage

Use the `snap-geo` conda environment on an Atlas or Chinook compute node for this work. You'll need to set the following environment variables: `DATA_DIR` and `OUTPUT_DIR` - these are the directories for the source and output datasets. Set these:

```sh
export DATA_DIR=path_to_source_dataset
export OUTPUT_DIR=path_to_write_outputs
```

or they will default to some directories in Atlas' scratch space (see `config.py`).

If you only want to process certain models, scenarios, months, or variables, you can edit `config.py` to reduce the scope of processing as well.

Also note that if you want to monitor the Dask client it defaults to port 8787 (http://127.0.0.1:8787/status) so you'll need to forward that port as well.

## References

References to the source data and products derived from it like those computed here should be cited as:

Mizukami, N., A. J. Newman, A. W. Wood, E. D. Gutmann, and J. J. Hamman, 2022: 21 st century
hydrologic projections for Alaska and Hawai’i. Boulder, CO: UCAR/NCAR/RAL. DOI:
https://doi.org/10.5065/c3kn-2y77
