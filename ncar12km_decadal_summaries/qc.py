import os
import csv
import numpy as np
import dask.array as da
import rasterio as rio
import argparse
import tqdm
from pathlib import Path

def make_list_of_tiffs(directory):
    files = [f for f in os.listdir(directory) if f.endswith(".tif")]
    return files


def process_file(file, variable_data, directory):
    with rio.open(Path(directory) / file) as src:
        data = src.read(1)
        data = da.from_array(data, chunks=data.shape)
        min_val = np.round(np.nanmin(data), 1).compute()
        mean_val = np.round(np.nanmean(data), 1).compute()
        max_val = np.round(np.nanmax(data), 1).compute()

        variable = file.split("_")[0]
        if variable not in variable_data:
            # Initialize the data for this variable
            variable_data[variable] = {
                "metadata": src.meta.copy(),
                "files": [],
                "min_values": [],
                "mean_values": [],
                "max_values": [],
            }
        else:
            # Compare the metadata from the first file with the current file
            if src.meta != variable_data[variable]["metadata"]:
                raise Exception(f"Metadata for file {file} does not match")
            variable_data[variable]["files"].append(file)
            variable_data[variable]["min_values"].append(min_val)
            variable_data[variable]["mean_values"].append(mean_val)
            variable_data[variable]["max_values"].append(max_val)


def qc_files(files, directory):
    variable_data = {}
    for tiff in tqdm.tqdm(files, desc="Processing files..."):
        process_file(tiff, variable_data, directory)
    # Write the statistics for each variable to a separate CSV file
    for variable, qcdata in variable_data.items():
        with open(f"{variable}_statistics.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(["File", "Min", "Mean", "Max"])
            for i, tiff_file in enumerate(qcdata["files"]):
                writer.writerow(
                    [
                        tiff_file,
                        qcdata["min_values"][i],
                        qcdata["mean_values"][i],
                        qcdata["max_values"][i],
                    ]
                )
    print("Processing complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a directory of GeoTIFFs")
    parser.add_argument(
        "directory", help="The path to the directory containing the GeoTIFFs"
    )
    args = parser.parse_args()
    files_to_qc = make_list_of_tiffs(args.directory)
    qc_files(files_to_qc, args.directory)
