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

import subprocess
import warnings
from datetime import datetime, timedelta

import src.helper_funs.datetime_helpers as dth
from config import glmtriggergenconfig as settings

# How long (in seconds) we expect GLM netCDF files to be
GLM_FILE_LENGTH_S = 20


def construct_file_dir_and_name(sat_id, year, doy, hour, minute=-1, second=-1):
    """construct_file_dir_and_name(sat_id, year, doy, hour, minute=-1, second=-1)

    Based on the input satellite ID and date/time, construct the google cloud
    directory and beginning path name that would match the specified
    file/files. Minute and second are optional parameters that shrink the
    specified location to certain files within a folder. Without minute and
    second, only the folder level is given.

    Args:
        sat_id (int): id of the satellite to use (either 16 || 17 || 18)
        year (int): year folder to look in
        doy (int): day of year folder to look in
        hour (int): hour folder to look in
        minute (int, optional): If included, restricts files to a particular
        minute (should be around 3 files at most). Defaults to -1.
        second (int, optional): If included, must be either 0, 20, or 40 and
        will restrict search to a single file. Defaults to -1.

    Returns:
        string: The constructed directory path and file name
    """
    # make sure the sat_id is valid
    if sat_id not in settings.SAT_ID_NUMS:
        raise ValueError(
            f"sat_id must be one of SAT_ID_NUMS: {settings.SAT_ID_NUMS}. It is {sat_id}."
        )

    # create the last part of the directory info
    dir_end = ""
    if year >= 2018:
        dir_end += "/" + str(int(year))
    else:
        raise ValueError("Year must be >= 2018 not " + str(year))
    if 0 < doy < 367:
        dir_end += "/" + str(int(doy)).zfill(3)
    else:
        raise ValueError("DOY must be between 1 and 366 (inclusive) not " + str(doy))
    if 0 <= hour < 24:
        dir_end += "/" + str(int(hour)).zfill(2)
    else:
        raise ValueError("Hour must be between 0 and 23 not " + str(hour))

    # if a minute was included, further restrict the files queried
    if 0 <= minute < 60:
        dir_end += (
            "/OR_GLM-L2-LCFA_G"
            + str(sat_id)
            + "_s"
            + str(int(year))
            + str(int(doy)).zfill(3)
            + str(int(hour)).zfill(2)
            + str(int(minute)).zfill(2)
        )

        # check the second to see if it should be added as well
        if second in [0, 20, 40]:
            dir_end += str(int(second)).zfill(2)

        # add wild card on the end
        dir_end += "*"

    return "gs://gcp-public-data-goes-" + str(sat_id) + "/GLM-L2-LCFA" + dir_end


class FileHistory:
    """FileHistory class

    A class for tracking the history of files loaded
    """

    date = datetime.utcnow()
    sat_id = 0
    filename = []

    def __init__(self, date, sat_id, filename):
        self.date = date
        self.sat_id = sat_id
        self.filename = filename

    def set_last_filename(self, filename):
        """A set method for the filename data member

        Args:
            filename (string): a new filename
        """
        self.filename = filename

    def year(self):
        """A get method for the year data member

        Returns:
            int: instance year
        """
        return self.date.year

    def doy(self):
        """A get method for the doy

        Returns:
            int: instance doy
        """
        return (self.date - datetime(self.date.year, 1, 1)).days + 1

    def hour(self):
        """A get method for the hour data member

        Returns:
            int: instance hour
        """
        return self.date.hour

    def minute(self):
        """A get method for the minute data member

        Returns:
            int: instance minute
        """
        return self.date.minute

    def decrement(self):
        """A method for decrementing the date data member by one hour.

        The filename data member is removed since it is no longer valid.
        No value is returned.

        """
        # remove filename since we are stepping and the old filename can't be valid anymore
        self.filename = ""

        # remove one day
        self.date = self.date - timedelta(hours=1)


