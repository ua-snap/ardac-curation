# Landfast Sea ice

## Setup
Create the conda environment from the `environment.yml` file if you have not done so already.
```sh
conda env create -f environment.yml
```
Activate the environment:
```sh
conda activate landfast_sea_ice
```
### Environment Variables
###### `INPUT_ZIP_DIR`
```sh
export INPUT_ZIP_DIR=/atlas_scratch/"$USER"/landfast_sea_ice
```
###### `INPUT_FLAT_DIR`
```sh
export INPUT_FLAT_DIR=/atlas_scratch/"$USER"/landfast_sea_ice
```
###### `SCRATCH_DIR`
Set the path where you will read/write intermediate data. Something like:
```sh
export INPUT_FLAT_DIR=/atlas_scratch/"$USER"/landfast_sea_ice/scratch
```
###### `OUTPUT_DIR`
```sh
export INPUT_FLAT_DIR=/atlas_scratch/"$USER"/landfast_sea_ice/output
``` 
### Input Source Data Archive
"Beau" and "Chuk" (i.e. Beafort Sea and Chukchi Sea) directories shared by Andy Mahoney and Andrew Einhorn via Google Drive were downloaded as .zip files via the Google Drive browser GUI in July 2024 and deposited on SNAP's Poseidon storage:
`/workspace/Shared/Tech_Projects/landfast_sea_ice`

The above is a backed up location and users should copy these data to their preferred location before proceeding, e.g.,

`scp "$USER"@poseidon.snap.uaf.edu://workspace/Shared/Tech_Projects/landfast_sea_ice/*.zip $INPUT_ZIP_DIR`

## Background
Per conversations with the involved PIs the most impactful and high yield data are monthly
min/median/mean/max seaward landfast ice edge (aka **SLIE**) "fields" for three different 9-year summary periods: 1996-05, 2005-14, 2014-23. These results were updated July 2024 by the PI and the data reside separate `AllSeasonsAnalysis/MonthySLIEs_yyyy-yyyy` directories for each ice era and each ice region (Chukchi / Beaufort).