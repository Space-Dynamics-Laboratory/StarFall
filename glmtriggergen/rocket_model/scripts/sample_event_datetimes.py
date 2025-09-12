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
Randomly sample event datetimes from a txt file.

Example usage:
python rocket_model/scripts/sample_event_datetimes.py
    DateTime Random Sampler
    -------------------------
    Default input file: sdlGlmPositives_2025_05_14.txt
    Current directory: /home/developer/glmtriggergen
    ⚠ Default file not found - you'll need to specify the path

    Enter input file path (press Enter for default):
      /home/developer/glmtriggergen/data/input/rocket_data/sdlGlmPositives_2025_07_31.txt
    Enter output file path (press Enter for 'sampled_datetimes.txt'):
      /home/developer/glmtriggergen/data/input/rocket_data/sampled_datetimes_2025_07_31.txt
    Enter number of datetimes to sample: 100
    Found 3689 datetime entries in
      /home/developer/glmtriggergen/data/input/rocket_data/sdlGlmPositives_2025_07_31.txt
    Successfully sampled 100 datetime entries
    Results saved to: /home/developer/glmtriggergen/data/input/rocket_data/sampled_datetimes_2025_07_31.txt
"""

import os
import random
import sys


def find_input_file(filename):
    """
    Try to find the input file in various common locations.

    Args:
        filename (str): Name of the file to find

    Returns:
        str: Full path to the file if found, None otherwise
    """
    # List of common locations to check
    search_paths = [
        ".",  # Current directory
        "./data",  # data subdirectory
        "./files",  # files subdirectory
        os.path.expanduser("~/Downloads"),  # Downloads folder
        os.path.expanduser("~/Desktop"),  # Desktop
        os.path.expanduser("~/Documents"),  # Documents
    ]

    for path in search_paths:
        full_path = os.path.join(path, filename)
        if os.path.exists(full_path):
            return full_path

    return None


def sample_datetimes(input_file, output_file, sample_size):
    """
    Randomly sample datetime entries from input file and save to output file.

    Args:
        input_file (str): Path to input txt file containing datetime strings
        output_file (str): Path to output txt file for sampled datetimes
        sample_size (int): Number of datetime entries to randomly sample
    """
    try:
        # Try to find the input file if it doesn't exist at the given path
        if not os.path.exists(input_file):
            print(f"File not found at: {input_file}")

            # Extract just the filename if a full path was provided
            filename = os.path.basename(input_file)
            print(f"Searching for '{filename}' in common locations...")

            found_path = find_input_file(filename)
            if found_path:
                input_file = found_path
                print(f"Found file at: {input_file}")
            else:
                print(f"Could not find '{filename}' in any of these locations:")
                search_paths = [
                    ".",
                    "./data",
                ]
                for path in search_paths:
                    print(f"  - {os.path.expanduser(path)}")
                print("\nPlease ensure the file exists and try again.")
                print("You can also provide the full path to the file.")
                return

        # Read all datetime entries from input file
        with open(input_file, "r") as f:
            datetimes = [line.strip() for line in f if line.strip()]

        print(f"Found {len(datetimes)} datetime entries in {input_file}")

        # Check if sample size is valid
        if sample_size > len(datetimes):
            print(
                f"Warning: Sample size ({sample_size}) is larger than available entries ({len(datetimes)})"
            )
            print(f"Using all {len(datetimes)} entries instead")
            sample_size = len(datetimes)
        elif sample_size <= 0:
            print("Error: Sample size must be greater than 0")
            return

        # Randomly sample datetime entries
        sampled_datetimes = random.sample(datetimes, sample_size)

        # Sort the sampled datetimes (optional - maintains chronological order)
        # Remove this line if you want to keep random order
        sampled_datetimes.sort(reverse=True)

        # Write sampled datetimes to output file
        with open(output_file, "w") as f:
            for datetime_str in sampled_datetimes:
                f.write(datetime_str + "\n")

        print(f"Successfully sampled {len(sampled_datetimes)} datetime entries")
        print(f"Results saved to: {output_file}")

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
    except Exception as e:
        print(f"Error: {str(e)}")


def main():
    """Main function to handle command line arguments or interactive input"""

    # Default input file path
    DEFAULT_INPUT_FILE = "sdlGlmPositives_2025_05_14.txt"

    # Check if command line arguments are provided
    if len(sys.argv) >= 2:
        # Command line mode with at least sample size provided
        if len(sys.argv) == 4:
            # Full command line: input_file output_file sample_size
            input_file = sys.argv[1]
            output_file = sys.argv[2]
            try:
                sample_size = int(sys.argv[3])
            except ValueError:
                print("Error: Sample size must be an integer")
                return
        elif len(sys.argv) == 3:
            # Partial command line: output_file sample_size (use default input)
            input_file = DEFAULT_INPUT_FILE
            output_file = sys.argv[1]
            try:
                sample_size = int(sys.argv[2])
            except ValueError:
                print("Error: Sample size must be an integer")
                return
        elif len(sys.argv) == 2:
            # Minimal command line: sample_size only (use defaults for files)
            input_file = DEFAULT_INPUT_FILE
            output_file = "sampled_datetimes.txt"
            try:
                sample_size = int(sys.argv[1])
            except ValueError:
                print("Error: Sample size must be an integer")
                return
    else:
        # Interactive mode
        print("DateTime Random Sampler")
        print("-" * 25)
        print(f"Default input file: {DEFAULT_INPUT_FILE}")
        print("Current directory:", os.getcwd())

        # Check if default file exists and show status
        if os.path.exists(DEFAULT_INPUT_FILE):
            print("✓ Default file found in current directory")
        else:
            found_path = find_input_file(DEFAULT_INPUT_FILE)
            if found_path:
                print(f"✓ Default file found at: {found_path}")
            else:
                print("⚠ Default file not found - you'll need to specify the path")

        # Get input file path
        input_file = input(
            "\nEnter input file path (press Enter for default): "
        ).strip()
        if not input_file:
            input_file = DEFAULT_INPUT_FILE

        # Get output file path
        output_file = input(
            "Enter output file path (press Enter for 'sampled_datetimes.txt'): "
        ).strip()
        if not output_file:
            output_file = "sampled_datetimes.txt"

        # Get sample size
        try:
            sample_size = int(input("Enter number of datetimes to sample: ").strip())
        except ValueError:
            print("Error: Please enter a valid integer for sample size")
            return

    # Perform the sampling
    sample_datetimes(input_file, output_file, sample_size)


if __name__ == "__main__":
    main()
