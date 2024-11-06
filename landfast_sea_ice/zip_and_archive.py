import os
import subprocess
import sys

from config import (
    OUTPUT_DIR,
    BEAUFORT_DIR,
    CHUKCHI_DIR,
    DAILY_BEAUFORT_DIR,
    DAILY_CHUKCHI_DIR,
    BEAUFORT_NETCDF_DIR,
    CHUKCHI_NETCDF_DIR,
)

DEST_DIR = "/workspace/Shared/Tech_Projects/landfast_sea_ice"
SYMLINK_DIR = "/workspace/Shared/Tech_Projects/rasdaman_production_datasets"


def main():
    # prompt user to choose a directory to zip from those imported from config
    print("Choose a directory to compress:")
    print("1. Beaufort MMM")
    print("2. Chukchi MMM")
    print("3. Beaufort Daily SLIE")
    print("4. Chukchi Daily SLIE")
    print("5. Beaufort NetCDFs")
    print("6. Chukchi NetCDFs")
    print("7. All of the above")
    choice = input("Enter the number of the directory you want to compress: ")
    if choice == "1":
        dir_name = BEAUFORT_DIR
    elif choice == "2":
        dir_name = CHUKCHI_DIR
    elif choice == "3":
        dir_name = DAILY_BEAUFORT_DIR
    elif choice == "4":
        dir_name = DAILY_CHUKCHI_DIR
    elif choice == "5":
        dir_name = BEAUFORT_NETCDF_DIR
    elif choice == "6":
        dir_name = CHUKCHI_NETCDF_DIR
    elif choice == "7":
        dir_name = [
            BEAUFORT_DIR,
            CHUKCHI_DIR,
            DAILY_BEAUFORT_DIR,
            DAILY_CHUKCHI_DIR,
            BEAUFORT_NETCDF_DIR,
            CHUKCHI_NETCDF_DIR,
        ]
    else:
        print("Invalid choice.")
        sys.exit(1)

    if isinstance(dir_name, list):
        dir_names = dir_name
    else:
        dir_names = [dir_name]

    for directory in dir_names:
        # tar file should just have the name of the directory at the top level
        tar_file = f"{directory.name}.tar.gz"
        user = os.getenv("USER")

        # confirm details with the user
        print(f"Directory to be compressed: {directory}")
        print(f"The compressed file will be named: {tar_file}")
        print(f"It will be copied to: {user}@poseidon.snap.uaf.edu:{DEST_DIR}")
        print(f"A symlink will be created in: {SYMLINK_DIR}")
        confirmation = input("Is this information correct? (y/n): ")

        if confirmation.lower() != "y":
            print("Aborting operation.")
            sys.exit(1)

        # create the tar.gz file using pigz, 24 cores
        print("Compressing the directory...")
        tar_command = (
            f"tar -cf - {str(directory)} | pigz -p 24 > {OUTPUT_DIR}/{tar_file}"
        )
        result = subprocess.run(tar_command, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error during compression: {result.stderr}")
            sys.exit(1)

        # Copy the tar.gz file to the remote machine
        print(f"Copying compressed file to {user}@poseidon.snap.uaf.edu:{DEST_DIR}...")
        scp_command = [
            "scp",
            f"{OUTPUT_DIR}/{tar_file}",
            f"{user}@poseidon.snap.uaf.edu:{DEST_DIR}",
        ]
        result = subprocess.run(scp_command, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error during file copy: {result.stderr}")
            sys.exit(1)

        # Create a symlink on the remote machine
        print(f"Creating a symlink for the compressed file in {SYMLINK_DIR}...")
        ssh_command = [
            "ssh",
            f"{user}@poseidon.snap.uaf.edu",
            f"ln -sf {DEST_DIR}/{tar_file} {SYMLINK_DIR}/{directory.name}",
        ]
        result = subprocess.run(ssh_command, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error creating symlink: {result.stderr}")
            sys.exit(1)

        print("Successfully moved compressed file and created symlink.")


if __name__ == "__main__":
    main()
