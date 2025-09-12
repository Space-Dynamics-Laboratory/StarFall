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
This script utilizes the newly developed `bolides` python package.
Run the following commands to install the package:
    conda install -c conda-forge cartopy --solver=libmamba -y
    conda install pip --solver=libmamba -y
    cd /home/developer/miniconda3/envs/py3117/bin/
    git clone https://github.com/jcsmithhere/bolides.git
    cd bolides
    /home/developer/miniconda3/envs/py3117/bin/pip install -e .
    /home/developer/miniconda3/envs/py3117/bin/pip install bolides
Open a new python terminal and run the following code.
"""

import csv
import datetime
import glob
import os
import re
import sys

# Adding modules to the system path
sys.path.insert(0, "/home/developer/glmtriggergen")

import numpy as np
import psycopg2 as pg
from bolides import BolideDataFrame  # See above comment for the bolides package

import src.helper_funs.datetime_helpers as dth
from config import glmtriggergenconfig as settings

FILE_DATE_STAMP_STR = "2025_08_13"
INPUT_DIR = "input/rocket_data/"
POS_DIR = "output/rocket_positives/"
NEG_DIR = "output/rocket_negatives/"
FP_DIR = POS_DIR + "fps/"
DUP_DIR = NEG_DIR + "duplicates/"


def write_list(input_list, filename, data_path):
    """write_list(input_list, filename)

    Args:
        input_list (list): A python list of values
        filename (string): A string for the file name
        data_path (string): A string providing the path to the file destination
    """
    with open(data_path + filename + ".txt", "w", encoding="UTF-8") as f:
        for line in input_list:
            f.write(f"{line}\n")


# Move any false-positives that appear in the true positive folder
def move_fps(filenames_list, rocket_dir, move_dir):
    """move_fps(filenames_list, rocket_dir, move_dir)

    Move false-positive files to a separate folder to avoid including in
    the training process. If a .png file is provided, the associated .npy
    files are also moved to the move_dir. However, if a .npy file is provided,
    it alone is moved to the move_dir. This allows appropriate handling of
    different types of artifacts which arise in the data, e.g., sometimes
    stereo events will have one true signal and one undesirable noisy
    signal, while other stereo events are simply false-positives signals.

    Args:
        filenames_list (list): A list of file strings each associated with a
        false-positive.
        rocket_dir (string): The directory name with the rocket data
        move_dir (string): The name of the directory to move the FPs to
    """
    for filename in filenames_list:
        try:
            os.rename(
                f"/home/developer/glmtriggergen/data/output/{rocket_dir}/{filename}",
                f"/home/developer/glmtriggergen/data/output/{rocket_dir}/{move_dir}/{filename}",
            )
        except Exception:
            print(f"File {filename} was unable to be moved to the FP folder.")
        else:
            print(f"File {filename} correctly moved to FP folder.")

        if filename[-3:] == "png":
            file_date_cluster_id = re.search("^\d+_\d+.0", filename)[0]
            goes16_data_file = file_date_cluster_id + "_16.0_energy_lat_lon_array.npy"
            if os.path.isfile(
                f"/home/developer/glmtriggergen/data/output/{rocket_dir}/{goes16_data_file}"
            ):
                os.rename(
                    f"/home/developer/glmtriggergen/data/output/{rocket_dir}/{goes16_data_file}",
                    f"/home/developer/glmtriggergen/data/output/{rocket_dir}/{move_dir}/{goes16_data_file}",
                )
                print(f"File {goes16_data_file} correctly moved to FP folder.")
            goes17_data_file = file_date_cluster_id + "_17.0_energy_lat_lon_array.npy"
            if os.path.isfile(
                f"/home/developer/glmtriggergen/data/output/{rocket_dir}/{goes17_data_file}"
            ):
                os.rename(
                    f"/home/developer/glmtriggergen/data/output/{rocket_dir}/{goes17_data_file}",
                    f"/home/developer/glmtriggergen/data/output/{rocket_dir}/{move_dir}/{goes17_data_file}",
                )
                print(f"File {goes17_data_file} correctly moved to FP folder.")
            goes18_data_file = file_date_cluster_id + "_18.0_energy_lat_lon_array.npy"
            if os.path.isfile(
                f"/home/developer/glmtriggergen/data/output/{rocket_dir}/{goes18_data_file}"
            ):
                os.rename(
                    f"/home/developer/glmtriggergen/data/output/{rocket_dir}/{goes18_data_file}",
                    f"/home/developer/glmtriggergen/data/output/{rocket_dir}/{move_dir}/{goes18_data_file}",
                )
                print(
                    f"File {goes18_data_file} correctly moved to {move_dir} subfolder."
                )


def find_duplicate_triggers(rocket_dir):
    """find_duplicate_triggers(rocket_dir)

    Occassionally, two genuine triggers occur in adjacent files in the
    GOES data. Since the GLM TG processes signals using adjacent files,
    duplicate triggers can arise when providing large lists of event dates.
    This function returns a list of .png files to provide to moveFPs() in
    order to omit these duplicate trigger files from the training process.

    Args:
        rocket_dir (string): The directory name with the rocket data

    Returns:
        to_drop_pngs_list (list): A list of file name strings to omit
    """
    neg_png_paths = glob.glob(settings.DATA_PATH + f"output/{rocket_dir}/*.png")

    neg_date_cluster_id_and_rank = [
        re.search("\d+_\d+.0_\d+.0", neg_png_path)[0] for neg_png_path in neg_png_paths
    ]
    neg_date_and_rank = [
        re.sub("_\d+.0_", "_", neg_string)
        for neg_string in neg_date_cluster_id_and_rank
    ]
    to_keep_bools = [True] * len(neg_date_and_rank)

    for path in neg_date_and_rank:
        is_duplicate_list = [path == neg_png_path for neg_png_path in neg_date_and_rank]
        num_duplicates = sum(is_duplicate_list)
        if num_duplicates > 1:
            is_duplicates_indices = np.sort(np.where(is_duplicate_list)[0])
            for loop_ind, is_duplicates_index in enumerate(is_duplicates_indices):
                if loop_ind == 0:
                    continue
                else:
                    to_keep_bools[is_duplicates_index] = False
    to_drop_bools = [not to_keep_bool for to_keep_bool in to_keep_bools]
    to_drop_paths = [path for (path, bool) in zip(neg_png_paths, to_drop_bools) if bool]
    to_drop_pngs_list = [
        re.search(r"\d+_\d+.0_\d+.0_i.png", to_drop_path)[0]
        for to_drop_path in to_drop_paths
    ]

    return to_drop_pngs_list


def create_data_dirs(dir_list):
    """create_data_dirs(dir_list)

    Create directories to organize the training and testing data into.

    Args:
        dir_list (list): List of dir paths, e.g., [INPUT_DIR, POS_DIR, NEG_DIR, FP_DIR, DUP_DIR].
    """
    # Make sure an input data directory exists
    for dir_string in dir_list:
        input_path = settings.DATA_PATH + dir_string
        if not os.path.isdir(input_path):
            os.makedirs(input_path)


def create_tp_event_dates(input_dir=INPUT_DIR):
    """create_tp_event_dates(input_dir=INPUT_DIR)

    Args:
        input_dir (string, optional): Input directory string. Defaults to INPUT_DIR.
    """
    # Download true-positive event times from neo-bolide website
    bdf = BolideDataFrame(source="glm")
    # Select only the high and medium confidence events
    tp_datetimes = bdf.datetime[
        (bdf.confidenceRating == "high") | (bdf.confidenceRating == "medium")
    ].tolist()
    # Reformat the times
    tp_datetime_ints = [int(x.strftime("%Y%m%d%H%M%S")) for x in tp_datetimes]
    # Write the event times to a file
    write_list(
        tp_datetime_ints,
        "sdlGlmPositives_" + FILE_DATE_STAMP_STR,
        settings.DATA_PATH + input_dir,
    )


def generate_pos_data():
    """generate_pos_data()

    Runs a command line statement to produce the individual trigger data files

    """
    # Run the following code to produce the individual trigger data files:
    tp_command_string = f'python ./GlmTriggerGen.py -d "data/{POS_DIR}" \
        -f "data/{INPUT_DIR}sdlGlmPositives_{FILE_DATE_STAMP_STR}.txt" -p -o'
    os.system(tp_command_string)


def clean_pos_data():
    """clean_pos_data()

    Move data that is not a true positive out of the true-positive dir

    """

    # Move any data that is not a true-positive
    # Many of these include weak artifacts bundled in stereo events
    fp_files = [
        "20230823162953_101.0_16.0_energy_lat_lon_array.npy",
        "20230701165753_193.0_3438.0_i.png",
        "20230701165750_169.0_1266.0_i.png",
        "20230701165739_66.0_2267.0_i.png",
        "20230616104247_88.0_41.0_i.png",
        "20230315131302_32.0_45.0_i.png",
        "20230104150215_53.0_18.0_energy_lat_lon_array.npy",
        "20230104150215_53.0_17.0_energy_lat_lon_array.npy",
        "20221230084306_56.0_16.0_energy_lat_lon_array.npy",
        "20221116132841_34.0_17.0_energy_lat_lon_array.npy",
        "20221112185230_280.0_40.0_i.png",
        "20221103053259_86.0_50.0_i.png",
        "20221029152806_42.0_53.0_i.png",
        "20220907114506_42.0_48.0_i.png",
        "20220418162132_71.0_16.0_energy_lat_lon_array.npy",
        "20220224140500_35.0_45.0_i.png",
        "20211116121615_83.0_42.0_i.png",
        "20210831213955_434.0_40.0_i.png",
        "20210806160633_49.0_73.0_i.png",
        "20210806160628_38.0_531.0_i.png",
        "20210806160624_31.0_234.0_i.png",
        "20210806160618_15.0_584.0_i.png",
        "20210510173914_60.0_17.0_energy_lat_lon_array.npy",
        "20210505111443_36.0_47.0_i.png",
        "20211104105812_51.0_16.0_energy_lat_lon_array.npy",  # Tiny GOES-16 part of a strong stereo event
        "20210315045023_66.0_16.0_energy_lat_lon_array.npy",
        "20201215133233_44.0_48.0_i.png",  # boarderline
        "20201118083549_41.0_107.0_i.png",  # double triggered event due to 20201118083553 event
        "20201021093850_63.0_61.0_i.png",
        "20200628165638_34.0_559.0_i.png",
        "20200527141126_85.0_16.0_energy_lat_lon_array.npy",
        "20191025162039_205.0_17.0_energy_lat_lon_array.npy",
        "20190822133413_70.0_17.0_energy_lat_lon_array.npy",
        "20190811220552_260.0_17.0_energy_lat_lon_array.npy",
        "20190723102926_161.0_16.0_energy_lat_lon_array.npy",
        "20190715171118_121.0_51.0_i.png",  # Zero event
        "20190704132417_102.0_40.0_i.png",
        "20190212070415_54.0_17.0_energy_lat_lon_array.npy",
        "20190422110608_35.0_61.0_i.png",
        "20190704132410_75.0_17.0_energy_lat_lon_array.npy",
        "20190704132417_102.0_40.0_i.png",
        "20181117214819_1.0_498.0_i.png",
    ]

    move_fps(fp_files, "rocket_positives", "fps")


def create_fp_event_dates(input_dir=INPUT_DIR):
    """create_fp_event_dates(input_dir=INPUT_DIR)

    Args:
        input_dir (_type_, optional): _description_. Defaults to INPUT_DIR.
    """
    # Download the false-positive event times from the StarFall vm database
    # Connect to the starfall vm database
    connection = pg.connect(
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host="database",
        port=settings.DB_PORT,
    )

    # Query the database
    # num_fps = len(tp_datetime_ints)
    num_fps = 1900
    fp_tuples = ()
    with connection.cursor() as cursor:
        query_string = f"SELECT approx_trigger_time \
            FROM starfall_db_schema.events \
            WHERE processing_state = 8.0 \
            ORDER BY approx_trigger_time desc \
            LIMIT {num_fps};"
        # Select the recent false-positives from the starfall vm database
        # See starfall/starfall-common/Types/ProcessingState.ts for processing_state definitions
        cursor.execute(query_string)
        fp_tuples = cursor.fetchall()

        # Can also select recent true-positives from the starfall vm database
        # cursor.execute("SELECT approx_trigger_time \
        #                 FROM starfall_db_schema.events \
        #                 WHERE processing_state = 6 OR processing_state = 7 \
        #                 ORDER BY approx_trigger_time desc \
        #                 LIMIT 10;")
        # tpTuples = cursor.fetchall()

    # Convert database tuples into lists of datetime ints
    fp_ssue_list = [ssue[0] for ssue in fp_tuples]
    # tpSSUEs = [ssue[0] for ssue in tpTuples]
    fp_datetimes = [dth.EPOCH + datetime.timedelta(seconds=x) for x in fp_ssue_list]
    # tp_datetimes = [dth.EPOCH + datetime.timedelta(seconds=x) for x in tpSSUEs]
    fp_datetime_ints = [int(x.strftime("%Y%m%d%H%M%S")) for x in fp_datetimes]

    # Store results in text files
    write_list(
        fp_datetime_ints,
        "sdlGlmNegatives_" + FILE_DATE_STAMP_STR,
        settings.DATA_PATH + input_dir,
    )


def process_csv_to_datetime_ints(
    csv_file_path,
    output_dir=settings.DATA_PATH + INPUT_DIR,
    file_date_stamp=FILE_DATE_STAMP_STR,
    output_filename="sdlGlmNegatives",
):
    """
    Process CSV file containing trigger times and convert to datetime integers.

    Args:
        csv_file_path: Path to the CSV file
        output_dir: Directory to save output files
        file_date_stamp: Date stamp to append to output filename
        output_filename: A string for the output filename

    Returns:
        list: List of datetime integers in YYYYMMDDHHMMSS format
    """
    # Read CSV file and convert to list
    fp_tuples = []

    try:
        with open(csv_file_path, "r", encoding="UTF-8") as file:
            csv_reader = csv.reader(file)
            # Skip header row
            header = next(csv_reader)
            print(f"Header: {header}")

            # Read data rows and convert to tuples
            for row in csv_reader:
                if row and row[0]:  # Check if row is not empty and has data
                    try:
                        # Convert string to float, then store as tuple
                        fp_tuples.append((float(row[0]),))
                    except ValueError:
                        print(f"Skipping invalid row: {row}")
                        continue

    except FileNotFoundError:
        print(f"Error: File {csv_file_path} not found.")
        return []
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

    print(f"Read {len(fp_tuples)} records from CSV")

    # Convert database tuples into lists of datetime ints
    fp_ssue_list = [ssue[0] for ssue in fp_tuples]

    # Convert to datetime objects
    fp_datetimes = [dth.EPOCH + datetime.timedelta(seconds=x) for x in fp_ssue_list]

    # Convert to integer format YYYYMMDDHHMMSS
    fp_datetime_ints = [int(x.strftime("%Y%m%d%H%M%S")) for x in fp_datetimes]

    # Generate filename with date stamp
    if file_date_stamp:
        filename = f"{output_filename}_{file_date_stamp}"
    else:
        filename = output_filename

    # Store results in text files
    write_list(fp_datetime_ints, filename, output_dir)

    return fp_datetime_ints


def remove_duplicates_from_file(input_file_path, output_file_path=None):
    """
    Remove duplicate entries from a text file while preserving the original order.

    Args:
        input_file_path (str): Path to the input file containing entries to deduplicate
        output_file_path (str, optional): Path for the output file. If None,
                                        will create a new file with '_deduplicated' suffix

    Returns:
        tuple: (original_count, unique_count, duplicates_removed)
    """

    # If no output path specified, create one based on input path
    if output_file_path is None:
        base_name = input_file_path.rsplit(".", 1)[0]
        extension = (
            input_file_path.rsplit(".", 1)[1] if "." in input_file_path else "txt"
        )
        output_file_path = f"{base_name}_deduplicated.{extension}"

    # Read the file and track unique entries
    unique_entries = []
    seen_entries = set()
    original_count = 0

    try:
        with open(input_file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()  # Remove whitespace and newlines
                if line:  # Skip empty lines
                    original_count += 1
                    if line not in seen_entries:
                        seen_entries.add(line)
                        unique_entries.append(line)

        # Write deduplicated entries to output file
        with open(output_file_path, "w", encoding="utf-8") as file:
            for entry in unique_entries:
                file.write(entry + "\n")

        unique_count = len(unique_entries)
        duplicates_removed = original_count - unique_count

        print("Removing duplicate events complete!")
        print(f"Original entries: {original_count}")
        print(f"Unique entries: {unique_count}")
        print(f"Duplicates removed: {duplicates_removed}")
        print(f"Output saved to: {output_file_path}")

        return original_count, unique_count, duplicates_removed

    except FileNotFoundError:
        print(f"Error: File '{input_file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error processing file: {e}")
        return None


def remove_duplicates_from_list(entries):
    """
    Remove duplicates from a list while preserving order.

    Args:
        entries (list): List of entries to deduplicate

    Returns:
        list: List with duplicates removed, order preserved
    """
    unique_entries = []
    seen_entries = set()

    for entry in entries:
        if entry not in seen_entries:
            seen_entries.add(entry)
            unique_entries.append(entry)

    return unique_entries


# Remember no gcloud files for GOES Sats exist before 2018-02-12 02:15:18
def generate_neg_data():
    """generate_neg_data()

    Runs a command line statement to produce the individual trigger data files

    """
    fp_command_string = f'python ./GlmTriggerGen.py -d "data/{NEG_DIR}" \
        -f "data/{INPUT_DIR}sdlGlmNegatives_{FILE_DATE_STAMP_STR}.txt" -p -o'
    os.system(fp_command_string)


# Remove duplicate FPs with different cluster IDs but same datetime and ranks
def clean_neg_data():
    """clean_neg_data()

    Move data that is not a true negative out of the true-negative dir

    """
    to_drop_pngs = find_duplicate_triggers("rocket_negatives")

    move_fps(to_drop_pngs, "rocket_negatives", "duplicates")

    files_to_move = [
        "20230911212314_222.0_93.0_i.png",
        "20230911205845_220.0_111.0_i.png",
        "20230911204423_167.0_58.0_i.png",
        "20230911202550_144.0_42.0_i.png",
        "20230911195156_111.0_42.0_i.png",
        "20230911194422_73.0_47.0_i.png",
        "20230908113044_136.0_18.0_energy_lat_lon_array.npy",
        "20230910183325_273.0_49.0_i",
    ]

    move_fps(files_to_move, "rocket_negatives", "duplicates")


def generate_data():
    """generate_data()

    The main function of this script.

    """
    # create_data_dirs([INPUT_DIR, POS_DIR, NEG_DIR, FP_DIR, DUP_DIR])

    # create_tp_event_dates()
    # generate_pos_data()
    # clean_pos_data()

    # create_fp_event_dates()
    # process_csv_to_datetime_ints(
    #     csv_file_path="/home/developer/glmtriggergen/data/input/glmStarFallEventDatesUnformatted.csv",
    #     output_filename="glmStarFallEventDates",
    # )
    remove_duplicates_from_file(
        input_file_path="/home/developer/glmtriggergen/data/input/glm_event_dates_2025_08_22.txt",
        output_file_path="/home/developer/glmtriggergen/data/input/glm_event_dates_1_2025_08_22.txt",
    )
    # generate_neg_data()
    # clean_neg_data()


if __name__ == "__main__":
    generate_data()
