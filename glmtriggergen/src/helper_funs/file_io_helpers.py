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
from datetime import datetime, timedelta

import numpy as np
from netCDF4 import Dataset

import src.colors as c
import src.helper_funs.datetime_helpers as dth
import src.helper_funs.gcloud_helpers as ghf
import src.helper_funs.geo_helpers as geohf
from config import glmtriggergenconfig as settings
from src.helper_funs.util_helpers import in_glm_file_latter_half


def write_trigger_data(good_cluster_ids, glmdata, data_dir):
    """write_trigger_data(good_cluster_ids, glmdata, data_dir)

    Extract and write to disk as numpy files the energy, lat, and lon
    data for all triggering events. The triggering events are identified
    by their provided cluster IDs.

    Args:
        good_cluster_ids (array): An array of triggering cluster IDs
        glmdata (object): A GlmDataSet class instance
        data_dir (string): The path to the data directory to write to
    """

    # For each triggering cluster ID
    for cluster_id in good_cluster_ids:
        # Skip the bad cluster IDs
        if cluster_id == glmdata.BAD_CLUSTER_ID:
            continue

        in_cluster_id_bools = glmdata.cluster_id == cluster_id
        unique_sat_ids = np.unique(glmdata.sat_id[in_cluster_id_bools])

        for sat_id in unique_sat_ids:
            # Index points with same cluster and satellite
            # Also, only include highest_energy points with good fitness
            in_cluster_sat_id_bools = (
                in_cluster_id_bools
                & (glmdata.sat_id == sat_id)
                & (glmdata.fitness == 1)
                & (glmdata.highest_energy == 1)
            )
            if np.all(~in_cluster_sat_id_bools):
                continue

            # Subset times and energies belonging to same cluster and sat
            energy_by_cluster_sats = glmdata.energy_joules[in_cluster_sat_id_bools]
            cloud_top_lat_lon_by_cluster_sat_degs = glmdata.cloud_top_lat_lon_deg[
                in_cluster_sat_id_bools
            ]
            lat_by_cluster_sat_degs = cloud_top_lat_lon_by_cluster_sat_degs[:, 0]
            lon_by_cluster_sat_degs = cloud_top_lat_lon_by_cluster_sat_degs[:, 1]

            # Identify a basetime
            basetime = glmdata.time_s[in_cluster_sat_id_bools][
                np.argmax(glmdata.source_intensity_wpsr[in_cluster_sat_id_bools])
            ]
            event_datetime = dth.convert_ssue_to_datetime(
                basetime + glmdata.basetime_ssue
            )

            energy_lat_lon_array = np.vstack(
                (
                    energy_by_cluster_sats,
                    lat_by_cluster_sat_degs,
                    lon_by_cluster_sat_degs,
                )
            )
            filename = (
                f'{event_datetime.strftime("%Y%m%d%H%M%S")}_'
                f"{cluster_id}_{sat_id}_energy_lat_lon_array.npy"
            )
            np.save(
                data_dir + filename,
                energy_lat_lon_array,
            )


def load_cal_tables(path_to_cal_tables):
    """load_cal_tables(self, path_to_cal_tables)

    Load the continuum calibration tables for all applicable
    satellite ID and orientation flip_flag combinations.

    Args:
        path_to_cal_tables (string): Absolute path to location of all
        calibration .nc files

    Returns:
        l2_cal_tables_dict (dict): A dictionary where the keys are
        the file paths to the .nc calibration table files, and the
        entries are three element lists containing the calibration
        table arrays.
    """
    # Load all calibration .nc files
    file_paths = glob.glob(path_to_cal_tables + "*.nc")
    file_paths = sorted(file_paths)
    l2_cal_tables_dict = dict.fromkeys(file_paths)
    for cal_tables_file_path in l2_cal_tables_dict:
        nc_data = Dataset(cal_tables_file_path, "r")
        pixel_to_lon_array = load_nc_lons(nc_data)
        pixel_to_lat_array = nc_data.variables["pixel_lat"][:, :]
        lookup_table = nc_data.variables["LUT"][:, :]
        l2_cal_tables_dict[cal_tables_file_path] = [
            pixel_to_lon_array,
            pixel_to_lat_array,
            lookup_table,
        ]

    return l2_cal_tables_dict


def load_nc_lons(nc_dataset):
    """load_nc_lons(nc_dataset)

    Returns a masked array of calibration table longitudes. If the GOES
    satellite is a GOES West satellite, the longitudes are wrapped to
    [-360, 0) degrees to avoid a discontinuity at -180 degrees.

    Args:
        nc_dataset (netCDF Dataset): The loaded netCDF Dataset object

    Returns:
        lon_masked_array: A numpy masked array of longitudes
    """

    lon_masked_array = nc_dataset.variables["pixel_lon"][:, :]
    if ("17" in nc_dataset.instrument) or ("18" in nc_dataset.instrument):
        lon_masked_array = geohf.wrap_longitudes(lon_masked_array, 0)

    return lon_masked_array


