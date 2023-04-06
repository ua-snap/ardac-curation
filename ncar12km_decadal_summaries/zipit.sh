#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: $0 path_to_directory path_to_zip_directory"
    exit 1
fi

directory="$1"
zip_directory="$2"

# loop over variables
for str in pcp snow_melt evap glacier_melt runoff tmin tmax sm1 sm2 sm3 iwe swe
do
    
    zip_file="${zip_directory}/${str}.zip"

    echo "Creating ${zip_file}"
    # delete zip archive if it exists already
    rm -f "${zip_file}"
    
    # create a zip file for the variable and add all tiffs with this string in their filename to the zip
    find "${directory}" -name "*${str}*.tif" -print0 | xargs -0 zip "${zip_file}"
done
