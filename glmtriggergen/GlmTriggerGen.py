#!/usr/bin/env python

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

import glob
import os
import signal
import sys
import threading
import time
from collections import deque, namedtuple
from datetime import datetime, timedelta

import numpy as np
from joblib import load

import src.helper_funs.database_helpers as dbh
import src.helper_funs.datetime_helpers as dth
from config import glmtriggergenconfig as settings
from src.helper_funs import status_helpers_queue
from src.helper_funs.file_io_helpers import (
    cleanup_files,
    download_glm_files,
    get_glm_file_meta,
    load_cal_tables,
)
from src.helper_funs.glm_data_set_helpers import process_glm_files
from src.helper_funs.util_helpers import in_glm_file_latter_half, signal_handler


def process_inputs(sys_input):
    """[setup, event_dates_que] = process_inputs(sys_input)

    Processes the system inputs to the python script

    INPUTS:
        sys_input - The sys.argv list that provides the system inputs to the
        process

    OUTPUTS:
        setup - named tuple containing:

            continuous_mode - if true, indicates continuous processing of data

            data_dir - data directory specified by the user to be used for data
            reads/writes. Defaults to settings.DATA_PATH

            local_only - if true, only use files already in data_dir; do not
            download new files

            keep_netcdfs - if true, none of the downloaded GLM netCDF files will
            be deleted after processing. Defaults to false

            do_plots - if true, plots are created of good clusters. Default is
            false

            output_trigger_file - if true, save a .csv file of trigger times and
            number of triggers to data_dir. Default is false

        event_dates_que - table of event dates that should be checked

    More information can be found by using the --help or -h flags
    """
    # Initialize some defaults
    start_time = datetime.utcnow() - timedelta(seconds=settings.WAIT_TIME_S)
    event_dates_que = deque()
    data_dir = settings.DATA_PATH
    keep_netcdfs = False
    do_plots = False
    debug_mode = False
    output_trigger_file = False
    continuous_mode = len(sys_input) == 1
    local_only = False
    generate_event_dates = False
    processing_start_time = 0.0
    processing_end_time = (
        datetime.utcnow() + timedelta(days=36500) - dth.EPOCH
    ).total_seconds()

    # loop through all inputs
    input_count = 1
    while input_count < len(sys_input):
        if (
            sys_input[input_count] == "-h" or sys_input[input_count] == "--help"
        ):  # print help info
            print(
                """
GlmTriggerGen.py

Attempts to detect events in GLM files pulled from the google cloud service or
stored locally depending or specified input options. All inputs are optional.
If no inputs are provided starts in continuous mode from current time.

INPUTS:
-c
    continuous_mode: From the specified starting time, will process all files moving
      forward in a continuous manner. Will continue to run until killed (e.g.,
      with ctrl-c). Note, however, that current files are given priority over
      other events in the list so it may take a while to get through all events
      provided by the event_file as they will only be processed during the down
      time while waiting for new files to be uploaded to the cloud.
-s
    processing_start_time: Time to start in the format YYYYMMDDhhmmss. If not provided,
      starts at the current time minus the wait period required by the config
      file for continuous mode and 1970/1/1/0/0/0 for data generation purposes.
-n
    processing_end_time: Time to end at in the format YYYYMMDDhhmmss. If not specified,
      continuous mode will run until ctrl-c is pressed
-d
    data_dir: Directory path to which data should be saved. If none provided,
      default behavior will create a /data/ directory.
-f
    event_file name: Name of the event txt file to load event times from. Should
      contain a column of dates in the format YYYYMMDDhhmmss.
-e
    event time: Event time to add to the list to be processed. Should be in the
      format YYYYMMDDhhmmss. Will be appended to the list provided by event_file
      if it is specified.
-g
    generate events: generate event times to analyze based on the start times
      of all files currently in the specified data directory. Will be appended
      to the list provided by event_file if it is specified.
-l
    local only: Only uses data already present in data_dir. Will not download
      any new files. Also assumes local files should be kept after processing
      (i.e., silently turns on the --keep-netcdfs flag).
-p
    do plots: If -p is included, plots are made of good clusters and near
      misses. Plots are saved in data_dir. (NOT RECOMMENDED IN CONTINUOUS MODE)
-o
    output trigger data: Save a .csv file of trigger times and number of
      triggers to data_dir. (NOT RECOMMENDED IN CONTINUOUS MODE)
--keep-netcdfs
    save netcdfs: If --keep-netcdfs is included, none of the downloaded GLM
      netCDF files will be deleted after processing. (NOT RECOMMENDED IN
      CONTINUOUS MODE)
--debug
    debug mode: Turn on additional output for troubleshooting the GLM trigger
      generator
-v, --version
    version: Return the version number of the GLM trigger generator code. See
      RELEASE.md for a history of the main changes in the versions.
            """
            )
            sys.exit()

        elif (sys_input[input_count] == "-v") or (
            sys_input[input_count] == "--version"
        ):
            print(f"version: {settings.GLM_TG_VERSION_FULL}")
            sys.exit()

        elif sys_input[input_count] == "-c":  # continuous mode
            continuous_mode = True
            input_count += 1

        elif sys_input[input_count] == "-s":  # processing start time
            start_time = datetime.strptime(
                str(sys_input[input_count + 1]), "%Y%m%d%H%M%S"
            )
            processing_start_time = (start_time - dth.EPOCH).total_seconds()
            input_count += 2

        elif sys_input[input_count] == "-n":  # processing end time
            processing_end_time = (
                datetime.strptime(str(sys_input[input_count + 1]), "%Y%m%d%H%M%S")
                - dth.EPOCH
            ).total_seconds()
            input_count += 2

        elif sys_input[input_count] == "-d":  # data directory
            data_dir = sys_input[input_count + 1]
            if not os.path.exists(data_dir):
                print(f"Specified data directory does not exist: {data_dir}.")
                sys.exit()
            input_count += 2

        elif sys_input[input_count] == "-f":  # event file
            # read file contents
            with open(sys_input[input_count + 1], encoding="utf8") as event_file:
                event_date_strings = [line.split() for line in event_file]

            # convert contents to SSUE (offset by half processing time to center processing on event time)
            for event in event_date_strings:
                event_dates_que.appendleft(
                    (
                        datetime.strptime(event[0], "%Y%m%d%H%M%S") - dth.EPOCH
                    ).total_seconds()
                )
            input_count += 2

        elif sys_input[input_count] == "-g":  # generate events from data dir
            generate_event_dates = True
            input_count += 1

        elif sys_input[input_count] == "-l":  # use only local files
            local_only = True
            keep_netcdfs = True
            input_count += 1

        elif sys_input[input_count] == "-p":  # turn on plots
            do_plots = True
            input_count += 1

        elif sys_input[input_count] == "-o":  # output trigger data
            output_trigger_file = True
            input_count += 1

        elif sys_input[input_count] == "--keep-netcdfs":  # turn on keep_netcdfs
            keep_netcdfs = True
            input_count += 1

        elif sys_input[input_count] == "--debug":  # output trigger data
            debug_mode = True
            input_count += 1

        elif sys_input[input_count] == "-e":  # single event time
            # setup the event information for a single event
            event_dates_que.appendleft(
                (
                    datetime.strptime(str(sys_input[input_count + 1]), "%Y%m%d%H%M%S")
                    - dth.EPOCH
                ).total_seconds()
            )
            input_count += 2

        else:
            raise ValueError("Unrecognized option: " + str(sys_input[input_count]))

    if generate_event_dates:  # add all the files to the event_dates_que deque
        print("Generating event dates from the data directory")
        # grab the file times and add them to event_dates_que
        file_paths = glob.glob(data_dir + "**/*.nc", recursive=True)
        for file_path in file_paths:
            file_start_time_ssue, file_end_time_ssue, _ = get_glm_file_meta(file_path)
            if (
                processing_start_time < file_end_time_ssue
                and processing_end_time >= file_start_time_ssue
            ):
                # Define the event time as the file start time + processing interval / 2
                gen_event_time = (
                    round(file_start_time_ssue) + settings.PROCESS_INTERVAL_S / 2
                )
                # Check if any other event times overlap
                # (Start times between glm satellites should be consistent)
                if gen_event_time not in event_dates_que:
                    event_dates_que.appendleft(gen_event_time)

    if len(event_dates_que) > 0:
        # Sort the specified historic event dates from oldest to newest
        # (i.e., low to high), this will ensure the newer events are
        # processed before the older events
        event_dates_que = deque(sorted(event_dates_que))

    if continuous_mode:
        # Fake an event date
        initial_event_date_ssue = (start_time - dth.EPOCH).total_seconds()
        # Ensure initial_event_date_ssue is in the first 10 seconds of a file

        # This helps with subsequent file processing to avoid duplicate triggers
        if in_glm_file_latter_half(initial_event_date_ssue):
            initial_event_date_ssue -= 10
        event_dates_que.append(initial_event_date_ssue)

    if len(event_dates_que) == 0:
        raise ValueError("No events provided and continuous mode was not activated")

    # Create a named tuple class for setup using the namedtuple factory
    # The class instances will be immutable and allow dot notation for
    # accessing data members.
    SetupNamedTuple = namedtuple(
        "SetupNamedTuple",
        [
            "continuous_mode",
            "data_dir",
            "local_only",
            "keep_netcdfs",
            "do_plots",
            "output_trigger_file",
            "debug_mode",
            "processing_end_time",
        ],
    )
    setup = SetupNamedTuple(
        continuous_mode,
        data_dir,
        local_only,
        keep_netcdfs,
        do_plots,
        output_trigger_file,
        debug_mode,
        processing_end_time,
    )

    return [setup, event_dates_que]


