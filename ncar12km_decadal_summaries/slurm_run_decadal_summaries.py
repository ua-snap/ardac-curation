import argparse

from generate_decadal_summaries import create_decadal_averages
from config import target_dirs


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", help="directory to save output GeoTIFF files")
    args = parser.parse_args()


    for target in target_dirs:
        create_decadal_averages(target, output_dir=args.output_dir, dry_run=False)
