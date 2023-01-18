# Permafrost Model Outputs

## Objective + Background

The purpose of this curation effort is to pre-process and quality control the full suite of the most recent (summer 2022 release) Geophysical Institute Permafrost Model (GIPL) outputs (the "CRREL dataset only") for use in the Arctic-EDS, ARDAC, and beyond. The model that produced the outputs that are analyzed and curated here was driven by several downscaled climate models (NCAR-CCSM4, GFDL-CM3, and an average blend of the two prior models plus three others with a high degree of skill for Alaska) driven under two separate emissions scenario (RCP 4.5 and RCP 8.5) forcing conditions. The model outputs include the following ten variables:

- Mean Annual Ground Temperature _(°C)_ at the following depths below the surface:
  - 0.01 m (also called the "surface" level)
  - 0.5 m
  - 1.0 m
  - 2.0 m
  - 3.0 m
  - 4.0 m
  - 5.0 m
- Permafrost Base _(m)_
- Permafrost Top _(m)_
- Talik Thickness _(m)_

## Structure

There are four key Jupyter Notebooks here: one for exploratory data analysis (EDA), one to process the data (pipeline), one for quality control (QC), and one for metadata generation (metadata). Each notebook contains the necessary information and code to meet the notebook objective. Most users should concentrate on the processing pipeline and quality control notebooks. Regenerating or modifying the dataset requires running the pipeline notebook, followed by the QC and metadata notebooks. The EDA work is contained within an `eda` directory to keep the structure of the curation a bit cleaner. The `zipit` notebook just has a script to generate a preview image and to compress the data into .zip files for distribution via the SNAP Data Catalog. The EDA notebook also examines a similar but separate dataset ("IEM") that isn't curated here.

## Executing Environment

These notebooks should be ran on your favorite Atlas compute node. Note that we've discontinued the use of `anaconda-project` for this curation effort. The environment used for this work is contained in a bespoke `environment.yml` file that is tracked within this repository. Be sure to activate that environment before attempting to run any of the code used in this curation effort.

## Curated Results

The ultimate dataset is comprised of 6000 individual GeoTIFF files with a 1 kilometer spatial resolution (i.e., pixel size). These data are ingested to the Rasdaman coverage `gipl_crrel_outputs` and data are backed up on disk (size 38 GB) at `/workspace/Shared/Tech_Projects/Arctic_EDS/project_data/rasdaman_datasets/crrel_gipl_outputs`. Note that the Rasdaman ingest recipe is not tracked in this repository - look for it over in the `rasdaman-ingest` repo.
