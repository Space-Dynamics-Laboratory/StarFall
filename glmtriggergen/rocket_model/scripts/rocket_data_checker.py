################################################################################################
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#################################################################################################

"""
ROCKET Data Checker

This script manages PNG files and their associated NPY data files by:
1. Finding all PNG files in a specified directory
2. Displaying each PNG file to the user
3. Asking if the associated satellite data should be kept
4. Moving unwanted files to another designated directory
"""

import glob
import os
import re
import shutil
from datetime import datetime

import matplotlib.pyplot as plt

SOURCE_DIR_STRING = "/home/developer/glmtriggergen/data/output/rocket_positives/"
TARGET_DIR_STRING = "/home/developer/glmtriggergen/data/output/rocket_positives/fps/"

PLOT_SCREEN_X_POS = 1000
PLOT_SCREEN_Y_POS = 100


class RocketDataChecker:
    """RocketDataChecker
    Main class for running the ROCKET Data Checker
    """

    def __init__(self, source_dir, target_dir, start_date=None):
        """
        Initialize the ROCKET Data Checker.

        Args:
            source_dir (str): Directory containing the PNG and NPY files
            target_dir (str): Directory to move unwanted files
            start_date (str): Starting date in YYYYMMDDHHMMSS format. Files before this date will be skipped.
        """
        self.source_dir = os.path.abspath(source_dir)
        self.target_dir = os.path.abspath(target_dir)
        self.start_date = start_date

        # Ensure the target directory exists
        os.makedirs(self.target_dir, exist_ok=True)

        # Regular expression to extract components from filenames
        self.png_pattern = re.compile(r"(\d+)_(\d+\.\d+)_(\d+\.\d+)_i\.png")
        self.npy_pattern = re.compile(
            r"(\d+)_(\d+\.\d+)_(\d+\.\d+)_energy_lat_lon_array\.npy"
        )

        # Get list of all PNG and NPY files in the source directory
        self.png_files = glob.glob(os.path.join(self.source_dir, "*.png"))
        self.npy_files = glob.glob(os.path.join(self.source_dir, "*.npy"))

        # Filter files by start date if provided
        if self.start_date:
            self.filter_files_by_date()

        # Sort PNG files in decreasing order of date and time
        self.sort_png_files_by_datetime(descending=False)

        # Count files in the directories
        (
            self.src_png_file_count,
            self.target_png_file_count,
            self.src_npy_file_count,
            self.target_npy_file_count,
        ) = self.count_files_in_dirs()

    def extract_png_info(self, filename):
        """Extract date_time and cluster_id from PNG filename."""
        basename = os.path.basename(filename)
        match = self.png_pattern.match(basename)
        if match:
            date_time, cluster_id, rank = match.groups()
            return date_time, cluster_id, rank
        return None, None, None

    def validate_date_format(self, date_str):
        """
        Validate that the date string is in YYYYMMDDHHMMSS format.

        Args:
            date_str (str): Date string to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not date_str or len(date_str) != 14:
            return False

        try:
            # Try to parse the date to ensure it's valid
            datetime.strptime(date_str, "%Y%m%d%H%M%S")
            return True
        except ValueError:
            return False

    def format_date_display(self, date_str):
        """
        Format date string for display purposes.

        Args:
            date_str (str): Date string in YYYYMMDDHHMMSS format

        Returns:
            str: Formatted date string for display
        """
        try:
            dt = datetime.strptime(date_str, "%Y%m%d%H%M%S")
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return date_str

    def filter_files_by_date(self):
        """
        Filter PNG and NPY files to only include those on or after the start date.
        """
        if not self.start_date:
            return

        original_png_count = len(self.png_files)
        original_npy_count = len(self.npy_files)

        # Filter PNG files
        self.png_files = [
            png_file
            for png_file in self.png_files
            if self.is_file_after_start_date(png_file, is_png=True)
        ]

        # Filter NPY files
        self.npy_files = [
            npy_file
            for npy_file in self.npy_files
            if self.is_file_after_start_date(npy_file, is_png=False)
        ]

        filtered_png_count = original_png_count - len(self.png_files)
        filtered_npy_count = original_npy_count - len(self.npy_files)

        if filtered_png_count > 0 or filtered_npy_count > 0:
            print(
                f"Filtered out {filtered_png_count} PNG files and {filtered_npy_count} NPY files before start date"
            )

    def is_file_after_start_date(self, file_path, is_png=True):
        """
        Check if a file's date is on or after the start date.

        Args:
            file_path (str): Path to the file
            is_png (bool): True if PNG file, False if NPY file

        Returns:
            bool: True if file should be processed, False if it should be skipped
        """
        if not self.start_date:
            return True

        if is_png:
            date_time, _, _ = self.extract_png_info(file_path)
        else:
            date_time, _, _ = self.extract_npy_info(file_path)

        if not date_time:
            return True  # Include files that don't match the expected pattern

        return int(date_time) >= int(self.start_date)

    def sort_png_files_by_datetime(self, descending=True):
        """
        Sorts in place the PNG files by date and time in the filename.

        Args:
            descending (bool): If True, sort in decreasing order (newest first)
        """

        def get_datetime(file_path):
            date_time, _, _ = self.extract_png_info(file_path)
            if date_time:
                return int(date_time)  # Convert to integer for proper numerical sorting
            return 0  # Default value for files that don't match the pattern

        self.png_files.sort(key=get_datetime, reverse=descending)

        if len(self.png_files) > 0:
            if descending:
                print("\nPNG files sorted by date and time (newest first)")
            else:
                print("\nPNG files sorted by date and time (oldest first)")

    def extract_npy_info(self, filename):
        """Extract date_time, cluster_id, and satellite_id from NPY filename."""
        basename = os.path.basename(filename)
        match = self.npy_pattern.match(basename)
        if match:
            date_time, cluster_id, satellite_id = match.groups()
            return date_time, cluster_id, satellite_id
        return None, None, None

    def find_associated_npy_files(self, png_file):
        """Find all NPY files associated with a PNG file based on date_time and cluster_id."""
        date_time, cluster_id, _ = self.extract_png_info(png_file)
        associated_files = []

        for npy_file in self.npy_files:
            npy_date_time, npy_cluster_id, _ = self.extract_npy_info(npy_file)
            if date_time == npy_date_time and cluster_id == npy_cluster_id:
                associated_files.append(npy_file)

        return associated_files

    def display_image(self, png_file, screen_x_position, screen_y_position):
        """Display a PNG image to the user."""
        plt.figure(figsize=(10, 8))
        mngr = plt.get_current_fig_manager()
        mngr.canvas.manager.window.wm_geometry(
            f"+{screen_x_position}+{screen_y_position}"
        )
        plt.imshow(plt.imread(png_file))
        plt.title(f"File: {os.path.basename(png_file)}")
        plt.axis("off")
        plt.tight_layout()
        plt.show(block=False)
        plt.waitforbuttonpress()
        plt.close("all")

    def move_files(self, files_to_move):
        """Move specified files to the target directory."""
        for file_path in files_to_move:
            target_path = os.path.join(self.target_dir, os.path.basename(file_path))
            shutil.move(file_path, target_path)
            print(f"Moved {os.path.basename(file_path)} to {self.target_dir}")

    def check_file_counts(self):
        """Checks that all files are still accounted for."""

        # Count files in the directories
        (
            src_png_file_count,
            target_png_file_count,
            src_npy_file_count,
            target_npy_file_count,
        ) = self.count_files_in_dirs()

        # Count files
        total_png_file_count = src_png_file_count + target_png_file_count
        total_npy_file_count = src_npy_file_count + target_npy_file_count
        original_png_file_count = self.src_png_file_count + self.target_png_file_count
        original_npy_file_count = self.src_npy_file_count + self.target_npy_file_count

        if (
            total_png_file_count == original_png_file_count
            and total_npy_file_count == original_npy_file_count
        ):
            print(
                f"\nTotal number of PNG files ({total_png_file_count}) and "
                + f"NPY files ({total_npy_file_count}) match original counts."
            )
        else:
            print(
                f"\nTotal number of PNG files ({total_png_file_count}) and "
                + f"NPY files ({total_npy_file_count}) do NOT match "
                + f"original counts ({original_png_file_count} and "
                + f"{original_npy_file_count}, respectively)."
            )

    def count_files_in_dirs(self):
        """Counts all PNG and NPY files in the source and target dirs

        Returns:
            Tuple: Counts of PNG and NPY files in source and target, e.g.,
            (len(src_png_files), len(target_png_files), len(src_npy_files),  len(target_npy_files))
        """
        # Get list of all PNG and NPY files in the source directory
        src_png_files = glob.glob(os.path.join(self.source_dir, "*.png"))
        src_npy_files = glob.glob(os.path.join(self.source_dir, "*.npy"))

        # Get list of all PNG and NPY files in the target directory
        target_png_files = glob.glob(os.path.join(self.target_dir, "*.png"))
        target_npy_files = glob.glob(os.path.join(self.target_dir, "*.npy"))

        # Store the file counts
        src_png_file_count = len(src_png_files)
        src_npy_file_count = len(src_npy_files)
        target_png_file_count = len(target_png_files)
        target_npy_file_count = len(target_npy_files)

        print(
            f"\nFound {src_png_file_count} PNG files and "
            + f"{src_npy_file_count} NPY files in {self.source_dir}"
        )
        print(
            f"Found {target_png_file_count} PNG files and "
            + f"{target_npy_file_count} NPY files in {self.target_dir}"
        )

        # Return file counts
        return (
            src_png_file_count,
            target_png_file_count,
            src_npy_file_count,
            target_npy_file_count,
        )

    def process_files(self):
        """Process all PNG files and their associated NPY files."""
        total_files = len(self.png_files)

        for file_index, png_file in enumerate(self.png_files, 1):
            png_basename = os.path.basename(png_file)
            print(f"\nProcessing {png_basename} ({file_index}/{total_files})")

            # Display the PNG file to the user
            self.display_image(png_file, PLOT_SCREEN_X_POS, PLOT_SCREEN_Y_POS)

            # Ask if the data should be kept
            keep_response = (
                input(f"Keep data for {png_basename}? ([Y]/N): ").strip().upper()
            )

            if keep_response != "N":
                print(f"Keeping {png_basename} and associated data files.")
                continue

            # Find all associated NPY files
            associated_npy_files = self.find_associated_npy_files(png_file)

            if len(associated_npy_files) == 0:
                print(f"No NPY files found associated with {png_basename}")
                # Move just the PNG file
                self.move_files([png_file])
                continue

            if len(associated_npy_files) == 1:
                # Move the PNG file and its associated NPY file
                self.move_files([png_file, associated_npy_files[0]])
            else:
                # Ask about each satellite data file individually
                print(
                    f"Found {len(associated_npy_files)} satellite data files associated with {png_basename}"
                )
                files_to_move = [png_file]  # Start with the PNG file

                for npy_file in associated_npy_files:
                    npy_basename = os.path.basename(npy_file)
                    _, _, satellite_id = self.extract_npy_info(npy_file)

                    sat_response = (
                        input(
                            f"Keep satellite data {satellite_id} ({npy_basename})? ([Y]/N): "
                        )
                        .strip()
                        .upper()
                    )

                    if sat_response == "N":
                        files_to_move.append(npy_file)

                # Move the unwanted files
                if (
                    len(files_to_move) > 1
                ):  # Only move if at least one NPY file is to be moved
                    self.move_files(files_to_move)


def main():
    """ "
    This executes the main process of the ROCKET Data Checker
    """
    print("=" * 80)
    print("ROCKET Data Checker")
    print("=" * 80)

    source_dir = SOURCE_DIR_STRING
    target_dir = TARGET_DIR_STRING

    # If not specified, get directory paths from user
    if SOURCE_DIR_STRING == "":
        source_dir = input("Enter the source directory path: ").strip()
    if TARGET_DIR_STRING == "":
        target_dir = input("Enter the target directory for unwanted files: ").strip()

    if not os.path.isdir(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return

    if not os.path.isdir(target_dir):
        print(f"Error: Target directory '{target_dir}' does not exist.")
        return

    # Get optional start date from user
    start_date = None
    start_date_input = input(
        "Enter starting date (YYYYMMDDHHMMSS format) or press Enter to process all files: "
    ).strip()

    if start_date_input:
        # Create a temporary manager instance to validate the date
        temp_manager = RocketDataChecker(".", ".")
        if temp_manager.validate_date_format(start_date_input):
            start_date = start_date_input
            print(
                f"Will process files from {temp_manager.format_date_display(start_date)} onwards"
            )
        else:
            print(
                "Invalid date format. Please use YYYYMMDDHHMMSS format (e.g., 20180508022713)"
            )
            print("Processing all files instead...")

    # Initialize and run the manager
    manager = RocketDataChecker(source_dir, target_dir, start_date)

    if len(manager.png_files) == 0:
        print("No PNG files found to process.")
        return

    if start_date:
        print(
            f"Processing files from {manager.format_date_display(start_date)} onwards"
        )

    manager.process_files()

    # Check file counts
    manager.check_file_counts()

    print("\nProcessing complete!")


if __name__ == "__main__":
    main()
