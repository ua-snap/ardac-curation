import os
import zipfile

from config import INPUT_ZIP_DIR, INPUT_DIR


def list_zips():
    """List all zip files in the input directory.

    Args:
        None

    Returns:
        list: A list of zip files in the input directory.
    """
    return [f for f in INPUT_ZIP_DIR.iterdir() if f.suffix == ".zip"]


def unzip_files():
    """Unzip all zip files in the input directory.

    Args:
        None

    Returns:
        None
    """
    for zip_file in list_zips():
        with zipfile.ZipFile(zip_file, "r") as z:
            z.extractall(INPUT_DIR)
        os.remove(zip_file)


if __name__ == "__main__":
    unzip_files()
