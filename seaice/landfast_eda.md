# "The Landfast Sea Ice Data"
## Objective
The purpose of this document is a high-level distillation of the progress made toward identifying, collecting, and curating "the landfast sea ice data" for integration into the Arctic Data Collaborative (ARDAC). This document describes the current understanding of the data proposes the next step forward in making these data more broadly accessible and useful with the ultimate aim of to a wider variety of end-users.

## Background
An initial exploratory data analysis has been completed for two similar but incongruent archives of landfast sea ice data. The first archive are the "[Recurring Spring Leads and Landfast Ice in the Beaufort and Chukchi Seas](https://nsidc.org/data/g02173/versions/1)" data that are hosted by the NSIDC. The second archive are the data preserved locally on the SNAP file system. These data will hereafter be referred to as "ths NSIDC data" and "the InteRFACE data" for brevity. Note that the NSIDC data contain another sea ice variable: leads. The leads data are intentionally omitted from the discussion here.

### What is Landfast Sea Ice?
Landfast ice is sea ice that is mostly stationary and attached to land. Specifically, landfast ice is defined here as being continguous to the coast and lacking detectable motion for approximately 20 days. This defintion is consistent with the that provided by [Mahoney et al. (2005)](https://seaice.alaska.edu/gi/publications/mahoney/Mahoney_2005_POAC_DefiningLFI.pdf) and [Mahoney et al. (2007)](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2006JC003559), and the landfast sea ice data in InteRFACE data are the same data analyzed in the 2007 publication.

### Why Care About Landfast Sea Ice?
From Mahoney et al. (2007):
>In the Arctic, landfast sea ice is a key element of the coastal system, integral to a wide range of geological and biological processes as well as human activities. The presence of landfast ice can mitigate the effect of winter storms on the coast but also impede navigation in the spring. As well as being of great importance to native subsistence activities [Nelson, 1969; George et al., 2004], the presence or absence of landfast in northern Alaska and its stability are of considerable economic importance for offshore development.

### Source Data Attributes
The landfast ice data are derived from RADARSAT-1 data aquired using the the moderate-resolution ScanSAR operation mode of the synthetic aperture radar (SAR) sensor. The RADARSAT-1 mission (no longer active) used a C-Band (5.3 GHz), 5.6 cm wavelength, HH polarized microwave frequency to image the earth. RADARSAT-1 could "detect" landfast ice because it has a distinct backscatter signature compared to surrounding pack ice, land, or open water. Indiviudal ScarSAR passes were mosaicked together to generate a mosaic every two or three days resulting in 8 to 35 mosaics per annual ice cycle. Data processing details are provided by [Eicken et al. (2006)](https://nsidc.org/sites/nsidc.org/files/files/data/noaa/g02173/eicken_leads_landfast_2006.pdf).

### Spatial Attributes
The NSIDC data domain encomapsses northern Alaska and northwestern Canada and includes the Beaufort and Chukchi Seas. The InteRFACE data shares the same domain but also includes a set of western Chukchi data that include the northwest Arctic Coast of Alaska and the Seward Peninsula that is not included in the NSIDC data. The native spatial resolution (i.e., pixel size) of both data sets is 100 m x 100 m. Some small islands are masked from the analysis - although large islands such as Barter and Herschel Islands are included.

### Temporal Atrributes
Data are characterized by seaonal ice cyles (October to July) that encompass two calendar years, so 1998-1999 is a single ice season. Eight annnual (1996-2004) seasonal ice cycles are included in the NSIDC data. Nine (1999-2008) seasonal ice cycles are included in the InteRFACE data for the Beaufort region. Twelve (1996-2008) seasonal ice cycles are included in the InteRFACE data for the Chukchi region.

The landfast ice extent detected from a set of three SAR mosaics (spanning ~20 days) are the foundation of both the NSIDC and InteRFACE datasets. For example, a file named `r1998010-032_slie.tif` is the landfast sea ice extent for the period spanning day-of-year (DOY) 010, 1998, to DOY 32, 1998 (Jan. 10th to Feb. 1st).

## Initial Findings
### NSIDC Data
Compressed data were fetched from the NSIDC FTP service and 225 GeoTIFF files were extracted from the `data/binarized_geotiffs` directory. Each file represents an individual landfast ice exent scene for the year and DOY range indicated by the file name. Note that the [User Guide](https://nsidc.org/sites/default/files/g02173-v001-userguide.pdf) for this dataset refers to landfast ice in a few different ways. The term "Landfast Ice Extent" is used for the extent GeoTIFFs where values of `255` or `1` (white, see Figure 1) indicate landfast ice and values of `0` (black, see Figure 1) indicate land, open ocean, or non-landfast ice. However, the term "seaward looking landfast ice edge" (SLIE) is used in the file names themselves and is used in much the same context as "ice extent". Monthly summary (miniumum, mean, median, and maximum landfast ice extent) data are also available from this archive.

| ![NSIDC Binarized SLIE](nsidc_binarized_slie.png)|
|:--:|
| <i>Figure 1. Nine random samples of the NSIDC landfast ice extent "binarized GeoTIFF" collection. The date of each scene is in the format YYYY-DOY-DOY. The scenes represent the full extent of the NSIDC data, an area spanning the Beaufort coastline of Alaska and a small portion of the Chukchi coastline as well.</i>|

### InteRFACE Data
There are 216 GeoTIFF landfast ice extent files for the Chukchi region and 250 for the Beaufort region.. A sample of these data appear in Figures 2 and 3. Note that the data values for these scenes are different than what is in the NSIDC data. These data lack a consistent set of unique values. My interpretations of the raster vales are as follows:

 - 0: No SLIE is present for this pixel. This means either water, or sea ice that is not landfast.
 - 63, 64, 111, or some other value between 0 and 128: No data.
 - 128: A landmask. The landmask appears constant across each GeoTiff sampled thus far.
 - 255: Landfast Sea Ice

Monthly statistical summary rasters, annual stacks, and vectorized ice edge products are also available in this archive.

| ![Chukchi SLIE](chukchi_slie.png)|
|:--:|
| <i>Figure 2. Nine random samples of the InteRFACE Chukchi landfast ice extent data. The date of each scene is in the format YYYY-DOY-DOY.</i>|

| ![Beaufort SLIE](beaufort_slie.png)|
|:--:|
| <i>Figure 3. Nine random samples of the InteRFACE Beaufort landfast ice extent data. The date of each scene is in the format YYYY-DOY-DOY.</i>|

## Recommendation for ARDAC Integration
I recommend we prioritize create a unified landfast ice extent datacube for ingest into ARDAC via an integration with our array geodatabase (Rasdaman) and SNAP Data API. A discrete daily time index will serve as the "third dimension" of this datacube and be a mechanism by which users can request, slice, and access data. This will require mapping the DOY ranges provided by the GeoTIFF file names to this index to control for which data (Chukchi, Beaufort, both) are available for which times. This effort will also require determining the extent to which the NSDIC (Figure 1) and the InteRFACE-Beaufort (Figure 3) datasets are indentical. As there are different numbers of GeoTIFFs available from each, it is possible that one is a subset of the other. Whereever we are fusing the the InteRFACE data with the NSIDC data we'll need to prescribe a common set of categorical integer encodings (e.g., 128 is always the landmask). The ultimate outcome would be for a user to be able to query the dataset by a date or set of dates and retreive an internally consistent set of whatever landfast sea ice data exists for that period. In my opinion this work would represent a substantial upgrade to the accessiblty and usability of these datasets for technical users.

However, there are deeper levels to both of these datasets. Other candidates for ingest to ARDAC might include:
 - Monthly summaries (min/mean/max) of landfast ice extent (both NSIDC and InteRFACE)
 - Landfast Ice Width (InteRFACE)
 - Water Depth at SLIE or other bathymetry summaries (InteRFACE)
 - Ice Cycle Key Events (InteRFACE)
 - AVHRR "Leads" (NSDIC)

If any of these are to be ingested to ARDAC they'll need to be triaged by relevance, perceived usefulness to current research efforts, and estimated work effort.

## References

>Eicken, H., L. Shapiro, A. G. Gaylord, A. Mahoney, and P. W. Cotter. 2009. Recurring Spring Leads and Landfast Ice in the Beaufort and Chukchi Seas, 1993-2004, Version 1. Boulder, Colorado USA. NSIDC: National Snow and Ice Data Center. doi: https://doi.org/10.7265/N5SB43P0. Accessed July 2022.

>Mahoney, A., Eicken, H., Gaylord, A. G., and Shapiro, L. (2007), Alaska landfast sea ice: Links with bathymetry and atmospheric circulation, <i>J. Geophys. Res.,</i> 112, C02001, doi:10.1029/2006JC003559. 

>Mahoney, A., Eicken, H., Shapiro, L., & Graves, A. (2005). Defining and locating the seaward landfast ice edge in northern Alaska. In 18th International Conference on Port and Ocean Engineering under Arctic Conditions (POAC'05), Potsdam, NY (pp. 991-1001).

>Eicken, H., L. Shapiro, A. G. Gaylord, A. Mahoney, and P. Cotter. 2006. Mapping and Characterization of Recurring Spring Leads and Landfast Ice in the Beaufort and Chukchi Seas. Final Report, Minerals Management Service OCS Study MMS 2005-068.

>Eicken, H., L. Shapiro, A. G. Gaylord, A. Mahoney, and P. W. Cotter. 2009. Recurring Spring Leads and Landfast Ice in the Beaufort and Chukchi Seas, 1993-2004, Version 1. Boulder, Colorado USA. NSIDC: National Snow and Ice Data Center. doi: https://doi.org/10.7265/N5SB43P0. Accessed July 2022.





