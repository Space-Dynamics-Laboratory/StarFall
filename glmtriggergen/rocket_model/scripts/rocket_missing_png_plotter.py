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
Script to plot energy data from NPY files that don't have associated PNG files.

This script:
1. Scans the rocket_positives directory for PNG and NPY files
2. Extracts datetime and cluster ID from filenames
3. Identifies NPY files without matching PNG files
4. Plots the energy data from unmatched NPY files
"""

import argparse
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PLOT_SCREEN_X_POS = 1000
PLOT_SCREEN_Y_POS = 100


def parse_filename(filename):
    """
    Parse filename to extract datetime and cluster ID.

    Args:
        filename (str): Filename to parse

    Returns:
        tuple: (datetime_str, cluster_id) or (None, None) if parsing fails
    """
    # Pattern to match: YYYYMMDDHHMMSS_clusterID_...
    pattern = r"^(\d{14})_(\d+(?:\.\d+)?)_"
    match = re.match(pattern, filename)

    if match:
        datetime_str = match.group(1)
        cluster_id = match.group(2)
        return datetime_str, cluster_id

    return None, None


def scan_directory(directory_path):
    """
    Scan directory for PNG and NPY files and categorize them.

    Args:
        directory_path (str): Path to the directory to scan

    Returns:
        tuple: (png_files_dict, npy_files_dict) where keys are (datetime, cluster_id)
    """
    png_files = defaultdict(list)
    npy_files = defaultdict(list)

    directory = Path(directory_path)

    if not directory.exists():
        raise FileNotFoundError(f"Directory '{directory_path}' does not exist")

    for file_path in directory.iterdir():
        if file_path.is_file():
            filename = file_path.name
            datetime_str, cluster_id = parse_filename(filename)

            if datetime_str and cluster_id:
                key = (datetime_str, cluster_id)

                if filename.lower().endswith(".png"):
                    png_files[key].append(file_path)
                elif (
                    filename.lower().endswith(".npy")
                    and "energy_lat_lon_array" in filename
                ):
                    npy_files[key].append(file_path)

    return dict(png_files), dict(npy_files)


def find_unmatched_npy_files(png_files_dict, npy_files_dict):
    """
    Find NPY files that don't have associated PNG files.

    Args:
        png_files_dict (dict): Dictionary of PNG files keyed by (datetime, cluster_id)
        npy_files_dict (dict): Dictionary of NPY files keyed by (datetime, cluster_id)

    Returns:
        list: List of NPY file paths without associated PNG files
    """
    unmatched_npy_files = []

    for key, npy_paths in npy_files_dict.items():
        if key not in png_files_dict:
            unmatched_npy_files.extend(npy_paths)

    return unmatched_npy_files


def plot_energy_data(
    npy_file_path, screen_x_position, screen_y_position, output_dir=None
):
    """
    Plot energy data from an NPY file in GOES-style format matching the original code.

    Args:
        npy_file_path (Path): Path to the NPY file
        output_dir (str): Optional directory to save plots
    """
    try:
        # Load the energy data
        energy_data = np.load(npy_file_path)

        # Extract datetime and cluster ID from filename for title
        datetime_str, cluster_id = parse_filename(npy_file_path.name)

        # Format datetime for display (matching original format)
        if datetime_str:
            dt = datetime.strptime(datetime_str, "%Y%m%d%H%M%S")
            formatted_datetime = dt.strftime("%Y/%m/%d %H:%M:%S.%f")[:-3] + " (UTC)"
        else:
            formatted_datetime = "Unknown Time (UTC)"

        # Create figure (matching original code style)
        fig = plt.figure(figsize=(8, 6))
        mngr = plt.get_current_fig_manager()
        mngr.canvas.manager.window.wm_geometry(
            f"+{screen_x_position}+{screen_y_position}"
        )

        # Convert to kW/sr (divide by 1000, matching original code)
        energy_kw_sr = energy_data[0]

        # Create time axis centered on peak intensity
        n_points = len(energy_kw_sr)
        peak_idx = np.argmax(energy_kw_sr)

        # Create a reasonable time range (adjust based on your data characteristics)
        time_relative = np.linspace(0, 1, n_points)
        # Center on the peak
        time_relative = time_relative - time_relative[peak_idx]

        # Plot with exact styling from original code
        plt.grid(True, which="major", linestyle="--")

        # Use tab:orange color (GOES 18.0 color from original)
        plt.plot(
            time_relative,
            energy_kw_sr,
            label=f"Cluster ID {cluster_id}" if cluster_id else "Cluster ID Unknown",
        )

        # Set labels exactly as in original code
        plt.xlabel("Observation Index Relative to Peak Intensity")
        plt.ylabel("Energy on Source (J)")

        # Set title exactly as in original code
        fig.suptitle(formatted_datetime)

        # Add legend
        plt.legend()

        # Save or display the plot
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            # Use naming convention similar to original code
            plot_filename = (
                f"{datetime_str}_{cluster_id}_i.png"
                if datetime_str and cluster_id
                else f"{npy_file_path.stem}_plot.png"
            )
            fig.savefig(output_path / plot_filename, dpi=150, bbox_inches="tight")
            print(f"Plot saved: {output_path / plot_filename}")
        else:
            plt.show()

        plt.close(fig)

    except Exception as e:
        print(f"Error plotting {npy_file_path.name}: {str(e)}")


def move_false_positive_files(directory_path, bad_positive_datetimes, verbose=False):
    """
    Move NPY files (without associated PNG files) matching bad positive datetimes to fps subdirectory.

    Args:
        directory_path (str): Path to the directory containing NPY files
        bad_positive_datetimes (list): List of datetime strings in YYYYMMDDHHMMSS format
        verbose (bool): Enable verbose output

    Returns:
        int: Number of files moved
    """
    directory = Path(directory_path)
    fps_dir = directory / "fps"

    # Create fps directory if it doesn't exist
    fps_dir.mkdir(exist_ok=True)

    # Get unmatched NPY files
    png_files, npy_files = scan_directory(directory_path)
    unmatched_npy_files = find_unmatched_npy_files(png_files, npy_files)

    moved_count = 0
    bad_datetime_set = set(bad_positive_datetimes)  # Convert to set for faster lookup

    for npy_file in unmatched_npy_files:
        # Extract datetime from filename
        datetime_str, _ = parse_filename(npy_file.name)

        if datetime_str and datetime_str in bad_datetime_set:
            # Move file to fps directory
            destination = fps_dir / npy_file.name
            try:
                npy_file.rename(destination)
                moved_count += 1
                if verbose:
                    print(f"Moved: {npy_file.name} -> fps/{npy_file.name}")
            except Exception as e:
                print(f"Error moving {npy_file.name}: {e}")

    return moved_count


def main():
    """Main function to execute the script."""
    parser = argparse.ArgumentParser(
        description="Plot energy data from NPY files without associated PNG files"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="rocket_positives",
        help="Directory containing PNG and NPY files (default: rocket_positives)",
    )
    parser.add_argument(
        "--directory",
        "-d",
        dest="alt_directory",
        help="Alternative way to specify directory containing PNG and NPY files",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output directory for saving plots (default: display plots)",
    )
    parser.add_argument(
        "--move-fps",
        "-m",
        action="store_true",
        help="Move false positive NPY files to fps subdirectory before plotting",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Use alternative directory if provided, otherwise use positional argument
    target_directory = args.alt_directory if args.alt_directory else args.directory

    # Convert to absolute path and validate
    target_path = Path(target_directory).resolve()

    # Define bad positive datetimes
    bad_positive_datetimes = [
        "20210114121210",
        "20230411185927",
        "20221222190731",
        "20190717210839",
        "20190716220359",
        "20231218142640",
        "20230822180941",
        "20230507115641",
        "20240712201150",
        "20210823115103",
        "20221221121359",
        "20230218170453",
        "20220416130306",
        "20200502184839",
        "20220301152536",
        "20190212070416",
        "20241120182410",
        "20230728052338",
        "20230512174020",
        "20210306170429",
        "20210102211022",
        "20241119182200",
        "20220202161626",
        "20190731212508",
        "20201117160332",
        "20210712145123",
        "20221201110055",
        "20220503221323",
        "20240731130118",
        "20220322211028",
        "20240618214140",
        "20220812210121",
    ]

    try:
        # Scan the directory
        print(f"Scanning directory: {target_path}")

        # Move false positives if requested
        if args.move_fps:
            print("\nMoving false positive files to fps subdirectory...")
            moved_count = move_false_positive_files(
                target_path, bad_positive_datetimes, args.verbose
            )
            print(f"Moved {moved_count} false positive files to fps/")

        # Re-scan after moving files
        png_files, npy_files = scan_directory(target_path)

        if args.verbose:
            print(f"Found {len(png_files)} unique PNG file groups")
            print(f"Found {len(npy_files)} unique NPY file groups")

        # Find unmatched NPY files
        unmatched_npy_files = find_unmatched_npy_files(png_files, npy_files)

        if not unmatched_npy_files:
            print(
                "No unmatched NPY files found. All NPY files have associated PNG files."
            )
            return

        print(f"\nFound {len(unmatched_npy_files)} unmatched NPY files:")
        for npy_file in unmatched_npy_files:
            print(f"  {npy_file.name}")

        # Plot energy data for each unmatched NPY file
        print("\nPlotting energy data...")
        for npy_file in unmatched_npy_files:
            if args.verbose:
                print(f"Processing: {npy_file.name}")
            plot_energy_data(
                npy_file, PLOT_SCREEN_X_POS, PLOT_SCREEN_Y_POS, args.output
            )

        print(f"\nCompleted processing {len(unmatched_npy_files)} files.")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
