"""Compute climatologies for a historical reference period by averaging over all years in the period. This module will leverage Dask and Dask Arrays to handle the reading of the 30 years of GeoTIFF data per degree day metric per model and scenario. The climatologies will be written to disk as GeoTIFFs in the climo_dir directory and eventually be used to compute deltas."""

from dask.distributed import LocalCluster, Client
import dask.array as da
import rasterio as rio

from config import models, scenarios, metrics, climo_dir, reprojected_dir

climo_start_year = 1981
climo_end_year = 2010

# we know from the EDA that this model is missing data
try:
    models.remove("HadGEM2-ES")
except:
    pass


def create_climo_file_groups():
    """Create lists of files for each model, scenario, and metric that are within the range of years provided by `climo_start_year` and `climo_end_year`."""
    file_groups = {}
    for model in models:
        for scenario in scenarios:
            for metric in metrics:
                # create a list of files for each model, scenario, and metric
                files = list(
                    reprojected_dir.glob(f"*{model}_{scenario}_{metric}_*.tif")
                )
                # filter out files not within the climatology period
                files = [
                    f
                    for f in files
                    if int(f.stem.split("_")[-1]) >= climo_start_year
                    and int(f.stem.split("_")[-1]) <= climo_end_year
                ]
                file_groups[(model, scenario, metric)] = files
    return file_groups


def compute_and_write_climos(file_groups):
    # each model/scenario combo gets its own climatology
    for (model, scenario, metric), files in file_groups.items():
        # read somewhere that chunking by full array size when data are small
        # can give you the benefits of chunking without too much overhead
        # this seems to go fast so I'm not going to worry about it for now
        arrays = [da.from_array(rio.open(f).read(1), chunks=(224, 317)) for f in files]
        assert len(arrays) == climo_end_year - climo_start_year + 1
        # stack data along the time axis
        stacked = da.stack(arrays, axis=0)
        # compute the mean along the time axis
        climo = stacked.mean(axis=0)
        # mean makes decimal noise, precision should be 0 for degree day metrics
        climo = climo.astype(int)
        # write the climatology to disk
        out_file = (
            climo_dir
            / f"{model}_{scenario}_{metric}_{climo_start_year}_{climo_end_year}_climo.tif"
        )
        with rio.open(files[0]) as src:
            profile = src.profile.copy()
            profile.update(
                dtype="int32",
                compress="deflate",
            )
            with rio.open(out_file, "w", **profile) as dst:
                dst.write(climo.compute(), 1)


def compute_and_write_daymet_climo():
    for metric in metrics:
        files = list(reprojected_dir.glob(f"*daymet_*{metric}*.tif"))
        # filter out files are within the climatology period
        files = [
            f
            for f in files
            if int(f.stem.split("_")[-1]) >= climo_start_year
            and int(f.stem.split("_")[-1]) <= climo_end_year
        ]
        arrays = [da.from_array(rio.open(f).read(1), chunks=(224, 317)) for f in files]
        assert len(arrays) == climo_end_year - climo_start_year + 1
        # stack data along the time axis
        stacked = da.stack(arrays, axis=0)
        # compute the mean along the time axis
        climo = stacked.mean(axis=0)
        # mean makes decimal noise, precision should be 0 for degree day metrics
        climo = climo.astype(int)
        # write the climatology to disk
        out_file = (
            climo_dir
            / f"daymet_historical_{metric}_{climo_start_year}_{climo_end_year}_climo.tif"
        )
        with rio.open(files[0]) as src:
            profile = src.profile.copy()
            profile.update(
                dtype="int32",
                compress="deflate",
            )
            with rio.open(out_file, "w", **profile) as dst:
                dst.write(climo.compute(), 1)


def compute_model_minus_daymet_deltas():
    # need to loop through metrics here

    for metric in metrics:

        climo_files = list(climo_dir.glob(f"*{metric}*.tif"))
        daymet_climo_file = list(climo_dir.glob(f"*daymet*{metric}*.tif"))[0]
        print(daymet_climo_file.name)

        # for each model climo file, subtract the daymet climo file with Dask
        daymet_climo_arr = da.from_array(
            rio.open(daymet_climo_file).read(1), chunks=(224, 317)
        )
        for model_climo in climo_files:
            print(model_climo.name)
            model_climo_arr = da.from_array(
                rio.open(model_climo).read(1), chunks=(224, 317)
            )
            delta = model_climo_arr - daymet_climo_arr
            out_file = climo_dir / f"{model_climo.stem}_minus_daymet_delta.tif"
            with rio.open(model_climo) as src:
                profile = src.profile.copy()
                profile.update(
                    dtype="int32",
                    nodata=0,
                    compress="deflate",
                )
                with rio.open(out_file, "w", **profile) as dst:
                    dst.write(delta.compute(), 1)


if __name__ == "__main__":
    cluster = LocalCluster()
    client = Client(cluster)

    file_groups = create_climo_file_groups()
    compute_and_write_climos(file_groups)
    compute_and_write_daymet_climo()
    compute_model_minus_daymet_deltas()

    client.close()
    cluster.close()