def get_glm_file_meta(filename):
    """start_ssue,end_ssue,sat_id = get_glm_file_meta(filename)

    Retrieve file start time, end time, and associated satellite for GLM files
    Times are in seconds since unix epoch
    The information is retrieved based on the GLM file naming convention

    INPUTS:
        filename - name of the file for which to retrieve information

    OUTPUTS:
        start_ssue - start time of the file in seconds since unix epoch

        end_ssue - end time of the file in seconds since unix epoch

        sat_id - satellite associated with the file (either 16 or 17)
    """

    # extract the needed file information
    sat_id = int(filename[-53:-51])
    year = int(filename[-49:-45])
    days = int(filename[-45:-42])
    hour = int(filename[-42:-40])
    mins = int(filename[-40:-38])
    secs = int(filename[-38:-36])
    start_ssue = (
        datetime(year, 1, 1, hour, mins, secs) + timedelta(days=days - 1) - dth.EPOCH
    ).total_seconds()
    year = int(filename[-33:-29])
    days = int(filename[-29:-26])
    hour = int(filename[-26:-24])
    mins = int(filename[-24:-22])
    secs = int(filename[-22:-20])
    end_ssue = (
        datetime(year, 1, 1, hour, mins, secs) + timedelta(days=days - 1) - dth.EPOCH
    ).total_seconds()

    # return the start and end SSUE
    return start_ssue, end_ssue, sat_id


def download_glm_files(start_time_ssue, end_time_ssue, data_dir, status_helper):
    """[local_filenames, got_all] = download_glm_files(start_time_ssue,
                                                       end_time_ssue,
                                                       data_dir,
                                                       local_filenames)

    Downloads the GLM files (if they don't already exist) that fall within the
    window of start_time_ssue to end_time_ssue

    INPUTS:
        start_time_ssue - start time of the desired window in seconds since unix
        epoch

        end_time_ssue - end time of the desired window in seconds since unix epoch

        data_dir - directory to store the data in once downloaded

        status_helper - a StatusHelper object for sending status and logs

    OUTPUTS:
        local_filenames - list of files that were downloaded (including their
        path)

        got_all - If true, all expected files were found when downloading data.
        If false, there were likely files missing.
    """
    # make sure the data_dir ends in '/'
    if data_dir[-1] != "/":
        raise ValueError("Expect specified data directory to end with /: " + data_dir)

    # get the list of files that fall within the requested time
    [filenames, got_all] = ghf.get_list_for_specific_window(
        start_time_ssue, end_time_ssue
    )

    # figure out which files we don't already have and download them
    local_filenames = []
    for file in filenames:
        # get the local name
        file_end_ind = file.rfind("/")
        local_name = file[file_end_ind + 1 :]

        # if it already exists, continue
        if os.path.isfile(data_dir + local_name):
            continue

        # if it doesn't exist, download it and add it to the list
        success = ghf.save_gcloud_files_to_dir(data_dir, file)
        if success:
            status_helper.send_logs([("debug", f"Successfully downloaded file {file}")])
        else:
            raise ValueError(f"Failed to download file {file}")
        local_filenames.append(data_dir + local_name)

    return [local_filenames, got_all]


def cleanup_files(local_filenames, event_dates_deque):
    """local_filenames = cleanup_files(local_filenames, event_dates_deque)

    Cleans up files that were downloaded for processing and are no longer
    needed. Files are considered to be no longer needed if they are not within
    a half of a file's length to an event_date which is yet to be processed.

    INPUTS:
        local_filenames - List of files (including paths) to consider for
        deletion

        event_dates_deque - The next times to process (seconds since unix epoch).

    OUTPUTS:
        local_filenames - List of remaining files after deletion of no longer
        needed files
    """
    # loop through the list of files
    for ii, file in enumerate(local_filenames):
        # get the file times
        start_ssue, end_ssue, _ = get_glm_file_meta(file)

        keep_file_list = []
        for event_date in event_dates_deque:
            # Check if the event date is in the first or second half of a file
            in_latter_half_of_file = in_glm_file_latter_half(event_date)
            if in_latter_half_of_file:
                keep_file = (
                    start_ssue - (settings.PROCESS_INTERVAL_S / 2) <= event_date
                ) and (end_ssue > event_date)
                keep_file_list.append(keep_file)
            else:
                keep_file = (start_ssue <= event_date) and (
                    end_ssue + (settings.PROCESS_INTERVAL_S / 2) > event_date
                )
                keep_file_list.append(keep_file)
        # Check if the end of the file comes before the time_to_process_ssue
        # If so, try to remove it
        if not any(keep_file_list):
            try:
                os.remove(file)
                local_filenames[ii] = None
            except PermissionError:
                # let it pass if it can't delete, it will try again
                if len(file) > 18:  # grab only the filename and not it's path
                    print(
                        f"{c.YELLOW}Failed to delete *_"
                        + file[-18:]
                        + " Will retry on next pass.{c.RESET}"
                    )
                else:
                    print(
                        f"{c.YELLOW}Failed to delete *_"
                        + file
                        + " Will retry on next pass.{c.RESET}"
                    )

    local_filenames = [file for file in local_filenames if file is not None]

    return local_filenames
