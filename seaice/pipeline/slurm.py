"""Helper functions for writing Slurm scripts for data processing. Functions should get called from the pipeline processing notebook. Each Slurm function calls out to a Python script."""


def write_sbatch(
    ncpus, slurm_email, slurm_dir, ac_conda_env, fp, profile, project_dir, output_dir
):
    """Write the SBATCH `.slurm` scripts to perform raster value consolidation.

    Args:
        ncpus (int): number of cpus to allocate per job
        slurm_email (str): email address for sending slurm messages
        slurm_dir (PosixPath): path to directory to write sbatch .slurm files
        ac_conda_env (str): name of the conda env that has anaconda-project installed
        fp (PosixPath): path to GeoTIFF file that will have its values fixed
        profile (dict-like object): profile used to create new GeoTIFF
        project_dir (str): path to directory of this anaconda-project project
        output_dir (PosixPath): path to intermediate results directory

    Returns:
        filepath of `.slurm` script
    """
    head = (
        "#!/bin/sh\n"
        + "#SBATCH --nodes=1\n"
        + f"#SBATCH --cpus-per-task={ncpus}\n"
        + "#SBATCH --account=snap\n"
        + "#SBATCH --mail-type=FAIL\n"
        + f"#SBATCH --mail-user={slurm_email}\n"
        + f"#SBATCH --output={slurm_dir}/{fp.name.replace('.tif', '_slurm_%j.out')}\n"
        + "#SBATCH -p main\n\n"
    )

    args = (
        # print start time
        "echo Start slurm && date\n"
        # initialize shell to use conda,
        'eval "$(conda shell.bash hook)"\n'
        # activate env with anaconda-project installed
        f"conda activate {ac_conda_env}\n"
        # call the python script that fixes the array values
        f"anaconda-project run python {project_dir}/fix_raster_values.py -d {fp} -p {profile} -o {output_dir}\n"
    )

    slurm_fp = slurm_dir.joinpath(fp.name.replace(".tif", "_fix_raster_values.slurm"))
    with open(slurm_fp, "w") as f:
        f.write(head + args)

    return slurm_fp


def write_case_b(
    ncpus,
    slurm_email,
    slurm_dir,
    ac_conda_env,
    dt,
    ts,
    project_dir,
    mask_dir,
    src_dir,
    output_dir,
):
    """Write the SBATCH `.slurm` scripts to merge data for Case B timestamps.

    Args:
        ncpus (int): number of cpus to allocate per job
        slurm_email (str): email address for sending slurm messages
        slurm_dir (PosixPath): path to directory to write sbatch .slurm files
        ac_conda_env (str): name of the conda env that has anaconda-project installed
        dt (PosixPath): path to a pickled dict that maps data files to a TimeStamp
        ts (Timestamp): Pandas Timestamp object used as a key for the above dict to find data.
        project_dir (str): path to directory of this anaconda-project project
        mask_dir (PosixPath): path to previously created regional masks
        src_dir (PosixPath): path to input data directory
        output_dir (PosixPath): path to final results directory

    Returns:
        filepath of `.slurm` script
    """
    slurmout = str(ts).split(" ")[0]
    head = (
        "#!/bin/sh\n"
        + "#SBATCH --nodes=1\n"
        + f"#SBATCH --cpus-per-task={ncpus}\n"
        + "#SBATCH --account=snap\n"
        + "#SBATCH --mail-type=FAIL\n"
        + f"#SBATCH --mail-user={slurm_email}\n"
        + f"#SBATCH --output={slurm_dir}/{slurmout}_%j.out\n"
        + "#SBATCH -p main\n\n"
    )

    args = (
        # print start time
        "echo Start slurm && date\n"
        # initialize shell to use conda,
        'eval "$(conda shell.bash hook)"\n'
        # activate env with anaconda-project installed
        f"conda activate {ac_conda_env}\n"
        # call the python script that merges data for a given date
        f"anaconda-project run python {project_dir}/single_raster_single_region.py -dt {dt} -ts \042{ts}\042 -m {mask_dir} -src {src_dir} -o {output_dir}\n"
    )

    slurm_fp = slurm_dir.joinpath(
        str(ts).split(" ")[0] + "_single_raster_single_region.slurm"
    )
    with open(slurm_fp, "w") as f:
        f.write(head + args)

    return slurm_fp