def main():
    """Main function for command line calling

    Attempts to detect events in GLM files pulled from the google cloud service
    or stored locally depending on specified input options

    See function process_inputs __doc__ for input help, or use the --help or -h
    flags
    """
    # Make sure we're running Python 3
    if sys.version_info[0] < 3:
        raise Exception("Must be using Python 3")

    # Process the inputs
    [setup, event_dates_que] = process_inputs(sys.argv)

    # Create a status helper object

    status_helper = status_helpers_queue.StatusHelperQueue(settings.STATUS_CONNECTION)
    status_thread = threading.Thread(
        target=status_helper.run_status_server_thread,
        args=(),
    )
    status_thread.daemon = True
    status_thread.start()
    print("Server listening for status requests")

    # Instantiate a database helper if requested
    if settings.SAVE_TO_DATABASE:
        db_helper = dbh.DBHelper(status_helper)
    else:
        db_helper = None

    # Print the remaining setup
    status_helpers_queue.send_setup_status(setup, event_dates_que, status_helper)

    # Prepare to handle Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Load all of the GOES GLM calibration tables
    l2_cal_tables_dict = load_cal_tables(settings.L2_CAL_TABLES_PATH)

    # Load the fitted model parameters for inference
    rocket_pipeline = load(
        os.path.join(settings.BASE_PATH, f"rocket_model/{settings.ROCKET_MODEL_NAME}")
    )

    # Print out some useful info header
    print(
        "  TIME PROCESSING   #Files LastTime MeanTime  #TRIGGERS     CURRENT TIME    #EVENTS"
    )
    print(
        "------------------- ------ -------- -------- ---------- ------------------- -------"
    )
    mean_time = 20.0

    # Store names of files already in the data_dir
    local_filenames = glob.glob(setup.data_dir + "**/*.nc", recursive=True)

    # Variable to iterate through in the processing while loop
    event_index = len(event_dates_que) - 1

    # Initialize for post-processing analysis
    if setup.output_trigger_file:
        event_file_dates = []
        triggered_events = []

    # Print the current event_date
    current_event_date = dth.convert_ssue_to_string(event_dates_que[event_index])
    print(current_event_date, end="", flush=True)
    status_helper.send_logs(
        [
            (
                "info",
                f"Attempting to process {settings.PROCESS_INTERVAL_S} s batch at {current_event_date}",
            )
        ]
    )

    # Begin of the processing while loop
    while event_index < len(event_dates_que):
        status_helper.send_status(
            [
                (
                    "Config CLUSTER_DURATION_LIMIT_S",
                    f"{settings.CLUSTER_DURATION_LIMIT_S} s",
                ),
                (
                    "Config CLUSTER_THRESHOLD",
                    f"{settings.VALID_RANK} continuous group points "
                    f"above {settings.MIN_ENERGY_LVL_J} J",
                ),
            ]
        )

        # Sanity check on event_index
        if event_index not in (len(event_dates_que) - 1, 0):
            raise ValueError(
                f"event_index should be 0 or {len(event_dates_que) - 1}. It was: {event_index}"
            )

        # Store the event time to process
        cur_event_ssue = event_dates_que[event_index]

        time_to_now_s = (datetime.utcnow() - dth.EPOCH).total_seconds() - cur_event_ssue
        # Check if the current event SSUE is too close to now, or if it is beyond end_time
        if (time_to_now_s < settings.WAIT_TIME_S) or (
            cur_event_ssue >= setup.processing_end_time
        ):
            # Current event SSUE is too close to now or within end_time
            # Check if we are processing the oldest event in the deque
            if event_index == 0:
                # Check if current event SSUE is within the end time
                if cur_event_ssue < setup.processing_end_time:
                    # If time is too close then wait. This makes sure files
                    # have come in from all satellites before processing
                    time.sleep(settings.WAIT_TIME_S - time_to_now_s)
                else:
                    # event_dates_que is on only event and it is beyond the end time
                    print(" Passed the specified end time. Terminating.")
                    status_helper.send_logs(
                        [("info", "Passed the specified end time. Terminating.")]
                    )
                    break
            else:
                # Current event SSUE is too close to now or within end_time AND
                # current event SSUE is not the zeroth event date.
                event_index = 0  # Select the oldest event in the deque
                print(" Caught up to current time or end time. Processing missed times")
                status_helper.send_logs(
                    [
                        (
                            "info",
                            "Caught up to current time or end time. Processing missed times",
                        )
                    ]
                )
                # Print the index 0 event_date
                current_event_date = dth.convert_ssue_to_string(
                    event_dates_que[event_index]
                )
                print(current_event_date, end="", flush=True)
                info_message = (
                    f"Attempting to process {settings.PROCESS_INTERVAL_S} "
                    f"s batch at {current_event_date}"
                )
                status_helper.send_logs([("info", info_message)])
                # Go to the next iteration of the event_date while loop
                continue

        # The current event date is not too close to now AND is within end_time
        clock_time = time.time()
        got_all = True
        if not setup.local_only:
            # Attempt to get the latest files
            [local_names, got_all] = download_glm_files(
                cur_event_ssue - settings.PROCESS_TIME_SIZE_S / 2,
                cur_event_ssue + settings.PROCESS_TIME_SIZE_S / 2,
                setup.data_dir,
                status_helper,
            )
            local_filenames.extend(local_names)

        # Check for data, then process the glm files (look for events)
        if (not got_all) and (time_to_now_s < settings.MAX_HOLD_TIME):
            # If all files did not download and time_to_now_s is within
            # MAX_HOLD_TIME, skip for now
            print("Skipping for now due to missing data.")
            status_helper.send_logs([("info", "Skipping for now due to missing data.")])
            event_index += 1  # Move to the next event
            if time_to_now_s < settings.WAIT_TIME_S:
                time.sleep(settings.WAIT_TIME_S - time_to_now_s)
        else:
            # All .nc files are available, proceed with processing
            [num_valid_files, num_good_clusters] = process_glm_files(
                setup.data_dir,
                l2_cal_tables_dict,
                rocket_pipeline,
                cur_event_ssue,
                status_helper,
                db_helper,
                setup.do_plots,
                setup.debug_mode,
                setup.output_trigger_file,
            )

            # Store for post-processing analysis
            if setup.output_trigger_file:
                event_file_dates.append(
                    dth.convert_ssue_to_string(event_dates_que[event_index])
                )
                triggered_events.append(num_good_clusters)

            # Count number of events in the queue (including the one just processed)
            queued_events_string = f"{(len(event_dates_que)):6d}"

            # Pop off the event
            if event_index == len(event_dates_que) - 1:
                # If we just processed most recent event, discard it
                event_dates_que.pop()
            else:
                # If we processed the oldest event, discard it
                event_dates_que.popleft()

            # Add another event onto queue if at last event, in continuous
            # mode, and the current time is before the setup.processing_end_time
            if (
                (event_index == len(event_dates_que))
                and setup.continuous_mode
                and (cur_event_ssue < setup.processing_end_time)
            ):
                event_dates_que.append(cur_event_ssue + settings.PROCESS_INTERVAL_S)

            # Unless the --keep-netcdfs flag was provided, delete the files
            # that will not be needed for future processing
            if not setup.keep_netcdfs:
                local_filenames = cleanup_files(local_filenames, event_dates_que)

            # Calculate the mean time to process and the current time
            mean_time = (19 * mean_time + (time.time() - clock_time)) / 20
            current_time = datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")

            # Print the number of files used in the processing of the event,
            # time to process the last event, a weighted running average of last
            # event processing times, the number of published triggers, the
            # current system time, and the number of events in the queue.
            print(
                f" {num_valid_files:6d} {(time.time() - clock_time):8.2f}",
                f"{mean_time:8.2f} {num_good_clusters:10d} {current_time} ",
                f"{queued_events_string}",
            )
            status_helper.send_status(
                [
                    ("Files in Batch", f"{num_valid_files:6d}"),
                    (
                        "Processing Time (Current)",
                        f"{(time.time() - clock_time):8.2f} s",
                    ),
                    ("Processing Time (Mean)", f"{mean_time:8.2f} s"),
                    ("Queued Batches", queued_events_string),
                ]
            )

        # Add another event onto queue if at last event, in continuous mode,
        # and the current time is before the setup.processing_end_time
        if (
            (event_index == len(event_dates_que))
            and setup.continuous_mode
            and (cur_event_ssue < setup.processing_end_time)
        ):
            event_dates_que.append(cur_event_ssue + settings.PROCESS_INTERVAL_S)

        # Go to the next event (unless we are out of events)
        event_index = max(len(event_dates_que) - 1, 0)

        if event_index < len(event_dates_que):
            # Print the next time to be processed. (Printing here will
            # appropriately flush the buffer instead of at the beginning of the
            # next loop.)
            current_event_date = dth.convert_ssue_to_string(
                event_dates_que[event_index]
            )
            print(current_event_date, end="", flush=True)
            info_message = (
                f"Attempting to process {settings.PROCESS_INTERVAL_S} "
                f"s batch at {current_event_date}"
            )
            status_helper.send_logs([("info", info_message)])
    # End of processing while loop

    if setup.output_trigger_file:
        # Concatenate the performance metrics and save as a .csv to output directory
        event_trigger_array = np.concatenate(
            (
                np.array(event_file_dates).reshape(-1, 1),
                np.array(triggered_events).reshape(-1, 1).astype("str"),
            ),
            axis=1,
        )
        np.savetxt(
            setup.data_dir + "event_trigger_array.csv",
            event_trigger_array,
            delimiter=",",
            header="EventDateTime,Triggers",
            comments="",
            fmt="%s",
        )

    # Unless the --keep-netcdfs flag was provided, clean up any remaining files
    if not setup.keep_netcdfs:
        _ = cleanup_files(local_filenames, event_dates_que)


if __name__ == "__main__":
    main()
