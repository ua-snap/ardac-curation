# AK NCAR 12 KM

## Creating Decadal Mean Summaries

### Structure

This script `generate_decadal_summaries.py` is responsible for creating decadal averages of monthly summarized (means, totals, and maximum values) of various climate variables from input sets of NetCDF files and writing the decadal averages to output GeoTIFFs on a model / scenario / variable / month / decade basis.

### Assumptions

The script takes two command line arguments: the input directory and the output directory. It also assumes that the input directory is a leaf directory, and that the output directory is created before running the script.

### Usage

This script can process both met and vic_hydro data types. The type of data is determined by the `src_type` variable, which is set based on the input directory's name. The script loads the input files from the input directory, creates decadal averages from the data, and writes the decadal averages to output files in the output directory. The output file names are formatted as: `variable_units_model_scenario_month_name_summary_function_start_year-end_year.tif`. The script also uses the `wrf_profile.pickle` file to set the profile for the output raster files.
If the `wrf_profile.pickle` file is not found, it will be created using the `create_wrf_raster_profile` function.

## Usage
