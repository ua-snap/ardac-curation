#!/bin/bash

# if [ $# -ne 1 ]; then
#     echo "Usage: $0 target_directory"
#     exit 1
# fi

# target_directory="$1"

# unzip -j -q /atlas_scratch/ssmarchenko/ssmarchenko_home/2022_IEM_proj/IEM_MRI_85_mo/_01mo_gipl2_mmgt_MRI-CGCM3-RCP85_2006_2100.zip -d "${target_directory}"

# unzip -j -q /atlas_scratch/ssmarchenko/ssmarchenko_home/2022_IEM_proj/IEM_MRI_85_mo/_02mo_gipl2_mmgt_MRI-CGCM3-RCP85_2006_2100.zip -d "${target_directory}"

# unzip -j -q /atlas_scratch/ssmarchenko/ssmarchenko_home/2022_IEM_proj/IEM_MRI_85_mo/_03mo_gipl2_mmgt_MRI-CGCM3_rcp85_2006_2100.zip -d "${target_directory}"

# unzip -j -q /atlas_scratch/ssmarchenko/ssmarchenko_home/2022_IEM_proj/IEM_MRI_85_mo/_04mo_gipl2_mmgt_MRI-CGCM3_rcp85_2006_2100.zip -d "${target_directory}"

# unzip -j -q /atlas_scratch/ssmarchenko/ssmarchenko_home/2022_IEM_proj/IEM_MRI_85_mo/_05mo_gipl2_mmgt_MRI-CGCM3_rcp85_2006_2100.zip -d "${target_directory}"

# unzip -j -q /atlas_scratch/ssmarchenko/ssmarchenko_home/2022_IEM_proj/IEM_MRI_85_mo/_06mo_gipl2_mmgt_MRI-CGCM3_rcp85_2006_2100.zip -d "${target_directory}"

# unzip -j -q /atlas_scratch/ssmarchenko/ssmarchenko_home/2022_IEM_proj/IEM_MRI_85_mo/_07mo_gipl2_mmgt_MRI-CGCM3_rcp85_2006_2100.zip -d "${target_directory}"

# unzip -j -q /atlas_scratch/ssmarchenko/ssmarchenko_home/2022_IEM_proj/IEM_MRI_85_mo/_08mo_gipl2_mmgt_MRI-CGCM3_rcp85_2006_2100.zip -d "${target_directory}"

# unzip -j -q /atlas_scratch/ssmarchenko/ssmarchenko_home/2022_IEM_proj/IEM_MRI_85_mo/_09mo_gipl2_mmgt_MRI-CGCM3_rcp85_2006_2100.zip -d "${target_directory}"

# unzip -j -q /atlas_scratch/ssmarchenko/ssmarchenko_home/2022_IEM_proj/IEM_MRI_85_mo/_10mo_gipl2_mmgt_MRI-CGCM3_rcp85_2006_2100.zip -d "${target_directory}"

# unzip -j -q /atlas_scratch/ssmarchenko/ssmarchenko_home/2022_IEM_proj/IEM_MRI_85_mo/_11mo_gipl2_mmgt_MRI-CGCM3_rcp85_2006_2100.zip -d "${target_directory}"

# unzip -j -q /atlas_scratch/ssmarchenko/ssmarchenko_home/2022_IEM_proj/IEM_MRI_85_mo/_12mo_gipl2_mmgt_MRI-CGCM3_rcp85_2006_2100.zip -d "${target_directory}"

if [ $# -ne 1 ]; then
    echo "Usage: $0 target_directory"
    exit 1
fi

target_directory="$1"

for zip_file in /atlas_scratch/ssmarchenko/ssmarchenko_home/2022_IEM_proj/IEM_MRI_85_mo/*.zip; do
    unzip -j -q "$zip_file" -d "$target_directory"
done

for zip_file in /atlas_scratch/ssmarchenko/ssmarchenko_home/2022_IEM_proj/IEM_NCAR_85_mo/*.zip; do
    unzip -j -q "$zip_file" -d "$target_directory"
done
