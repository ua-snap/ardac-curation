# Landfast Sea Ice
## Setup
Create the `snap-geo` conda environment if you have not done so already and activate it.
```sh
git clone https://github.com/ua-snap/snap-geo.git
cd snap-geo
conda env create -f environment.yml
conda activate snap-geo
```

### Source Data Archive
Landfast Sea Ice data products are split into "Beau" and "Chuk" (i.e., Beaufort Sea and Chukchi Sea) directories. Data were shared by Andy Mahoney and Andrew Einhorn via Google Drive and were downloaded as .zip files via the Google Drive web browser interface in July 2024 and deposited on SNAP's Poseidon storage:
`/workspace/Shared/Tech_Projects/landfast_sea_ice`

The above path is a backed up location and users should copy these data to their preferred location before proceeding, e.g.,
`scp "$USER"@poseidon.snap.uaf.edu://workspace/Shared/Tech_Projects/landfast_sea_ice/*.zip $INPUT_ZIP_DIR`

### Environment Variables
Set paths for the compressed / uncompressed data as needed, e.g.,:
```sh
export INPUT_ZIP_DIR=/beegfs/CMIP6/"$USER"/landfast_sea_ice_zips
export INPUT_DIR=/beegfs/CMIP6/"$USER"/landfast_sea_ice
```
Set paths for intermediate and output data products:
```sh
export SCRATCH_DIR=/beegfs/CMIP6/"$USER"/landfast_sea_ice_scratch
export OUTPUT_DIR=/beegfs/CMIP6/"$USER"/landfast_sea_ice_products
``` 

## Background
Per conversations with the involved PIs the most impactful and high yield data are monthly min/median/mean/max seaward landfast ice edge (aka **SLIE**) "fields" for three different 9-year summary periods: 1996-05, 2005-14, 2014-23. These results were updated July 2024 by the PI and the data reside separate `AllSeasonsAnalysis/MonthySLIEs_yyyy-yyyy` directories for each ice era and each ice region (Chukchi / Beaufort).

