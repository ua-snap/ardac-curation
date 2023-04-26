#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: $0 source_directory target_directory"
    exit 1
fi

source_directory=$1
target_directory=$2

for dir in "$source_directory"/IEM_MRI_45_mo "$source_directory"/IEM_NCAR_45_mo "$source_directory"/IEM_MRI_85_mo "$source_directory"/IEM_NCAR_85_mo; do

    if [ "$(find "$dir" -mindepth 1 -maxdepth 1 -type d)" ]; then
        echo "$dir has subdirectories:"
        for sub_dir in "$dir"/*/; do
            echo "Unzipping data in $sub_dir ..."
            parent_dir=$(basename "$sub_dir")
            for zip_file in "$sub_dir"*.zip; do                
                unzip -q -j "$zip_file" -d "$target_directory"
                for extracted_file in "$target_directory"/*.tif; do
                    new_filename="${parent_dir}_${extracted_file##*/}"
                    mv "$extracted_file" "$target_directory/renamed/$new_filename"
                done
            done
        done
    else
        echo "$dir does not have subdirectories."
    fi
done