def write_case_c(
    ncpus,
    slurm_email,
    slurm_dir,
    ac_conda_env,
    dt,
    ts,
    project_dir,
    mask_dir,
    max_dir,
    src_dir,
    output_dir,
):
    """Write the SBATCH `.slurm` scripts to merge data for Case C timestamps

    Args:
        ncpus (int): number of cpus to allocate per job
        slurm_email (str): email address for sending slurm messages
        slurm_dir (PosixPath): path to directory to write sbatch .slurm files
        ac_conda_env (str): name of the conda env that has anaconda-project installed
        dt (PosixPath): path to a pickled dict that maps data files to a TimeStamp
        ts (Timestamp): Pandas Timestamp object used as a key for the above dict to find data.
        project_dir (str): path to directory of this anaconda-project project
        mask_dir (PosixPath): path to previously created regional masks
        max_dir (PosixPath): path to intermediate results directory
        src_dir (PosixPath): path to input data directory
        output_dir (PosixPath): path to final results directory

    Returns:
        filepath of `.slurm` script
    """
    slurmout = str(ts).split(" ")[0]
    head = (
        "#!/bin/sh\n"
        + "#SBATCH --nodes=1\n"
        + f"#SBATCH --cpus-per-task={ncpus}\n"
        + "#SBATCH --account=snap\n"
        + "#SBATCH --mail-type=FAIL\n"
        + f"#SBATCH --mail-user={slurm_email}\n"
        + f"#SBATCH --output={slurm_dir}/{slurmout}_%j.out\n"
        + "#SBATCH -p main\n\n"
    )

    args = (
        # print start time
        "echo Start slurm && date\n"
        # initialize shell to use conda,
        'eval "$(conda shell.bash hook)"\n'
        # activate env with anaconda-project installed
        f"conda activate {ac_conda_env}\n"
        # call the python script that merges data for a given date
        f"anaconda-project run python {project_dir}/many_rasters_single_region.py -dt {dt} -ts \042{ts}\042 -m {mask_dir} -mx  {max_dir} -src {src_dir} -o {output_dir}\n"
    )

    slurm_fp = slurm_dir.joinpath(
        str(ts).split(" ")[0] + "_many_rasters_single_region.slurm"
    )
    with open(slurm_fp, "w") as f:
        f.write(head + args)

    return slurm_fp


def write_case_d(
    ncpus,
    slurm_email,
    slurm_dir,
    ac_conda_env,
    dt,
    ts,
    project_dir,
    mask_dir,
    max_dir,
    src_dir,
    output_dir,
):
    """Write the SBATCH `.slurm` scripts to merge data for Case D timestamps.

    Args:
        ncpus (int): number of cpus to allocate per job
        slurm_email (str): email address for sending slurm messages
        slurm_dir (PosixPath): path to directory to write sbatch .slurm files
        ac_conda_env (str): name of the conda env that has anaconda-project installed
        dt (PosixPath): path to a pickled dict that maps data files to a TimeStamp
        ts (Timestamp): Pandas Timestamp object used as a key for the above dict to find data.
        project_dir (str): path to directory of this anaconda-project project
        mask_dir (PosixPath): path to previously created regional masks
        max_dir (PosixPath): path to intermediate results directory for time series maximums
        src_dir (PosixPath): path to input data directory
        output_dir (PosixPath): path to final results directory

    Returns:
        filepath of `.slurm` script
    """
    slurmout = str(ts).split(" ")[0]
    head = (
        "#!/bin/sh\n"
        + "#SBATCH --nodes=1\n"
        + f"#SBATCH --cpus-per-task={ncpus}\n"
        + "#SBATCH --account=snap\n"
        + "#SBATCH --mail-type=FAIL\n"
        + f"#SBATCH --mail-user={slurm_email}\n"
        + f"#SBATCH --output={slurm_dir}/{slurmout}_%j.out\n"
        + "#SBATCH -p main\n\n"
    )

    args = (
        # print start time
        "echo Start slurm && date\n"
        # initialize shell to use conda,
        'eval "$(conda shell.bash hook)"\n'
        # activate env with anaconda-project installed
        f"conda activate {ac_conda_env}\n"
        # call the python script that merges data for a given date
        f"anaconda-project run python {project_dir}/many_rasters_both_regions.py -dt {dt} -ts \042{ts}\042 -m {mask_dir} -mx  {max_dir} -src {src_dir} -o {output_dir}\n"
    )

    slurm_fp = slurm_dir.joinpath(
        str(ts).split(" ")[0] + "_many_rasters_both_regions.slurm"
    )
    with open(slurm_fp, "w") as f:
        f.write(head + args)

    return slurm_fp
