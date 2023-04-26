#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: $0 path_to_source_directory path_to_unzipped_directory"
    exit 1
fi

source_directory="$1"
target_directory="$2"

for directory in "${source_directory}"/*/; do
    if [[ "${directory}" != *"mo/"* ]]; then
        for zip_file in "${directory}"*.zip; do
            if [ -f "${zip_file}" ]; then
                echo "Unzipping ${directory} ..."
                unzip -j -q "${zip_file}" -d "${target_directory}"
            fi
        done
    fi
done
