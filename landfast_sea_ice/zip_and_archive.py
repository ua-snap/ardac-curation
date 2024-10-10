import os
import subprocess
import shutil
import sys

from config import (
    OUTPUT_DIR,
    BEAUFORT_DIR,  # MMM GeoTIFFs
    CHUKCHI_DIR,  # MMM GeoTIFFs
    DAILY_BEAUFORT_DIR,  # Daily SLIE GeoTIFFS
    DAILY_CHUKCHI_DIR,  # Daily SLIE GeoTIFFS
    BEAUFORT_NETCDF_DIR,
    CHUKCHI_NETCDF_DIR,
)

# Define constants
DEST_DIR = "/workspace/Shared/Tech_Projects/landfast_sea_ice"
SYMLINK_DIR = "/workspace/Shared/Tech_Projects/rasdaman_production_datasets"


def main():

    # prompt user to choose a directory to zip from those imported from config
    print("Choose a directory to zip:")
    print("1. Beaufort MMM")
    print("2. Chukchi MMM")
    print("3. Beaufort Daily SLIE")
    print("4. Chukchi Daily SLIE")
    print("5. Beaufort NetCDFs")
    print("6. Chukchi NetCDFs")
    print("7. All of the above")
    choice = input("Enter the number of the directory you want to zip: ")
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

    # zip file should just have the name of the directory at the top level
    zip_file = f"{dir_name.name}.zip"
    user = os.getenv("USER")

    # Confirm details with the user
    print(f"Directory to be zipped: {dir_name}")
    print(f"The zip file will be named: {zip_file}")
    print(f"It will be copied to: {user}@poseidon.snap.uaf.edu:{DEST_DIR}")
    print(f"A symlink will be created in: {SYMLINK_DIR}")
    confirmation = input("Is this information correct? (y/n): ")

    if confirmation.lower() != "y":
        print("Aborting operation.")
        sys.exit(1)

    # Create the zip file
    print("Zipping the directory...")
    try:
        shutil.make_archive(dir_name, "zip", dir_name)
    except FileNotFoundError:
        print(f"Error: The directory '{dir_name}' was not found.")
        sys.exit(1)

    # Copy the zip file to the remote machine
    print(f"Copying zip file to {user}@poseidon.snap.uaf.edu:{DEST_DIR}...")
    scp_command = [
        "scp",
        f"{OUTPUT_DIR}/{zip_file}",
        f"{user}@poseidon.snap.uaf.edu:{DEST_DIR}",
    ]
    result = subprocess.run(scp_command, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error during file copy: {result.stderr}")
        sys.exit(1)

    # Create a symlink on the remote machine
    print(f"Creating a symlink for the zip file in {SYMLINK_DIR}...")
    ssh_command = [
        "ssh",
        f"{user}@poseidon.snap.uaf.edu",
        f"ln -s {DEST_DIR}/{zip_file} {SYMLINK_DIR}/{dir_name.name}",
    ]
    result = subprocess.run(ssh_command, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error creating symlink: {result.stderr}")
        sys.exit(1)

    print("Succesfully moved zip file and created symlink.")


if __name__ == "__main__":
    main()
