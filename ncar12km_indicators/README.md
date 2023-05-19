# NCAR 12km Met Indicators

## Background

This pipeline contains code for creating an indicators dataset from the the [NCAR Alaska Near Surface Meteorology Daily Averages](https://www.earthsystemgrid.org/dataset/ucar.ral.hydro.predictions.alaska.met.daily.html) dataset, which is part of the ["21st Century Hydrologic Projections for Alaska and Hawaii"](https://www.earthsystemgrid.org/dataset/ucar.ral.hydro.predictions.html) data release.

The goal of creating this dataset is for inclusion in ARDAC and for integration with tools such as Northern Climate Reports and the Arctic-EDS. Source data are available for download from the Climate Data Gateway at NCAR.

This dataset has been explored and vetted [elsewhere in this repository](https://github.com/ua-snap/ardac-curation/blob/2ac116c4f0fb6f68369bc998d3cb9117c441a5e1/ncar12km_decadal_summaries/README.md) - please reference that section for more background information on the source data.

## Pipeline

### Yearly indicators

Use the `process_indicators.ipynb` notebook to create the base indicators dataset, which will compute the following indicators:

* `hd`:  “Hot day” threshold -- the highest observed daily $T_{max}$ such that there are 5 other observations equal to or greater than this value.
* `cd`: “Cold day” threshold -- the lowest observed daily $T_{min}$ such that there are 5 other observations equal to or less than this value.
* `rx1day`: Maximum 1-day precipitation
* `su`: Summer Days –- Annual number of days with Tmax above 25 C
* `dw`: Deep Winter days –- Annual number of days with Tmin below -30 C
* `wsdi`: Warm Spell Duration Index -- Annual count of occurrences of at least 5 consecutive days with daily mean T above 90 th percentile of historical values for the date
* `cdsi`: Cold Spell Duration Index -- Same as WDSI, but for daily mean T below 10 th percentile
* `rx5day`: Maximum 5-day precipitation
* `r10mm`: Number of heavy precip days –- Annual count of days with precip > 10 mm
* `cwd`: Consecutive wet days –- Yearly number of the most consecutive days with precip > 1 mm
* `cdd`: Consecutive dry days –- Same as CED, but for days with precip < 1 mm

These indicators are computed at the yearly time scale from the source data which comes at a daily scale. Here is the expected data cube for each indicator:

* model
* scenario
* year
* 2D spatial axes


### Era-based summary dataset for Rasdaman coverage

Use the `process_era_summary_coverage.ipynb` notebook to derive an era-based summary dataset from the above base yearly dataset, where all of the indicators are summarized by minimum, mean, and maximum aggregation operations over the year axis, using 30-year periods. This dataset is intended to be ingested into Rasdaman as-is, using ingest files in [this directory](https://github.com/ua-snap/rasdaman-ingest/tree/cad45e82a47a626f440a2443fcf7ea93c432a67d/ardac/ncar12km_indicators) of the `rasdaman-ingest` repository. 

Here is the expected data cube for the Rasdaman coverage:

* indicator
* era
* model
* scenario
* 2D spatial axes


## Processing Flow

The exploratory data analysis (EDA) notebook sets the stage for our expectations about the data and is used to craft some assertions to check for mistakes during processing. T

## Usage

Use the `snap-geo` conda environment on an Atlas compute node for this work. You'll need to set the following environment variables: `DATA_DIR` and `OUTPUT_DIR` - these are the directories for the source and output datasets. Set these:

```sh
export DATA_DIR=path_to_source_dataset
export OUTPUT_DIR=path_to_write_outputs
```

or they will default to some directories (see `config.py`).

If you only want to process certain models, scenarios, months, or variables, you can edit `config.py` to reduce the scope of processing as well. Currently, this dataset only processes two models which overlap with the NCR tool: NCAR-CCSM4 and MRI-CGCM3.

The `config.py` module establishes some directory structures, and lists the models and scenarios, and asserts which variables will be processed and how, and provides the template for output filenames. The module `indicators.py` contains the functions and logic used to compute indicators from daily data with the `xclim` package. There is a quality control (`qc`) notebook for use against all datasets created with the above notebooks. 