def get_file_list_from_gcloud(sat_id, year, doy, hour, minute=-1, second=-1):
    """get_file_list_from_gcloud(sat_id, year, doy, hour, minute=-1, second=-1)

    Based on the input time reads the list of files in that directory of the
    appropriate GOES satellite

    Args:
        sat_id (int): id of the satellite to use (either 16 || 17 || 18)
        year (int): year folder to look in
        doy (int): day of year folder to look in
        hour (int): hour folder to look in
        minute (int, optional): If included, restricts files to a particular
        minute (should be around 3 files at most). Defaults to -1.
        second (int, optional): If included, must be either 0, 20, or 40 and
        will restrict search to a single file. Defaults to -1.

    Returns:
        list: A list of files
    """
    path = construct_file_dir_and_name(sat_id, year, doy, hour, minute, second)

    # use gsutil to get the directories available
    # If a directory is requested that doesn't exist, it will throw an error: subprocess.CalledProcessError
    output = subprocess.run(
        [settings.GS_UTIL, "ls", path],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    if output.stderr:
        warnings.warn(
            f"GOES {sat_id} did not have gcloud data available. GS_UTIL ERR: {output.stderr}"
        )

    # split into an actual list removing things that aren't a file
    files = [ii for ii in output.stdout.split("\n") if ii != ""]
    return files


def get_latest_list_from_gcloud(history):
    """get_latest_list_from_gcloud(history)

    Based on the last files loaded (stored in history) downloads new files,
    returns those filenames

    Args:
        history (instance): FileHistory class instance containing the name of
        last folder / file loaded


    Returns:
        list: A list of all files
    """
    all_files = []
    # if the last file doesn't exist, create one based on the time that would be approximately right
    if not history.filename:
        sat_id = history.sat_id
        year = history.year()
        doy = history.doy()
        hour = history.hour()
        minute = history.minute()
        history.set_last_filename(
            f"gs://gcp-public-data-goes-{sat_id :02}/GLM-L2-LCFA/{year :04}/"
            f"{doy :03}/{hour :02}/OR_GLM-L2-LCFA_G{sat_id :02}_s{year :04}"
            f"{doy :03}{hour :02}{minute :02}000_e{year :04}{doy :03}"
            f"{hour :02}{minute :02}200_c00000000000000.nc"
        )

    # try to get the latest files
    latest = FileHistory(datetime.utcnow(), history.sat_id, "")
    files = []
    num_files_in_dir = 0
    while len(files) == num_files_in_dir:
        try:
            files = get_file_list_from_gcloud(
                latest.sat_id, latest.year(), latest.doy(), latest.hour()
            )
        except (
            subprocess.CalledProcessError
        ):  # in case we asked right before a new folder could be created
            try:
                latest.decrement()
                files = get_file_list_from_gcloud(
                    latest.sat_id, latest.year(), latest.doy(), latest.hour()
                )
            except subprocess.CalledProcessError as err:
                raise ValueError(
                    "For sat_id "
                    + str(history.sat_id)
                    + "on date "
                    + latest.date.strftime("%Y/%m/%dT%H:%M:%S")
                    + " and the hour before that returned no data."
                    + " Are you sure you are querying the cloud correctly?"
                    + " The error was-> "
                    + err.stderr
                ) from err

        # record the number of files in the directory
        num_files_in_dir = len(files)

        # grab the file list that comes after the last file read
        if not history.filename:
            raise ValueError("Somehow we got here and history.filename is empty")

        files = [file for file in files if file > history.filename]

        # add the newest files
        all_files = all_files + files

        # step an hour back
        latest.decrement()

    all_files.sort()
    return all_files


def get_available_satellite_ids(start_time_ssue, sat_info_dict):
    """
    Function to get a list of satellite IDs where the given time falls within
    the satellite's operational period.

    Args:
        start_time_ssue (int): Time in seconds since Unix epoch
        sat_dict (dict): Dictionary containing satellite information

    Returns:
        list: List of satellite IDs available at the given time
    """
    available_satellite_ids = []

    # Far future date for satellites without end times
    far_future_datetime_ssue = (datetime(2100, 1, 1) - dth.EPOCH).total_seconds()

    for sat_info in sat_info_dict.values():
        # Get start string name (varies by satellite)
        start_string_key = "GCLOUD_START_STRING"
        end_string_key = "GCLOUD_END_STRING"

        # Get start time
        start_string = sat_info.get(start_string_key)
        if start_string:
            start_time = dth.get_ssue_from_datetime_string(start_string)
        else:
            # Skip if no start time found
            continue

        # Get end time (use far future if not specified)
        end_string = sat_info.get(end_string_key)
        if end_string:
            end_time = dth.get_ssue_from_datetime_string(end_string)
        else:
            end_time = far_future_datetime_ssue

        # Check if input time is within range
        if start_time <= start_time_ssue < end_time:
            available_satellite_ids.append(sat_info["ID"])

    return available_satellite_ids


def get_list_for_specific_window(start_time_ssue, end_time_ssue):
    """[file_list, got_all] = get_list_for_specific_window(start_time_ssue, end_time_ssue)

    Based on a specified time window, gets list of GLM files available during that window

    Args:
        start_time_ssue (int): Time since epoch (in seconds) for the start of
        the time window
        end_time_ssue (int): Time since epoch (in seconds) for the end of the
        time window

    Returns:
        list: [file_list, got_all]
                file_list (list): list of files (including paths) on the Google
                cloud platform for GLM files that fall within the specified
                window
                got_all (bool): If true, all expected files were on the Google
                cloud platform for the specified window
    """
    # Check for satellites which were operational between start and end times
    sat_ids = get_available_satellite_ids(start_time_ssue, settings.SAT_INFO_DICT)

    # initialize the file list
    file_list = []
    got_all = True

    # start off at start time adjusted to file start times (on 20 second intervals)
    time = int(start_time_ssue)
    time = time - (time % GLM_FILE_LENGTH_S)
    while time <= end_time_ssue:
        # calculate the year, doy, hour
        [year, doy, hour, minute, second] = dth.get_year_doy_time_from_ssue(time)

        # loop through all satellites
        for sat_id in sat_ids:
            # pull the data
            try:
                files = get_file_list_from_gcloud(
                    sat_id, year, doy, hour, minute, second
                )
                if len(files) > 1:
                    warnings.warn(
                        f"Got {str(len(files))} files back instead of 1. Using last file received."
                    )
                    files = [files[-1]]
                    print(files)
            except (
                subprocess.CalledProcessError
            ):  # in case we query a directory that has not yet been created
                got_all = False
                continue

            file_list.extend(files)

        # increment time
        time += GLM_FILE_LENGTH_S

    return [file_list, got_all]


def save_gcloud_files_to_dir(data_path, filenames):
    """save_gcloud_files_to_dir(data_path, filenames)

    Save the files listed in filenames from Google cloud to data_path on the
    local system

    Args:
        data_path (string): path to save the data on the local system (must end
        in /)
        filenames (list): list of files stored on the Google cloud services to
        save to local system

    Returns:
        bool: True if succeeded. False otherwise.
    """

    # make sure filenames is a list of filenames and not a single string
    if isinstance(filenames, str):
        filenames = [filenames]

    num_failed = 0
    for file in filenames:
        try:
            subprocess.run(
                [settings.GS_UTIL, "cp", file, data_path[:-1]],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
        except subprocess.CalledProcessError:
            print(file + " failed to download!")
            num_failed += 1

    # display the number of failed files
    if num_failed > 0:
        print(f"{num_failed} out of {len(filenames)} files failed to download.")

    # if all files failed, return false, otherwise return true
    if num_failed == len(filenames):
        return False

    return True
