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
import warnings
from datetime import datetime, timedelta

import numpy as np
import numpy.ma as ma
import zmq
from google.protobuf.json_format import MessageToJson
from matplotlib import pyplot as plt
from netCDF4 import Dataset
from pandas import DataFrame

import src.helper_funs.datetime_helpers as dth
import src.helper_funs.geo_helpers as ghf
import src.helper_funs.smtp_helpers as smtp
import src.helper_funs.velocity_helpers as vhf
from config import glmtriggergenconfig as settings
from src import rocketUtils
from src.helper_funs.calibration_helpers import find_nearest_unmasked_value
from src.helper_funs.file_io_helpers import get_glm_file_meta
from src.helper_funs.math_helpers import comb, continuous_above_min, energy_filter
from src.helper_funs.plotting_helpers import plot_pairs
from src.helper_funs.util_helpers import debug_print, in_glm_file_latter_half
from src.protobuf import glm_pb2, msg_track_pb2

# Constants which affect the degree to which the calibration tables are
# reduced. All lat/lons are kept if they fall within +- of the following
# respective constants.
HALF_LON_DIFF_WINDOW_DEGREES = 2
HALF_LAT_DIFF_WINDOW_DEGREES = 2

# Assumed cloudtop altitude (meters) at event locations
GLM_CLOUDTOP_ALT_M = 20.0e03

# The ratio of area under the black body curve divided by the spectral radiance
# of the black body curve at 777.4 nm
SPECTRAL_IRRADIANCE_TO_INTEGRATED_IRRADIANCE_M = 1.16e-06

# Approx distance between latitude lines in meters
DLAT_DIST_M = 111.0e3

# Multiplicative factors used for initial distance filtering
ROUGH_LAT_DISTANCE_FACTOR = 3
ROUGH_LON_DISTANCE_FACTOR = 7.5

# Only data with energies above the following threshold will be included in
# constructing the group size metric
ENERGY_PERCENT_CAP = 90
# The group size metric only considers group sizes above the following threshold
GROUP_SIZE_MIN = 5
# Mark all clusters who's metrics fall above this threshold as BAD_CLUSTER_ID
GROUP_SIZE_METRIC_THRESHOLD = 0.20

# A threshold for the trigonometric sine of the angle between sat positions
# used for determining if two LOS are too close to parallel.
PARALLEL_THRESHOLD_RADIANS = np.pi / 18

# GLM sampling period lengths in seconds
GLM_SAMPLE_PERIOD_S = 0.02
HALF_GLM_SAMPLE_PERIOD_S = GLM_SAMPLE_PERIOD_S / 2

# Default nonstereo altitude estimate for an event (in meters)
DEFAULT_NONSTEREO_ALTITUDE_ESTIMATE_M = 32000

# GOES-19 anomaly regions
GOES19_ANOMALY_LAT_LONS = [(-21.2, -121.4), (3.4, -127.9)]
GOES19_ANOMALY_TOLERANCE_DEG = 0.5

# Only data with energies above the following threshold will be included in
# the velocity estimates
ENERGY_PERCENT_FLOOR = 10

# The minimum number of points required for a velocity estimate
MIN_NUM_POINTS_FOR_VEL_ESTIMATE = 13

# The maximum speed for which a velocity estimate can be before discarding
MAX_SPEED_THRESHOLD_KMPS = 100


class GlmDataSet:
    """class GlmDataSet

    Defines a class for storing and processing GLM data.

    Class Members:

        CONSTANTS:

        CLOUD_TOP_EQUATOR_M - Height in meters of the cloud top layer defined
        used by the L2 GLM data processing (at the equator)

        CLOUD_TOP_POLE_M - Height in meters of the cloud top layer defined used
        by the L2 GLM data processing (at the poles)

        HIGH_ALTITUDE_M - The highest altitude (in meters) at which events might
        occur

        LOW_ALTITUDE_M - The lowest altitude (in meters) at which events might
        occur

        BAD_CLUSTER_ID - The ID to give points removed from a cluster because
        they are considered to be outside the normal event

        The following are parameters taken from the "event" information in the
        GLM data files.

        event_lat - The event (or pixel) latitude (in degrees)

        event_lon - The event (or pixel) longitude (in degrees)

        event_energy - The event (or pixel) energy (in joules)

        event_parent_group_id - The parent group id for which the event belongs
        to. See the NOAA GLM ATBD for more information on the hierarchical
        structure between events and groups (and flashes which are not used
        here).

        The following are parameters taken from the "group" information in the
        GLM data files or derived from those parameters. For our purposes, the
        group is taken as a line-of-sight from the satellite to an unknown point
        somewhere between HIGH_ALTITUDE_M and LOW_ALTITUDE_M.

        group_id - the "group_id" parameter provided from the GLM data file

        cloud_top_lat_lon_deg - the latitude and longitude (in degrees) provided
        for the point in the file

        sat_pos_ecef_m - the position of the satellite at the time the point was
        recorded.

        high_pos_ecef_m - the position in the ECEF coordinate frame (in meters) at
        HIGH_ALTITUDE_M given the satellite position
        and look direction derived from cloud_top_lat_lon_deg

        low_pos_ecef_m - the position in the ECEF coordinate frame (in meters) at
        LOW_ALTITUDE_M given the satellite position and look direction derived
        from cloud_top_lat_lon_deg

        basetime_ssue - the seconds since unix epoch of the basetime for the file
        (scalar)

        basetime_str - the string version of basetime_ssue in the format
        '%Y/%m/%d %H:%M:%S

        time_s - seconds past basetime_ssue for the point

        energy_joules - the energy provided in the file for the point (in joules)

        sat_id - the ID of the satellite used to record the given point

        cluster_id - the cluster to which the given point was assigned during
        processing

        quality_flag - the quality flag as given in the GLM data file for the
        given point

        fitness - the fitness for the given point to belong to its given cluster

        highest_energy - the highest energy within a given cluster

        ranks - the number of continuous points above a minimal threshold for
        a given cluster

        Class Functions:

        __init__ - create an instance of the class with empty arrays for the
        members used to store data

        load_glm_data_at_time - load data in a specified file into the class arrays
        performing the necessary processing to get updated position

        cluster_glm_data - find optimal clusters for the GLM data based on input
        limits of range/time

        mark_bad_points - mark the fitness of the points relative to their clusters

        rank_glm_clusters - determine the ranking of the GLM clusters and return
        the result
    """

    def __init__(self, status_helper):
        # NEEDED CONSTANTS
        # definition of the cloud top layer
        self.CLOUD_TOP_EQUATOR_M = 14e3
        self.CLOUD_TOP_POLE_M = 6e3
        # definition of desired altitudes
        self.HIGH_ALTITUDE_M = 100e3
        self.LOW_ALTITUDE_M = 0
        # cluster ID for points that get removed from a cluster
        self.BAD_CLUSTER_ID = -1

        # Event (pixel) level data
        # initialize data arrays
        self.event_time = np.array([])
        self.event_lat = np.array([])
        self.event_lon = np.array([])
        self.event_energy = np.array([])
        self.event_intensity_wsr = np.array([])
        self.event_parent_group_id = np.array([])

        # Group / Cluster level data
        # unique id provided by the glm data (called group_id)
        self.group_id = np.array([])
        # satellite that provided the data
        self.sat_id = np.array([])
        # earliest and latest times amongst all files in batch processed
        self.files_start_ssue = np.nan
        self.files_end_ssue = np.nan
        # derived cluster (SDL made groups) of the data
        self.cluster_id = np.array([])
        self.num_clusters = 0
        # position information from glm (provided and derived)
        self.cloud_top_lat_lon_deg = np.array([])
        self.sat_pos_ecef_m = np.array([])
        self.high_pos_ecef_m = np.array([])
        self.low_pos_ecef_m = np.array([])
        # a flag indicating whether the satellite is upright (0), inverted (2),
        # or somewhere between (1)
        self.yaw_flip_flag = np.array([])
        # time information (seconds since unix epoch)
        self.time_s = np.array([])
        self.basetime_str = ""
        self.basetime_ssue = 0
        # energy joules
        self.energy_joules = np.array([])

        # Estimated Group / Cluster Parameters
        # source intensity in W/sr (one per cluster)
        self.source_intensity_wpsr = np.array([])
        # cluster parameter estimates dictionary where key is cluster_id
        self.location_ecef_m = {}
        # cluster velocity vector is a disctionary where key is cluster_id and
        # value is a velocity (x,y,z) tuple
        self.velocities = {}

        # cluster rocket prob key is cluster_id and sat_id
        self.rocket_prob = {}

        # Quality information (provided and derived)
        self.quality_flag = np.array([])
        self.fitness = np.array([])
        self.highest_energy = np.array([])
        self.ranks = np.array([])

        # Store the send_status and send_logs methods as glmDataSet methods
        self.send_status = status_helper.send_status
        self.send_logs = status_helper.send_logs

    def count_clusters(self, update_self=False):
        """self.count_clusters()

        Counts the number of unique cluster IDs that do not match the
        self.BAD_CLUSTER_ID.

        Args:
            update_self (bool, optional): Whether self.num_clusters should
            be updated to reflect this recent count. Defaults to False.

        Returns:
            num_unique_clusters (int): The number of unique cluster IDs
        """
        bad_cluster_mask = self.cluster_id == self.BAD_CLUSTER_ID
        good_cluster_ids = self.cluster_id[~bad_cluster_mask]
        num_unique_clusters = len(np.unique(good_cluster_ids))
        if update_self:
            self.num_clusters = num_unique_clusters
        return num_unique_clusters

    def load_glm_files(self, file_paths):
        """load_glm_files(self, file_paths)

        Load the data from all GLM files listed in file_paths

        INPUTS:
            self - class instance

            file_paths - files to process (path and filename)

        OUTPUTS:
            There are no explicit outputs. The class arrays are updated with
            information from the files found.
        """
        if not file_paths:
            return

        # temporary python arrays to hold the data between files
        event_time = []
        event_lat = []
        event_lon = []
        event_energy = []
        event_parent_group_id = []
        lat = []
        lon = []
        time = []
        energy = []
        q_flag = []
        flip_flag = []
        g_id = []
        sat_ids = []
        sat_pos_ecef = []
        files_start_ssue = np.nan
        files_end_ssue = np.nan

        for file_path in file_paths:
            file_start_ssue, file_end_ssue, sat_id = get_glm_file_meta(file_path)
            files_start_ssue = np.nanmin([files_start_ssue, file_start_ssue])
            files_end_ssue = np.nanmax([files_end_ssue, file_end_ssue])

            # open up the file
            nc_data = Dataset(file_path, "r")

            # grab the basetime
            basetime = datetime(2000, 1, 1, 12, 0, 0) + timedelta(
                seconds=float(nc_data.variables["product_time"][:])
            )
            if (basetime - dth.EPOCH).total_seconds() < self.basetime_ssue:
                error_message = (
                    "GOES data ingest relies on processing earlier "
                    "files first, but subsequent file basetime is less "
                    "than current data instance basetime_ssue."
                )
                self.send_logs([("error", error_message)])
            if self.basetime_ssue == 0:
                self.basetime_str = basetime.strftime("%Y/%m/%d %H:%M:%S")
                self.basetime_ssue = (basetime - dth.EPOCH).total_seconds()
            time_adjust = (basetime - dth.EPOCH).total_seconds() - self.basetime_ssue

            # grab satellite position
            sat_pos = ghf.adjusted_lat_lon_to_ecef(
                np.array(
                    [
                        nc_data.variables["nominal_satellite_subpoint_lat"][:],
                        nc_data.variables["nominal_satellite_subpoint_lon"][:],
                        nc_data.variables["nominal_satellite_height"][:].data * 1e3,
                    ]
                )
            )

            # Store the event (or GLM pixel) time, location, energy, and parent group ID
            # Account for change from seconds to milliseconds in L2 data on Dec 4th, 2018
            if basetime < datetime(2018, 12, 4, 0, 0, 0):
                event_time.append(
                    time_adjust
                    + 0.001 * np.float64(nc_data.variables["event_time_offset"][:])
                )
            else:
                event_time.append(
                    time_adjust + np.float64(nc_data.variables["event_time_offset"][:])
                )
            event_lat.append(nc_data.variables["event_lat"][:])
            event_lon.append(nc_data.variables["event_lon"][:])
            # Carefully handle loading the event energies
            event_energy.append(self.extract_event_energy(nc_data))
            event_parent_group_id.append(nc_data.variables["event_parent_group_id"][:])

            # grab the desired information, append to previous values
            lat.append(nc_data.variables["group_lat"][:])
            lon.append(nc_data.variables["group_lon"][:])
            if basetime < datetime(2018, 12, 4, 0, 0, 0):
                group_time = time_adjust + 0.001 * np.float64(
                    nc_data.variables["group_time_offset"][:]
                )
            else:
                group_time = time_adjust + np.float64(
                    nc_data.variables["group_time_offset"][:]
                )
            # If the group_time consist of a single np.float then insert it into a list
            if isinstance(group_time, np.floating):
                group_time = [group_time]
            time.append(group_time)
            energy.append(nc_data.variables["group_energy"][:])
            q_flag.append(nc_data.variables["group_quality_flag"][:])
            g_id.append(nc_data.variables["group_id"][:])
            flip_flag.append(
                list(
                    np.ma.getdata(nc_data.variables["yaw_flip_flag"][:]).tolist()
                    * np.full(len(g_id[-1]), 1)
                )
            )
            sat_ids.append(list(sat_id * np.ones(len(g_id[-1]))))
            sat_pos_ecef.append(np.tile(sat_pos, [len(g_id[-1]), 1]))
        # end of file_path in file_paths

        # store event data as class data members
        self.event_time = np.array(np.concatenate(event_time))
        self.event_lat = np.array(np.concatenate(event_lat))
        self.event_lon = np.array(np.concatenate(event_lon))
        self.event_energy = np.array(np.concatenate(event_energy))
        self.event_intensity_wsr = np.zeros(self.event_energy.shape)
        self.event_parent_group_id = np.array(np.concatenate(event_parent_group_id))

        # process the discovered position data
        self.cloud_top_lat_lon_deg = np.vstack(
            (np.concatenate(lat), np.concatenate(lon))
        ).data.transpose()
        ecef_pos = ghf.adjusted_lat_lon_to_ecef(
            self.cloud_top_lat_lon_deg, self.CLOUD_TOP_EQUATOR_M, self.CLOUD_TOP_POLE_M
        )
        self.sat_pos_ecef_m = np.array(np.concatenate(sat_pos_ecef))
        self.high_pos_ecef_m = ghf.find_pierce_point_at_alt(
            self.sat_pos_ecef_m, ecef_pos, self.HIGH_ALTITUDE_M
        )
        self.low_pos_ecef_m = ghf.find_pierce_point_at_alt(
            self.sat_pos_ecef_m, ecef_pos, self.LOW_ALTITUDE_M
        )

        # store the yaw flip flag
        self.yaw_flip_flag = np.array(np.concatenate(flip_flag))

        # satellite that provided the data
        self.sat_id = np.array(np.concatenate(sat_ids))
        self.files_start_ssue = files_start_ssue
        self.files_end_ssue = files_end_ssue
        # process the other data
        self.group_id = np.array(np.concatenate(g_id))
        self.time_s = np.array(np.concatenate(time))
        # energy joules
        self.energy_joules = np.array(np.concatenate(energy))
        # source intensity in W/sr
        self.source_intensity_wpsr = np.zeros(self.sat_id.shape)
        # derived cluster of the data
        self.cluster_id = np.zeros(self.sat_id.shape)
        # quality information (provided and derived)
        self.quality_flag = np.array(np.concatenate(q_flag))
        self.fitness = np.ones(self.sat_id.shape)
        self.highest_energy = np.zeros(self.sat_id.shape)

    def trim_glm_files(self, start_time_ssue, end_time_ssue):
        """trim_glm_files(self, start_time_ssue, end_time_ssue)

        If the event time is in the first half of a file, trims off the first
        portion of the previous file. If the event time is in the second half
        of a file, trims off the last portion of the subsequent file.

        Args:
            self - class instance

            start_time_ssue - start time in seconds since unix epoch for the
            search time

            end_time_ssue - end time in seconds since unix epoch for the search
            time

        Returns:
            There are no explicit outputs. The class data members trimmed.
        """
        ## Omit data too far away from the event_date
        # Determine if the event_date falls within the first or second half of the associated .nc file
        event_time_ssue = (start_time_ssue + end_time_ssue) / 2

        # Assign valid_times to all indices which are "closer" to the event_date
        if in_glm_file_latter_half(event_time_ssue):
            # Keep all except latter end of the second file
            valid_times = self.time_s < (
                settings.PROCESS_INTERVAL_S * 2
                - ((end_time_ssue - start_time_ssue) / 2)
            )
        else:
            # Keep all except for beginning of first file
            valid_times = self.time_s > ((end_time_ssue - start_time_ssue) / 2)

        # if there were no detections inside our time frame, this is remotely possible
        if sum(valid_times) == 0:
            return

        # shrink the data to the appropriate window
        self.cloud_top_lat_lon_deg = self.cloud_top_lat_lon_deg[valid_times, :]
        self.high_pos_ecef_m = self.high_pos_ecef_m[valid_times, :]
        self.low_pos_ecef_m = self.low_pos_ecef_m[valid_times, :]
        self.yaw_flip_flag = self.yaw_flip_flag[valid_times]
        self.group_id = self.group_id[valid_times]
        self.time_s = self.time_s[valid_times]
        self.energy_joules = self.energy_joules[valid_times]
        self.source_intensity_wpsr = self.source_intensity_wpsr[valid_times]
        self.sat_id = self.sat_id[valid_times]
        self.sat_pos_ecef_m = self.sat_pos_ecef_m[valid_times, :]
        self.cluster_id = self.cluster_id[valid_times]
        self.quality_flag = self.quality_flag[valid_times]
        self.fitness = self.fitness[valid_times]
        self.highest_energy = self.highest_energy[valid_times]

        # end of trim_glm_files

    def extract_event_energy(self, nc_obj):
        """self.extract_event_energy(nc_obj)

        Ground processing results in L2 netCDF files where the
        event_energy variable has a fill value of -1 for missing data.
        However, since the _Unsigned flag is set to true for this
        otherwise (signed) int16 variable, the fill value is converted
        into 65535 (2 ** 16 - 1) when netCDF4 loads the .nc files into
        memory.

        While not all reasons are currently (March 2023) known for what
        causes missing events (pixel energies) in the L2 data,
        converting the missing values into maximum recordable event
        energies (in Joules) gets us closest to the event energies
        present in the L0 data.

        The maximum recordable event energy is estimated by multiplying
        the event_energy scale_factor to the maximum recordable event
        integer and then adding the event_energy add_offset.

        Args:
            nc_obj (Dataset): A Dataset object created by the netCDF4
            python library for a given .nc file.

        Returns:
            event_energies (numpy array): An array of event energies.
        """

        # Extract the event_energy variable from the netCDF object
        nc_event_energy_obj = nc_obj.variables["event_energy"]
        event_energies = np.array(nc_event_energy_obj[:])
        event_energies_mask = nc_event_energy_obj[:].mask

        # If at least one value is missing in the event_energies,
        # replace all of the original FillValues in the event_energies
        # with a new FillValue
        if not isinstance(event_energies_mask, np.bool_):
            # Store the scale_factor and add_offset for the event_energy variable
            event_energy_scale_factor = nc_event_energy_obj.scale_factor
            event_energy_add_offset = nc_event_energy_obj.add_offset

            # Determine if the event_energy variable is stored as an unsigned value
            event_energy_is_unsigned = nc_event_energy_obj._Unsigned.lower()[0] == "t"

            # Determine if the data type of the event_energy variable is a numpy signed int
            event_energy_base_type_is_signed_int = nc_event_energy_obj.dtype.kind == "i"

            # Extract the maximum possible value for the event_energy dtype
            event_energy_type_max_value = np.iinfo(nc_event_energy_obj.dtype).max

            # If the event_energy base type is a signed int and the
            # event_energy _Unsigned flag is true, double the base type
            # max possible value and add one
            if event_energy_base_type_is_signed_int and event_energy_is_unsigned:
                event_energy_type_max_value = 2 * event_energy_type_max_value + 1

            # Create a new fill value by multiplying the event_energy
            # scale_factor to the maximum recordable event integer and
            # then adding the event_energy add_offset
            new_event_energy_fill_value = (
                event_energy_type_max_value * event_energy_scale_factor
                + event_energy_add_offset
            )

            event_energies[event_energies_mask] = new_event_energy_fill_value

        return event_energies

    def load_glm_data_at_time(self, datafolder, start_time_ssue, end_time_ssue):
        """load_glm_data_at_time(self, datafolder, start_time_ssue, end_time_ssue)

        Load the data from all GLM files contained in datafolder that fall
        between start_time_ssue and end_time_ssue. Any data in those files outside
        the specified range will be trimmed. The event level data are trimmed
        later by self.prune_event_data_by_group_id() after triggering clusters are
        formed, but before event energies are calibrated.

        INPUTS:
            self - class instance

            datafolder - path to folder in which to search for files

            start_time_ssue - start time in seconds since unix epoch for the
            search time

            end_time_ssue - end time in seconds since unix epoch for the search
            time

        OUTPUTS:

            num_valid_files - number of files found in the folder to be processed

            startTimeRel - seconds after desired start time of first data point

            endTimeRel - seconds before desired end time of last data point

        NOTE: startTimeRel and endTimeRel should both be small positive numbers.
        Negative numbers would indicate that the data points are being
        incorrectly filtered to the desired time, large positive numbers would
        indicate a lack of data during the desired interval (could be a minor
        issue or a temporary lack of data). The class arrays are updated with
        information from the files found.
        """

        # search the directory for all netcdf files (.nc)
        file_paths = glob.glob(datafolder + "**/*.nc", recursive=True)
        if not file_paths:
            print(
                "No file paths found. "
                + f"Start time: {dth.convert_ssue_to_string(start_time_ssue)}, "
                + f"End time: {dth.convert_ssue_to_string(end_time_ssue)}, "
                + f"Current time: {datetime.utcnow()}"
            )
            return 0  # return if there was no data
        # save variable for valid paths
        valid_paths = []

        # determine start and end time of the files
        for file_path in file_paths:
            file_start_ssue, file_end_ssue, _ = get_glm_file_meta(file_path)
            # if the file is in the right window, load the data and insert into the structure
            if start_time_ssue < file_end_ssue and end_time_ssue >= file_start_ssue:
                valid_paths.append((file_path, file_start_ssue))

        # this shouldn't happen but if it does problems can arise
        if len(valid_paths) == 0:
            print(
                "No files with valid times found. "
                + f"Start time: {dth.convert_ssue_to_string(start_time_ssue)}, "
                + f"End time: {dth.convert_ssue_to_string(end_time_ssue)}, "
                + f"Current time: {datetime.utcnow()}"
            )
            return 0

        # Ensure valid_paths is sorted so the earliest file is processed first
        valid_paths = sorted(valid_paths, key=lambda x: x[1])
        valid_paths = [pathTuple[0] for pathTuple in valid_paths]

        self.load_glm_files(valid_paths)

        self.trim_glm_files(start_time_ssue, end_time_ssue)

        return len(valid_paths)

    def prune_event_data_by_group_id(self, good_cluster_ids):
        """prune_event_data_by_group_id(self)

        This method prunes all of the event (or pixel) lat, lon, energies
        and parent group IDs which have parent group IDs still in the
        good_group_ids.

        Args:
            good_cluster_ids (numpy array): An array of the triggering
            cluster IDs

        Returns:
            (tuple): The pruned eventTime, eventLat, eventLon,
            eventEnergy, and eventParentGroupId numpy arrays
        """
        # Identify the group IDs used within the good clusters
        good_group_ids = self.group_id[np.in1d(self.cluster_id, good_cluster_ids)]

        # Check for all event parent group ID's which are in good_group_ids
        keep_event_bool = np.in1d(self.event_parent_group_id, good_group_ids)

        # Prune the event level data to the pixels which belong to the
        # triggering cluster's groups
        pruned_event_time = self.event_time[keep_event_bool]
        pruned_event_lat = self.event_lat[keep_event_bool]
        pruned_event_lon = self.event_lon[keep_event_bool]
        pruned_event_energy_j = self.event_energy[keep_event_bool]
        pruned_event_intensity_wpsr = self.event_intensity_wsr[keep_event_bool]
        pruned_event_parent_group_id = self.event_parent_group_id[keep_event_bool]

        return (
            pruned_event_time,
            pruned_event_lat,
            pruned_event_lon,
            pruned_event_energy_j,
            pruned_event_intensity_wpsr,
            pruned_event_parent_group_id,
        )

    def compute_source_intensities(
        self, l2_cal_tables_dict, cluster_ids, debug_mode=False
    ):
        """compute_source_intensities(self, cluster_ids, debug_mode=False)

        This method converts the energy on sensor (in joules) to source
        intensity (in W/sr).

        Args:
            l2_cal_tables_dict (dict): A dictionary where the keys are
            the file paths to the .nc calibration table files, and the
            entries are three element lists containing the calibration
            table arrays.
            cluster_ids (numpy array): An array of the triggering cluster IDs
            debug_mode (bool, optional): Turn on additional output for
            troubleshooting the GLM trigger generator. Defaults to False.
        """

        ## Apply calibration calculations to desired energy data members
        # Use sat ID and flip_flag and cluster ID to subset the data
        sat_ids = np.unique(self.sat_id)
        flip_flags = np.unique(self.yaw_flip_flag)

        for sat_id in sat_ids:
            for flip_flag in flip_flags:
                # Skip the "neither" flip_flag
                if flip_flag == 1:
                    print("Flip flag = 1, i.e., Sat neither upright nor inverted.")
                    continue

                in_sat_flip_flag_bools = (self.sat_id == sat_id) & (
                    self.yaw_flip_flag == flip_flag
                )
                # Check if any data belongs to this sat-flipflag combo
                if np.all(~in_sat_flip_flag_bools):
                    continue

                pixel_to_lon_array, pixel_to_lat_array, lookup_table = (
                    self.select_cal_tables(sat_id, flip_flag, l2_cal_tables_dict)
                )

                # Apply calibration calculations to desired energy data
                # members across all provided cluster IDs
                self.within_cluster_calibration(
                    cluster_ids,
                    in_sat_flip_flag_bools,
                    pixel_to_lon_array,
                    pixel_to_lat_array,
                    lookup_table,
                    debug_mode,
                )

    def select_cal_tables(self, sat_id, flip_flag, l2_cal_tables_dict):
        """select_cal_tables(self, sat_id, file_paths, flip_flag)

        Load the continuum calibration tables for the given satellite ID
        and orientation flip_flag.

        Args:
            sat_id (float): The satellite ID number
            flip_flag (int): Orientation of the satellite. Upright=0,
            Inverted=2, Somewhere between upright and inverted=1.
            l2_cal_tables_dict (dict): A dictionary where the keys are
            the file paths to the .nc calibration table files, and the
            entries are three element lists containing the calibration
            table arrays

        Returns:
            pixel_to_lon_array (numpy masked array): An array that maps pixel
            x-y coordinates to diurnal longitudes
            pixel_to_lat_array (numpy masked array): An array that maps pixel
            x-y coordinates to diurnal latitudes
            lookup_table (numpy masked array): An array that maps pixel
            x-y coordinates to calibration lookup table values
        """
        # Select the calibration tables for the given sat and orientation
        sat_id_str = str(int(sat_id))
        sat_id_paths = [
            path for path in l2_cal_tables_dict.keys() if sat_id_str in path
        ]
        if sat_id_str == "16":
            sat_cal_tables_list = l2_cal_tables_dict[sat_id_paths[0]]
        elif sat_id_str == "17" and flip_flag == 0:
            sat_cal_tables_list = l2_cal_tables_dict[
                [path for path in sat_id_paths if "upright" in path][0]
            ]
        elif sat_id_str == "17" and flip_flag == 2:
            sat_cal_tables_list = l2_cal_tables_dict[
                [path for path in sat_id_paths if "inverted" in path][0]
            ]
        elif sat_id_str == "18":
            sat_cal_tables_list = l2_cal_tables_dict[sat_id_paths[0]]
        elif sat_id_str == "19" and flip_flag == 0:
            sat_cal_tables_list = l2_cal_tables_dict[
                [path for path in sat_id_paths if "upright" in path][0]
            ]
        elif sat_id_str == "19" and flip_flag == 2:
            sat_cal_tables_list = l2_cal_tables_dict[
                [path for path in sat_id_paths if "inverted" in path][0]
            ]
        else:
            print(
                f"Sat ID ({int(sat_id)}) and yaw_flip_flag ({flip_flag}) "
                "not recognized for calibration table selection."
            )

        # Unpack the individual calibration tables for the given sat and
        # orientation
        [pixel_to_lon_array, pixel_to_lat_array, lookup_table] = sat_cal_tables_list

        return pixel_to_lon_array, pixel_to_lat_array, lookup_table

    def within_cluster_calibration(
        self,
        cluster_ids,
        in_sat_flip_flag_bools,
        pixel_to_lon_array,
        pixel_to_lat_array,
        lookup_table,
        debug_mode,
    ):
        """within_cluster_calibration(self, cluster_ids, in_sat_flip_flag_bools,
                                    pixel_to_lon_array, pixel_to_lat_array,
                                    lookup_table, debug_mode)

        Apply calibration calculations to desired energy data members
        across all provided cluster IDs

        Args:
            cluster_ids (numpy array): An array of the triggering cluster IDs
            in_sat_flip_flag_bools (numpy array): A boolean array where True
            indicates when a data member index belongs to a
            satellite-flip_flag combination
            pixel_to_lon_array (numpy masked array): An array that maps pixel
            x-y coordinates to diurnal longitudes
            pixel_to_lat_array (numpy masked array): An array that maps pixel
            x-y coordinates to diurnal latitudes
            lookup_table (numpy masked array): An array that maps pixel
            x-y coordinates to calibration lookup table values
            debug_mode (bool): Turn on additional output for
            troubleshooting the GLM trigger generator
        """
        for cluster_id in cluster_ids:
            # Skip the bad cluster IDs
            if cluster_id == self.BAD_CLUSTER_ID:
                continue

            # Index points with same cluster ID, satellite ID, and flip flag
            in_cluster_sat_bools = (
                self.cluster_id == cluster_id
            ) & in_sat_flip_flag_bools
            # Check if any data belongs to this cluster-sat-flipflag
            if np.all(~in_cluster_sat_bools):
                continue

            # Pick off the Sat position of the first point
            # (these are likely to be the same across all points
            # within the same sat)
            sat_pos_ecef_m = self.sat_pos_ecef_m[in_cluster_sat_bools][0]

            # Subset data members by the cluster-sat ID boolean index
            cluster_sat_lat_lon_deg = self.cloud_top_lat_lon_deg[in_cluster_sat_bools]
            group_ids_in_cluster_sat = self.group_id[
                in_cluster_sat_bools
            ]  # These should all be unique

            # Prune the calibration tables to the cluster area
            cal_data_near_lat_lon, lat_lon_pixel_array = self.prune_calibration_tables(
                cluster_sat_lat_lon_deg, pixel_to_lon_array, pixel_to_lat_array
            )
            if not cal_data_near_lat_lon:
                print("Error. No calibration data near the trigger location.")
                continue

            # Store the summed event, i.e., group source intensity
            group_source_intensities_wpsr = self.within_group_calibration(
                group_ids_in_cluster_sat,
                lat_lon_pixel_array,
                lookup_table,
                sat_pos_ecef_m,
                debug_mode,
            )

            self.source_intensity_wpsr[in_cluster_sat_bools] = (
                group_source_intensities_wpsr
            )

    def prune_calibration_tables(
        self, cluster_sat_lat_lon_deg, pixel_to_lon_array, pixel_to_lat_array
    ):
        """prune_calibration_tables(self, cluster_sat_lat_lon_deg,
                                  pixel_to_lon_array, pixel_to_lat_array)

        Reduce the calibration tables to an array of lats, lons, pixel x,
        and pixel y coordinates which are close to the center lat-lon of
        the cluster

        Args:
            cluster_sat_lat_lon_deg (numpy array): The cloud-top lat-lons
            which belong to the cluster-sat-flip_flag combination
            pixel_to_lon_array (numpy masked array): An array that maps pixel
            x-y coordinates to diurnal longitudes
            pixel_to_lat_array (numpy masked array): An array that maps pixel
            x-y coordinates to diurnal latitudes

        Returns:
            A tuple of the following:
                (boolean): True if the calibration table was reduced
                lat_lon_pixel_array (numpy array): An array of lats, lons,
                pixel x, and pixel y coordinates which are close to the
                center lat-lon of the cluster
        """
        # Find the median group lat and lon for the cluster
        cluster_sat_lat_med = np.median(cluster_sat_lat_lon_deg[:, 0])
        cluster_sat_lon_med = ghf.wrap_longitudes(
            np.median(cluster_sat_lat_lon_deg[:, 1]), 0
        )

        # Find all lons within HALF_LON_DIFF_WINDOW_DEGREES of cluster_sat_lon_med
        near_lon_med_array = (
            ma.abs(pixel_to_lon_array - cluster_sat_lon_med)
            < HALF_LON_DIFF_WINDOW_DEGREES
        )
        # Similarly for the lats
        near_lat_med_array = (
            ma.abs(pixel_to_lat_array - cluster_sat_lat_med)
            < HALF_LAT_DIFF_WINDOW_DEGREES
        )

        # Find shared pixel coordinates between intersection of arrays
        near_lat_lon_mask = near_lon_med_array & near_lat_med_array

        # Check if any data falls within the calibration tables
        if np.all(~near_lat_lon_mask):
            return (False, None)
        shared_pixel_coords = np.asarray(ma.where(near_lat_lon_mask)).T

        pixel_lon_reduced_array = pixel_to_lon_array[near_lat_lon_mask]
        pixel_lat_reduced_array = pixel_to_lat_array[near_lat_lon_mask]

        lat_lon_pixel_array = np.hstack(
            (
                pixel_lat_reduced_array[np.newaxis].T,
                pixel_lon_reduced_array[np.newaxis].T,
                shared_pixel_coords,
            )
        )

        return (True, lat_lon_pixel_array)

    def within_group_calibration(
        self,
        group_ids_in_cluster_sat,
        lat_lon_pixel_array,
        lookup_table,
        sat_pos_ecef_m,
        debug_mode,
    ):
        """self.within_group_calibration(group_ids_in_cluster_sat, lat_lon_pixel_array,
                                       lookup_table, sat_pos_ecef_m, debug_mode)

        Compute the source intensity for a given cluster-sat-flip_flag
        combination across all respective groups

        Args:
            group_ids_in_cluster_sat (numpy array): An array of group IDs
            which occur within a given cluster-sat-flip_flag combination
            lat_lon_pixel_array (numpy array): An array of lats, lons,
            pixel x, and pixel y coordinates which are close to the
            center lat-lon of the cluster
            lookup_table (numpy masked array): An array that maps pixel
            x-y coordinates to calibration lookup table values
            sat_pos_ecef_m (numpy array): The satellites ECEF position
            coordinates (x, y, z)
            debug_mode (bool): Turn on additional output for
            troubleshooting the GLM trigger generator

        Returns:
            summed_event_intensities (numpy array): An array of the summed
            calibrated event intensities
        """
        # Initialize an array for collecting the summed event intensities
        summed_event_intensities = np.zeros(len(group_ids_in_cluster_sat))

        # Calibrate each individual event energy within each group ID
        # and sum to a new group energy in joules
        for group_ind, group_id in enumerate(group_ids_in_cluster_sat):
            debug_print(f"\tGroup ID = {group_id}", debug_mode=debug_mode)
            # Subset the event data associated with the parent group ID
            keep_event_bool = self.event_parent_group_id == group_id
            event_lats_deg = self.event_lat[keep_event_bool]
            event_lons_deg = self.event_lon[keep_event_bool]
            event_energies_j = self.event_energy[keep_event_bool]

            # Ensure longitudinals are within 0 to -360
            event_lons_deg = ghf.wrap_longitudes(event_lons_deg, 0)

            ## Assuming the event occurred at cloud-top-
            ## height, convert lat and lon to Ecef
            event_lat_lon_deg = np.column_stack((event_lats_deg, event_lons_deg))
            event_cloud_top_pos_ecefs_m = ghf.adjusted_lat_lon_to_ecef(
                event_lat_lon_deg,
                GLM_CLOUDTOP_ALT_M,
                GLM_CLOUDTOP_ALT_M,
            )

            # Sum all of the event source intensities to get a group source intensity
            event_intensities_wpsr = self.calibrate_events(
                event_energies_j,
                event_cloud_top_pos_ecefs_m,
                event_lons_deg,
                event_lats_deg,
                lat_lon_pixel_array,
                lookup_table,
                sat_pos_ecef_m,
            )
            summed_event_intensities[group_ind] = np.sum(event_intensities_wpsr)
            debug_print(
                f"Summed EventIntensity = {np.sum(event_intensities_wpsr)}",
                debug_mode=debug_mode,
            )

            # Store the event intensities for the given group
            self.event_intensity_wsr[keep_event_bool] = event_intensities_wpsr

        return summed_event_intensities

    def calibrate_events(
        self,
        event_energies_j,
        event_cloud_top_pos_ecefs_m,
        event_lons_deg,
        event_lats_deg,
        lat_lon_pixel_array,
        lookup_table,
        sat_pos_ecef_m,
    ):
        """self.calibrate_events(event_energies_j, event_cloud_top_pos_ecefs_m,
                                event_lons_deg, event_lats_deg, lat_lon_pixel_array,
                                lookup_table, sat_pos_ecef_m)

        Calibrate all of the event source intensities to get a
        group source intensity. Note: A saturating pixel is assigned the
        value 65535.0 (2^16 - 1) in the event level data. These values
        are omitted from the calibration calculations.

        Args:
            event_energies_j (numpy array): An array of event (pixel)
            energies (in Joules) for a given group
            event_cloud_top_pos_ecefs_m (numpy array): An array of event (pixel)
            cloud-top ECEF coordinates (in meters) for a given group
            event_lons_deg (numpy array): An array of event (pixel)
            longitudes (in degrees) for a given group
            event_lats_deg (numpy array): An array of event (pixel)
            latitudes (in degrees) for a given group
            lat_lon_pixel_array (numpy array): An array of lats, lons,
            pixel x, and pixel y coordinates which are close to the
            center lat-lon of the cluster
            lookup_table (numpy masked array): An array that maps pixel
            x-y coordinates to calibration lookup table values
            sat_pos_ecef_m (numpy array): The satellites ECEF position
            coordinates (x, y, z)

        Returns:
            (float): The event intensities (in Watts/steradian)
            for a given group
        """
        # Initialize an event source intensities list
        event_intensities_wpsr = np.zeros(shape=len(event_energies_j))

        for event_ind, event_energy_j in enumerate(event_energies_j):
            # Subset event data
            event_cloud_top_pos_ecef_m = event_cloud_top_pos_ecefs_m[event_ind]
            event_lon_deg = event_lons_deg[event_ind]
            event_lat_deg = event_lats_deg[event_ind]

            # Convert event lat and lons into pixel coords
            (pixel_x, pixel_y) = self.lat_lon_to_pixel_xy(
                lat_lon_pixel_array,
                event_lon_deg,
                event_lat_deg,
            )

            # Calibrate event energies into source intensities
            event_intensities_wpsr[event_ind] = self.calibrate_energy(
                pixel_x,
                pixel_y,
                lookup_table,
                sat_pos_ecef_m,
                event_cloud_top_pos_ecef_m,
                event_energy_j,
            )

        return event_intensities_wpsr

    def lat_lon_to_pixel_xy(self, lat_lon_pixel_array, event_lon_deg, event_lat_deg):
        """self.lat_lon_to_pixel_xy(lat_lon_pixel_array, event_lons_deg, event_lats_deg, event_ind)

        Convert event lat and lon to pixel_x and pixel_y using a reduced
        calibration table. This method finds the pixel associated with
        the minimum absolute difference between the table lat/lon value
        and the actual lat/lon value.

        Args:
            lat_lon_pixel_array (numpy array): An array of lats, lons,
            pixel x, and pixel y coordinates which are close to the
            center lat-lon of the cluster
            event_lon_deg (float): Event longitude coordinate (in degrees)
            event_lat_deg (float): Event latitude coordinate (in degrees)

        Returns:
            (pixel_x, pixel_y) (tuple): The estimated pixel x and y
            coordinates, respectively.
        """
        pixel_x = -1
        pixel_y = -1
        pixel_x_list = []
        pixel_y_list = []
        num_tries = 10

        # Initialize the reducing_lat_lon_pixel_array
        reducing_lat_lon_pixel_array = lat_lon_pixel_array

        for step_ind in range(num_tries):
            # Find the x pixel coordinate for the nearest lon value
            lon_abs_diffs = ma.abs(reducing_lat_lon_pixel_array[:, 1] - event_lon_deg)
            pixel_x = reducing_lat_lon_pixel_array[lon_abs_diffs.argmin(), 2]
            pixel_x_list.append(pixel_x)

            # Reduce lat_lon_pixel_array by pixel_x +- 1 pixels for y search
            reduce_by_x_bools = ma.abs(lat_lon_pixel_array[:, 2] - pixel_x) <= 1
            reducing_lat_lon_pixel_array = lat_lon_pixel_array[reduce_by_x_bools, :]

            # Find the y pixel coordinate for the nearest lat value using
            # the reduced x lat_lon_pixel_array
            lat_abs_diffs = ma.abs(reducing_lat_lon_pixel_array[:, 0] - event_lat_deg)
            pixel_y = reducing_lat_lon_pixel_array[lat_abs_diffs.argmin(), 3]
            pixel_y_list.append(pixel_y)

            # Start checking for a stable solution after a few steps
            if len(pixel_y_list) > 2:
                if (
                    pixel_x_list[step_ind - 2]
                    == pixel_x_list[step_ind - 1]
                    == pixel_x_list[step_ind]
                ) & (
                    pixel_y_list[step_ind - 2]
                    == pixel_y_list[step_ind - 1]
                    == pixel_y_list[step_ind]
                ):
                    break
                if step_ind == num_tries - 1:
                    print("Calibration pixel coordinates may not be optimal.")
                    break

            # If we have reached a stable solution, no need to reduce the array
            # further. Otherwise, reduce lat_lon_pixel_array by pixel_y +- 1
            # pixels for next x search
            reduce_by_y_bools = ma.abs(lat_lon_pixel_array[:, 3] - pixel_y) <= 1
            reducing_lat_lon_pixel_array = lat_lon_pixel_array[reduce_by_y_bools, :]

        return (int(pixel_x), int(pixel_y))

    def calibrate_energy(
        self,
        pixel_x,
        pixel_y,
        lookup_table,
        sat_pos_ecef_m,
        event_cloud_top_pos_ecef_m,
        event_energy_j,
    ):
        """self.calibrate_energy(pixel_x, pixel_y, lookup_table, sat_pos_ecef_m,
                                event_cloud_top_pos_ecef_m, event_energy_j)

        Calibrate event energies (in Joules) into source intensities
        (in Watts/steradian)

        Args:
            pixel_x (int): The sensor pixel x coordinate
            pixel_y (int): The sensor pixel y coordinate
            lookup_table (numpy masked array): An array that maps pixel
            x-y coordinates to calibration lookup table values
            sat_pos_ecef_m (numpy array): The satellites ECEF position
            coordinates (x, y, z)
            event_cloud_top_pos_ecef_m (numpy array): An array of event (pixel)
            cloud-top ECEF coordinates (in meters) for a given group
            event_energy_j (float): The event (pixel) energy (in Joules)

        Returns:
            (float): The calibrated source intensity (in Watts/steradian)
        """
        #  Convert pixel x and y into LUT value (in W/m^2/m)
        lut_value = lookup_table[pixel_x, pixel_y].data.tolist()

        # Masked values for events near the edge of the FOV become zero
        # Find the nearest unmasked lookup table value in those cases
        if lut_value == 0:
            lut_value = find_nearest_unmasked_value(lookup_table, (pixel_x, pixel_y))

        # Compute Range-to-Source for the event
        range_to_source_m = np.linalg.norm(sat_pos_ecef_m - event_cloud_top_pos_ecef_m)

        # Compute intensity_conversion_coefficient
        intensity_conversion_coefficient = (
            SPECTRAL_IRRADIANCE_TO_INTEGRATED_IRRADIANCE_M * (range_to_source_m) ** 2.0
        )

        # Convert event energies into source intensities
        return intensity_conversion_coefficient * event_energy_j * lut_value

    def cluster_glm_data(self, cluster_distance_m, time_distance_s):
        """cluster_glm_data(self,cluster_distance_m, time_distance_s)

        Identify clusters in the data by finding points with a minimal distance
        between them of less than cluster_distance_m and a time difference of
        less than time_distance_s. Not all points in the cluster may share that
        relationship, e.g., if A and B can be clustered and B and C can be clustered
        A and C will also be in the same cluster even if they don't fit the time
        and distance requirements.

        INPUTS:
            self - class instance

            cluster_distance_m - the maximum distance (in meters) two
            lines-of-sight can be separated by to pass the clustering test

            time_distance_s - the time in seconds two lines-of-sight can be
            separated by to pass the clustering test

        OUTPUTS:
            There are no explicit outputs. The cluster_id class member will be
            updated.
        """
        rough_lat_distance_m = ROUGH_LAT_DISTANCE_FACTOR * cluster_distance_m
        rough_lon_distance_m = ROUGH_LON_DISTANCE_FACTOR * cluster_distance_m
        rough_lat_deg = rough_lat_distance_m / DLAT_DIST_M

        # make sure we have data
        if self.high_pos_ecef_m.size == 0:
            return

        # sort the points by time, latitude, and longitude
        sorted_time_indices = np.argsort(self.time_s)
        last_time_index = np.max(sorted_time_indices)

        # Initialize num_clusters using current highest cluster ID
        if self.cluster_id.size == 0:
            num_clusters = 0
        else:
            num_clusters = max(self.cluster_id)

        # loop through all points in order of time
        for current_index in sorted_time_indices:
            # if this doesn't belong to a cluster add it to a new one
            if self.cluster_id[current_index] == 0:
                self.cluster_id[current_index] = num_clusters + 1
                num_clusters += 1

            # if we are on the last point, leave
            # we go this far so that if the last point isn't grouped, it gets added to one here
            if current_index == last_time_index:
                continue

            # determine at this latitude, what the approximate distance between longitude is
            current_time = self.time_s[current_index]
            current_lat = self.cloud_top_lat_lon_deg[current_index, 0]
            current_lon = self.cloud_top_lat_lon_deg[current_index, 1]
            current_cluster_id = self.cluster_id[current_index]

            # determine what the range of latitude and longitudes would be at this point
            dlon_dist_m = np.cos(np.radians(current_lat)) * DLAT_DIST_M
            rough_lon_deg = rough_lon_distance_m / dlon_dist_m

            min_lat = current_lat - rough_lat_deg
            max_lat = current_lat + rough_lat_deg
            min_lon = current_lon - rough_lon_deg
            max_lon = current_lon + rough_lon_deg

            # Find indices of points to compare with that fall within
            # time_distance_s, a rough lat-lon rectangle, and are not in the
            # same cluster
            # Within time_distance_s
            comp_points_bools = (current_time <= self.time_s) & (
                self.time_s <= (current_time + time_distance_s)
            )
            # Within rough lat window
            time_lat_window_bools = (
                min_lat <= self.cloud_top_lat_lon_deg[comp_points_bools, 0]
            ) & (self.cloud_top_lat_lon_deg[comp_points_bools, 0] <= max_lat)
            # Reduce the points to compare with to only those within the time
            # AND lat windows
            comp_points_bools[comp_points_bools] = time_lat_window_bools
            # Within rough lon window
            time_lat_lon_window_bools = (
                min_lon <= self.cloud_top_lat_lon_deg[comp_points_bools, 1]
            ) & (self.cloud_top_lat_lon_deg[comp_points_bools, 1] <= max_lon)
            # Reduce the points to compare with to only those within the time,
            # lat, and lon windows
            comp_points_bools[comp_points_bools] = time_lat_lon_window_bools
            # And are not in the same cluster
            time_lat_lon_id_window_bools = (
                self.cluster_id[comp_points_bools] != current_cluster_id
            )
            # Reduce the points to compare with to only those within the time,
            # lat, lon windows, and that are not in the same cluster
            comp_points_bools[comp_points_bools] = time_lat_lon_id_window_bools
            # Convert the comparison point booleans to indices
            window_indices = np.where(comp_points_bools)[0]

            # For all points within the window, assign to same cluster_id if
            # within cluster_distance_m
            for window_index in window_indices:
                # Compute distance between LOSs
                closest_distance, _, _ = ghf.dist3d_segment_to_segment(
                    self.low_pos_ecef_m[window_index],
                    self.high_pos_ecef_m[window_index],
                    self.low_pos_ecef_m[current_index],
                    self.high_pos_ecef_m[current_index],
                )
                if closest_distance > cluster_distance_m:
                    continue

                # if window_index is already in a cluster, assign all points in
                # that cluster to this one
                if self.cluster_id[window_index] > 0:
                    self.cluster_id[
                        self.cluster_id == self.cluster_id[window_index]
                    ] = current_cluster_id
                else:  # otherwise, just assign it to the cluster
                    self.cluster_id[window_index] = current_cluster_id

        # end of cluster_glm_data

    def mark_redundant_clusters(self, event_time_ssue):
        """markBoundaryClusters(self, event_time_ssue)

        INPUTS:
            self - class instance

            event_time_ssue -

        OUTPUTS:
            There are no explicit outputs. The cluster_id class member will be
            updated.
        """

        # Mark every cluster as either a (1) outer boundary, or (2) first or second file redundant cluster.
        # Find the boundaries with respect to the relative time_s
        times_ssue = self.basetime_ssue + self.time_s
        # (1) outer boundary clusters
        if in_glm_file_latter_half(event_time_ssue):
            are_outer = (
                times_ssue <= self.files_start_ssue + settings.CLUSTER_TIME_S
            ) | (
                times_ssue
                >= self.files_end_ssue
                - settings.PROCESS_TIME_SIZE_S / 2
                - settings.CLUSTER_TIME_S
            )
        else:
            are_outer = (
                times_ssue
                <= self.files_start_ssue
                + settings.PROCESS_TIME_SIZE_S / 2
                + settings.CLUSTER_TIME_S
            ) | (times_ssue >= self.files_end_ssue - settings.CLUSTER_TIME_S)
        outer_cluster_ids = np.unique(self.cluster_id[are_outer])

        # Mark redundant outer clusters
        are_outer_clusters = np.in1d(self.cluster_id, outer_cluster_ids)
        self.cluster_id[are_outer_clusters] = self.BAD_CLUSTER_ID

        # (2) inner boundary, (3) first file, and (4) second file clusters
        cluster_ids = np.unique(self.cluster_id)

        file_mid_ssue = (self.files_end_ssue + self.files_start_ssue) / 2
        first_file_cluster_ids = []
        second_file_cluster_ids = []

        for cluster_id in cluster_ids:
            # Skip the bad cluster IDs
            if cluster_id == self.BAD_CLUSTER_ID:
                continue

            # Index points with same cluster
            cluster_bools = self.cluster_id == cluster_id

            # Skip if no points belong to this cluster
            if np.all(~cluster_bools):
                continue

            # Subset times belonging to same cluster
            cluster_times_ssue = times_ssue[cluster_bools]

            # Define which file the clusters "belong" to
            if in_glm_file_latter_half(event_time_ssue):
                # Store the start time of the cluster
                cluster_start_ssue = np.min(cluster_times_ssue)
                if cluster_start_ssue < file_mid_ssue + settings.CLUSTER_TIME_S:
                    first_file_cluster_ids.append(cluster_id)
                else:
                    second_file_cluster_ids.append(cluster_id)
            else:
                # Store the start time of the cluster
                cluster_end_ssue = np.max(cluster_times_ssue)
                if cluster_end_ssue > file_mid_ssue - settings.CLUSTER_TIME_S:
                    second_file_cluster_ids.append(cluster_id)
                else:
                    first_file_cluster_ids.append(cluster_id)

        if in_glm_file_latter_half(event_time_ssue):
            # Keep first file clusters
            are_redundant_clusters = np.in1d(self.cluster_id, second_file_cluster_ids)
        else:
            # Keep second file clusters
            are_redundant_clusters = np.in1d(self.cluster_id, first_file_cluster_ids)

        # Mark redundant clusters
        self.cluster_id[are_redundant_clusters] = self.BAD_CLUSTER_ID

        # end of mark_redundant_clusters

    def mark_long_durations(self, debug_mode=False):
        """mark_long_durations(self)

        Marks clusters as BAD_CLUSTER_ID if any cluster duration lasts
        beyond settings.CLUSTER_DURATION_LIMIT_S.

        INPUTS:
            self - class instance

        OUTPUTS:
            There are no explicit outputs.  The cluster_id class member
            will be updated for each data point.
        """
        # Grab all the unique cluster ids in the data
        cluster_ids = np.unique(self.cluster_id)

        for cluster_id in cluster_ids:
            # Skip the bad cluster IDs
            if cluster_id == self.BAD_CLUSTER_ID:
                continue

            # Index points with same cluster
            cluster_bools = self.cluster_id == cluster_id

            # Skip if no points belong to this cluster
            if np.all(~cluster_bools):
                continue

            # Subset times belonging to same cluster
            times_s = self.time_s[cluster_bools]

            # Compute the duration in seconds (i.e., range of time
            # values) of the event using numpy's peak-to-peak function
            duration_s = np.ptp(times_s)
            debug_print(
                f"Cluster ID {cluster_id} duration (seconds): {duration_s}", debug_mode
            )

            # Mark cluster as BAD_CLUSTER_ID if any cluster duration
            # lasts beyond settings.CLUSTER_DURATION_LIMIT_S
            if duration_s > settings.CLUSTER_DURATION_LIMIT_S:
                self.cluster_id[cluster_bools] = self.BAD_CLUSTER_ID
                debug_print(
                    f"Cluster ID {cluster_id} beyond duration limit.", debug_mode
                )

    def omit_large_group_size_clusters(self, cluster_ids, data_dir, debug_mode=False):
        """self.omit_large_group_size_clusters(cluster_ids)

        Marks clusters as BAD_CLUSTER_ID if any cluster has a proportion
        above 0.8 of group sizes larger than 5, considering only the
        group sizes which have energies above the 90th percentile.

        The metric is computed as follows: For each combination of
        cluster ID and sat ID, extract the data who's energy is above the
        90th percentile. Then use all of the group IDs to gather all of
        the event data, and compute the proportion of group cluster sizes
        (number of events per group) greater than 5 events. If the
        proportion of groups satisfying this condition is above 0.8,
        mark the cluster as BAD_CLUSTER_ID.

        Note: The constants used in this metric were determined through
        a grid search of parameters on the training data.

        INPUTS:
            self: class instance
            cluster_ids (numpy array): An array of cluster IDs
            data_dir (string): The name of the directory for the debug plots
            debug_mode (bool, optional): Turn on additional output for
            troubleshooting the GLM trigger generator. Defaults to False.

        OUTPUTS:
            cluster_ids (numpy array): An updated array of cluster IDs
        """
        num_clusters_before_filters = len(cluster_ids)

        for cluster_id_ind, cluster_id in enumerate(cluster_ids):
            # Skip the bad cluster IDs
            if cluster_id == self.BAD_CLUSTER_ID:
                continue

            in_cluster_bools = self.cluster_id == cluster_id
            if np.all(~in_cluster_bools):
                continue

            # Identify all sat IDs within cluster
            sat_ids = np.unique(self.sat_id[in_cluster_bools])

            # Initialize a list for sat metrics to be combined into a cluster metric
            sat_cluster_metrics = np.zeros(len(sat_ids))

            for sat_id_ind, sat_id in enumerate(sat_ids):
                # Index points with same cluster and satellite
                in_cluster_sat_id_bools = in_cluster_bools & (self.sat_id == sat_id)
                if np.all(~in_cluster_sat_id_bools):
                    continue

                # Use only the data which is in the upper ENERGY_PERCENT_CAP of energy
                energy_j = self.energy_joules[in_cluster_sat_id_bools]
                energy_percentile_threshold = np.percentile(
                    energy_j, ENERGY_PERCENT_CAP
                )
                higher_energy_bools = energy_j > energy_percentile_threshold

                # Check that at least one point is included
                if np.all(~higher_energy_bools):
                    continue

                # Subset event point indices by in_cluster_sat_id_bools and higher_energy_bools
                high_energy_group_point_inds = np.where(in_cluster_sat_id_bools)[0][
                    higher_energy_bools
                ]

                # Initialize an array for group cluster sizes for the highest energy group points
                group_cluster_size_array = np.zeros(len(high_energy_group_point_inds))

                for group_cluster_size_ind, point_ind in enumerate(
                    high_energy_group_point_inds
                ):
                    group_id = self.group_id[point_ind]
                    group_cluster_size = np.sum(self.event_parent_group_id == group_id)
                    group_cluster_size_array[group_cluster_size_ind] = (
                        group_cluster_size
                    )

                # Compute proportion of groups with more than GROUP_SIZE_MIN events
                group_size_metric = np.sum(
                    group_cluster_size_array > GROUP_SIZE_MIN
                ) / len(group_cluster_size_array)

                # Store the metric for later analysis
                sat_cluster_metrics[sat_id_ind] = group_size_metric

                if debug_mode:
                    # Plot metric distribution
                    pcntls = np.percentile(
                        group_cluster_size_array, [0, 25, 50, 75, 95, 100]
                    )
                    clstr_mean = group_cluster_size_array.mean()
                    basetime = self.time_s[in_cluster_sat_id_bools][
                        np.argmax(self.energy_joules[in_cluster_sat_id_bools])
                    ]
                    event_datetime = dth.convert_ssue_to_datetime(
                        basetime + self.basetime_ssue
                    )

                    fig = plt.figure()
                    fig.suptitle(f"Cluster {cluster_id} GOES {sat_id}")
                    plt.hist(group_cluster_size_array, range=[0, 40])
                    plt.plot(pcntls[2], 0, "b|", label=f"Median = {pcntls[2]}")
                    plt.plot(
                        clstr_mean, 0, "r|", label=f"Mean = {round(clstr_mean, 1)}"
                    )
                    plt.plot(pcntls[5], 0, "b|", label=f"Max = {pcntls[5]}")
                    plt.plot(
                        0,
                        0,
                        "none",
                        label=f"PropAbove5 = {round(group_size_metric, 2)}",
                    )
                    plt.legend()
                    plt.xlabel("Group Cluster Size (Number of Pixels)")
                    plt.ylabel("Counts")
                    fig.savefig(
                        data_dir
                        + event_datetime.strftime("%Y%m%d%H%M%S")
                        + f"_{cluster_id}_{sat_id}_ClusterHist.png"
                    )
                    plt.close()

            # Combine the sat metrics into a cluster metric
            cluster_size_metric = np.array(max(sat_cluster_metrics))

            # Filter out clusters which fail a metric criteria
            if cluster_size_metric > GROUP_SIZE_METRIC_THRESHOLD:
                cluster_ids[cluster_id_ind] = self.BAD_CLUSTER_ID

        cluster_ids = cluster_ids[cluster_ids != self.BAD_CLUSTER_ID]

        debug_message = (
            f"{num_clusters_before_filters - len(cluster_ids)} weak "
            f"clusters filtered as lightning ({len(cluster_ids)} remain)"
        )
        self.send_logs([("debug", debug_message)])

        return cluster_ids

    def mark_low_altitude_stereo_events(
        self, max_num_comparisons=10, altitude_threshold_m=20e3, debug_mode=False
    ):
        """mark_low_altitude_stereo_events(self)

        For stereo clusters, computes the estimated altitude of the
        event at peak brightness. If the estimated altitude is below
        altitude_threshold_m, the cluster is marked as a bad cluster.

        INPUTS:
            self - class instance

            max_num_comparisons (int, optional): maximum number of
            energies to collect per satellite for comparing in order to
            align energy distributions. Defaults to 10.

            altitude_threshold_m (float, optional): the threshold (in
            meters) for which all stereo cluster IDs with estimated
            altitudes below will be marked as self.BAD_CLUSTER_ID.
            Defaults to 20e3 meters.

            debug_mode (bool, optional): Turn on additional output for
            troubleshooting the GLM trigger generator. Defaults to False.

        OUTPUTS:
            There are no explicit outputs. The cluster_id class member
            will be updated for each data point.
        """
        debug_print("\nStart mark_low_altitude_stereo_events()", debug_mode)
        # Get all the cluster ids and sat ids in the data
        unique_cluster_ids = np.unique(self.cluster_id)

        for unique_cluster_id in unique_cluster_ids:
            debug_print(f"\nCluster ID: {unique_cluster_id}", debug_mode)
            # Skip the bad cluster IDs
            if unique_cluster_id == self.BAD_CLUSTER_ID:
                continue

            # Index points with same cluster
            in_cluster_bools = self.cluster_id == unique_cluster_id
            if np.all(~in_cluster_bools):
                continue

            # Get all stereo satellite IDs
            sat_ids_to_compare = self.get_stereo_pair(in_cluster_bools, debug_mode)

            # Skip cluster if no stereo satellites are found
            if len(sat_ids_to_compare) == 0:
                continue

            # Reduce in_cluster_bools to only have sat_ids_to_compare
            sat_ids_to_compare_bools = np.in1d(
                self.sat_id[in_cluster_bools], sat_ids_to_compare
            )
            in_cluster_bools[in_cluster_bools] = sat_ids_to_compare_bools
            # Collect the top max_num_comparisons number of energies,
            # highPosEcef, lowPosEcef, and times
            (_, high_pos_ecef_m, low_pos_ecef_m, times_s) = self.subset_by_top_energies(
                sat_ids_to_compare, in_cluster_bools, max_num_comparisons, debug_mode
            )

            # Marks all cluster_id class members as BAD_CLUSTER_ID if the
            # estimated altitude is below altitude_threshold_m.
            self.mark_low_atl_clusters(
                high_pos_ecef_m,
                low_pos_ecef_m,
                times_s,
                altitude_threshold_m,
                in_cluster_bools,
                unique_cluster_id,
                debug_mode,
                store_location_estimate=True,
            )

        # end of mark_low_altitude_stereo_events

    def get_stereo_pair(self, in_cluster_bools, debug_mode):
        """get_stereo_pair(self, in_cluster_bools, debug_mode)

        Args:
            in_cluster_bools (numpy array): A numpy array of booleans.
            True indicates data which belongs to the same cluster.

            debug_mode (bool, optional): Turn on additional output for
            troubleshooting the GLM trigger generator. Defaults to False.

        Returns:
            sat_ids_to_compare (list): A list of two non-parallel stereo
            satellites.

        Note: The value PARALLEL_THRESHOLD_RADIANS was determined by
        comparing position angles from GOES-16 to 17 and 16 to 18
        against GOES-17 to 18. The 16-17 and 16-18 are 1.082 radians,
        while the 17-18 are approximately zero. The threshold
        guarentees the angle between stereo satellites is at least pi/6.
        """
        sat_pos_ecef_m = self.sat_pos_ecef_m[in_cluster_bools]
        sat_ids = self.sat_id[in_cluster_bools]
        unique_sat_pos = np.unique(
            np.hstack((sat_ids.reshape(-1, 1), sat_pos_ecef_m)), axis=0
        )
        unique_sat_ids = unique_sat_pos[:, 0].astype(int).tolist()
        unique_sat_pos_ecef_m = unique_sat_pos[:, 1:4]

        sat_ids_to_compare = []
        num_sats_within_cluster = len(unique_sat_ids)
        # Check if there are at least two unique satellite positions
        if num_sats_within_cluster >= 2:
            # Compute the pairwise angles between all satellites
            # Compute the sine of the angle between each sat-to-sat comparison
            sine_angle_array = np.zeros(shape=(comb(num_sats_within_cluster, 2), 3))
            comparison_ind = 0
            for sat1ind in range(num_sats_within_cluster - 1):
                sat_pos1_ecef_m = unique_sat_pos_ecef_m[sat1ind]
                for sat2ind in range(sat1ind + 1, num_sats_within_cluster):
                    sat_pos2_ecef_m = unique_sat_pos_ecef_m[sat2ind]
                    x_prod_mag = np.linalg.norm(
                        np.cross(sat_pos1_ecef_m, sat_pos2_ecef_m)
                    )
                    line_of_sight1_mag = np.linalg.norm(sat_pos1_ecef_m)
                    line_of_sight2_mag = np.linalg.norm(sat_pos2_ecef_m)
                    sine_angle_array[comparison_ind] = np.array(
                        [
                            sat1ind,
                            sat2ind,
                            np.arcsin(
                                x_prod_mag / (line_of_sight1_mag * line_of_sight2_mag)
                            ),
                        ]
                    )
                    comparison_ind += 1
            debug_print(f"Sine Angle Array\n{sine_angle_array}", debug_mode)

            # Find all of the non-parallel satellite pairs
            non_parallel_sats = sine_angle_array[
                sine_angle_array[:, 2] > PARALLEL_THRESHOLD_RADIANS, 0:2
            ]
            if len(non_parallel_sats) == 0:
                return sat_ids_to_compare

            # The -1 index picks GOES 16-18 pairs over GOES 16-17 pairs
            sat_ind_to_keep = non_parallel_sats[-1].astype(int).tolist()

            # Translate satellite indices into Sat IDs
            sat_ids_to_compare = [unique_sat_ids[x] for x in sat_ind_to_keep]
            debug_print(f"Sats to compare: {sat_ind_to_keep}", debug_mode)

        return sat_ids_to_compare

    def subset_by_top_energies(
        self, sat_ids_to_compare, in_cluster_bools, max_num_comparisons, debug_mode
    ):
        """subset_by_top_energies(self, sat_ids_to_compare, in_cluster_bools,
        max_num_comparisons, debug_mode)

        For a given cluster, this method:
         (1) Finds the peak energy among the given stereo satellites
         (2) Extracts max_num_comparisons of data values around the
         peak energy for each satellite
        At most, max_num_comparisons number of data
        values for each numpy array in windowedEnergiesJ, high_pos_ecef_m,
        low_pos_ecef_m, and times_s will be collected.

        Args:
            sat_ids_to_compare (list): The non-parallel satellite IDs
            provided by the satellite for loop in
            self.mark_low_altitude_stereo_events.

            in_cluster_bools (numpy array): A numpy array of booleans.
            True indicates data which belongs to the same cluster.

            max_num_comparisons (int): The maximum number of energies to
            collect per satellite for comparing in order to align energy
            distributions.

        Returns:
            A tuple of the following:

            energies_near_peak_time_j (list): A list (of length equal to the number
            of satellites) of (1-demensional) numpy arrays containing
            max_num_comparisons number of energies in Joules which occurred near
            the peak energy among the stereo satellites.

            high_pos_ecef_m (list): A list (of length equal to the number
            of satellites) of (1-demensional) numpy arrays containing
            (max_num_comparisons of) LOS high ECEF coords in meters.

            low_pos_ecef_m (list): A list (of length equal to the number
            of satellites) of (1-demensional) numpy arrays containing
            (max_num_comparisons of) LOS low ECEF coords in meters.

            times_s (list): A list (of length equal to the number
            of satellites) of (1-demensional) numpy arrays containing
            (max_num_comparisons of) times in seconds.
        """
        num_sats_within_cluster = len(sat_ids_to_compare)

        # Initialize objects to store data for nearest points
        energies_near_peak_time_j = [None] * num_sats_within_cluster
        high_pos_ecef_m = [None] * num_sats_within_cluster
        low_pos_ecef_m = [None] * num_sats_within_cluster
        times_s = [None] * num_sats_within_cluster

        # Find time of max energy
        max_energy_in_cluster_index = np.argmax(self.energy_joules[in_cluster_bools])
        max_energy_sat_id = int(
            self.sat_id[in_cluster_bools][max_energy_in_cluster_index]
        )
        max_energy_time_s = self.time_s[in_cluster_bools][max_energy_in_cluster_index]

        # Move the max energy satellite to the first position for mark_low_atl_clusters()
        sat_ids_to_compare = [
            sat_id for sat_id in sat_ids_to_compare if sat_id != max_energy_sat_id
        ]
        sat_ids_to_compare.insert(0, max_energy_sat_id)

        # Attempt to extract values from all of the satellite(s) which
        # occurred at approximately the same times as peak energy
        for sat_id_ind, unique_sat_id in enumerate(sat_ids_to_compare):
            debug_print(f"Sat ID: {unique_sat_id}", debug_mode)
            # Index points with same cluster and satellite
            in_cluster_sat_id_bools = in_cluster_bools & (self.sat_id == unique_sat_id)
            if np.all(~in_cluster_sat_id_bools):
                continue

            # Subset times belonging to same cluster and sat
            times_by_cluster_sat_s = self.time_s[in_cluster_sat_id_bools]

            # Identify index of nearest max_num_comparisons number of energies
            # Times are not necessarily monotonically increasing, search for closest time indices
            abs_time_diffs_s = np.abs(times_by_cluster_sat_s - max_energy_time_s)
            nearest_time_indices = np.argsort(abs_time_diffs_s)
            # Check if enough points exist in the event, otherwise use all
            if len(times_by_cluster_sat_s) >= max_num_comparisons:
                nearest_time_indices = nearest_time_indices[:max_num_comparisons]

            # Get the cooresponding times, ecef coordinates (for
            # both high and low alt) and energies.
            times_s[sat_id_ind] = times_by_cluster_sat_s[nearest_time_indices]
            energies_near_peak_time_j[sat_id_ind] = self.energy_joules[
                in_cluster_sat_id_bools
            ][nearest_time_indices]
            high_pos_ecef_m[sat_id_ind] = self.high_pos_ecef_m[in_cluster_sat_id_bools][
                nearest_time_indices
            ]
            low_pos_ecef_m[sat_id_ind] = self.low_pos_ecef_m[in_cluster_sat_id_bools][
                nearest_time_indices
            ]

        return (energies_near_peak_time_j, high_pos_ecef_m, low_pos_ecef_m, times_s)

        # end of subset_by_top_energies

    def mark_low_atl_clusters(
        self,
        high_pos_ecef_m,
        low_pos_ecef_m,
        times_s,
        altitude_threshold_m,
        in_cluster_bools,
        cluster_id,
        debug_mode=False,
        store_location_estimate=True,
    ):
        """mark_low_atl_clusters(self, high_pos_ecef_m, low_pos_ecef_m, times_s,
            altitude_threshold_m, in_cluster_bools, debug_mode=False)

        Checks for lines-of-sight between satellites that occurred at
        roughly the same time, estimates an altitude for the stereo
        event, and marks all cluster_id class members as BAD_CLUSTER_ID
        if the estimated altitude is below altitude_threshold_m.

        Args:
            high_pos_ecef_m (list): A list (of length equal to the number
            of satellites) of (1-demensional) numpy arrays containing
            (max_num_comparisons of) LOS high ECEF coords in meters.

            low_pos_ecef_m (list): A list (of length equal to the number
            of satellites) of (1-demensional) numpy arrays containing
            (max_num_comparisons of) LOS low ECEF coords in meters.

            times_s (list): A list (of length equal to the number
            of satellites) of (1-demensional) numpy arrays containing
            (max_num_comparisons of) times in seconds.

            altitude_threshold_m (float, optional): the threshold (in
            meters) for which all stereo events with estimated altitudes
            below will be marked as "bad". Defaults to 20e3 meters.

            in_cluster_sat_id_bools (numpy array): A numpy array of booleans.
            True indicates data which belongs to the same cluster.

            cluster_id (float): The cluster ID number

            debug_mode (bool, optional): Turn on additional output for
            troubleshooting the GLM trigger generator. Defaults to False.

            store_location_estimate (bool, optional): Store the location
            estimates of the stereo events

        Returns:
            Nothing is returned. Marks all cluster_id class members as
            BAD_CLUSTER_ID if the estimated altitude is below
            altitude_threshold_m.
        """
        # Within the top max_num_comparisons energies for each satellite,
        # check if there are any lines-of-sight between the satellites which
        # occurred at similar times. If found, use these lines-of-sight for
        # computing the estimated altitude. If not found, do not change the
        # cluster_id

        for time_ind1, time_val1 in enumerate(times_s[0]):
            # Check for other times within HALF_GLM_SAMPLE_PERIOD_S
            # TODO: Add functionality for handling ESA's LI which will have
            # a different sampling period
            matching_time_bools = abs(times_s[1] - time_val1) < HALF_GLM_SAMPLE_PERIOD_S
            # If none match, move to the next highest energy time
            if np.all(~matching_time_bools):
                continue

            # In the event of multiple time matches, pick the index for the
            # higher energy
            time_ind2 = np.min(np.where(matching_time_bools))
            high_pos_ecef0m = high_pos_ecef_m[0][time_ind1]
            low_pos_ecef0m = low_pos_ecef_m[0][time_ind1]
            high_pos_ecef1m = high_pos_ecef_m[1][time_ind2]
            low_pos_ecef1m = low_pos_ecef_m[1][time_ind2]

            # Compute the min distance vector between two lines-of-sight
            [_, seg0p_min, seg1p_min] = ghf.dist3d_segment_to_segment(
                high_pos_ecef0m,
                low_pos_ecef0m,
                high_pos_ecef1m,
                low_pos_ecef1m,
            )
            # Find the middle point of the min distance vector
            min_dist_seg_ecef_ave = np.mean(np.stack([seg0p_min, seg1p_min]), axis=0)
            # Store the estimated location of the stereo event
            if store_location_estimate:
                self.location_ecef_m[str(cluster_id)] = min_dist_seg_ecef_ave
            # Convert the middle point to Geodetic to estimate altitude
            (_, _, estimated_altitude) = ghf.ecef2geodetic(
                min_dist_seg_ecef_ave[0],
                min_dist_seg_ecef_ave[1],
                min_dist_seg_ecef_ave[2],
            )
            debug_print(f"Estimated altitude: {estimated_altitude}", debug_mode)
            # Mark the cluster_id as bad if estimated altitude below 20km
            # Otherwise check next matching times
            if estimated_altitude < altitude_threshold_m:
                debug_print("Filtered out due to low alt.", debug_mode)
                self.cluster_id[in_cluster_bools] = self.BAD_CLUSTER_ID
                # Exit the for-loop which checks for matching times
                break
            # If times matched, and est alt was above
            # altitude_threshold_m, don't mark the cluster_id for this
            # cluster as BAD_CLUSTER_ID
            break

        # end of mark_low_atl_clusters

    def mark_higher_energies(self):
        """mark_higher_energies(self)

        Searches through each cluster for points that have unique or higher
        duplicate energies at each time. The highest_energy data member for these
        points are marked as 1.

        INPUTS:
            self - class instance

        OUTPUTS:
            There are no explicit outputs.  The highest_energy class member will
            be updated for each data point.
        """
        # Grab all the cluster ids and sat ids in the data
        cluster_ids = np.unique(self.cluster_id)
        sat_ids = np.unique(self.sat_id)

        for cluster_id in cluster_ids:
            # Skip the bad cluster IDs
            if cluster_id == self.BAD_CLUSTER_ID:
                continue

            for sat_id in sat_ids:
                # Index points with same cluster and satellite
                in_cluster_sat_id_bools = (self.cluster_id == cluster_id) & (
                    self.sat_id == sat_id
                )
                if np.all(~in_cluster_sat_id_bools):
                    continue

                # Subset times and energies belonging to same cluster and sat
                time_by_cluster_sat_s = self.time_s[in_cluster_sat_id_bools]
                energy_by_cluster_sat_s = self.energy_joules[in_cluster_sat_id_bools]

                ## Find all energies which are unique for their time and mark as highest_energy = 1
                # Find the unique times and counts of those unique times
                unique_times, unique_time_counts = np.unique(
                    time_by_cluster_sat_s, return_counts=True
                )

                # Keep all of the unique times that only appear once
                unique_times_without_duplicates = unique_times[
                    np.where(unique_time_counts == 1)[0]
                ]

                highest_energy_flag_inds = []

                for unique_time in unique_times_without_duplicates:
                    index_of_data_to_keep = np.where(
                        time_by_cluster_sat_s == unique_time
                    )[0]
                    highest_energy_flag_inds.append(index_of_data_to_keep[0])

                ## Find all energies which are duplicates for their time and mark max energy as highest_energy = 1
                # Keep only max energy of the duplicate times
                duplicate_times = unique_times[np.where(unique_time_counts > 1)[0]]

                for duplicate_time in duplicate_times:
                    # Find the indices of all matching duplicate times with duplicate_time
                    identical_times_indicies = np.where(
                        time_by_cluster_sat_s == duplicate_time
                    )[0]

                    # Find the max energy
                    max_energy_among_indentical_times = energy_by_cluster_sat_s[
                        identical_times_indicies
                    ][np.argmax(energy_by_cluster_sat_s[identical_times_indicies])]

                    # Store the index of the max energy for those identical times
                    index_of_time_and_energy_to_keep = np.where(
                        (time_by_cluster_sat_s == duplicate_time)
                        & (energy_by_cluster_sat_s == max_energy_among_indentical_times)
                    )[0]

                    # append index_of_time_and_energy_to_keep to a master list listToKeep
                    highest_energy_flag_inds.append(index_of_time_and_energy_to_keep[0])

                highest_energy_by_cluster_sat = np.zeros(
                    np.sum(in_cluster_sat_id_bools)
                )
                highest_energy_by_cluster_sat[highest_energy_flag_inds] = np.ones(
                    len(highest_energy_flag_inds)
                )
                self.highest_energy[in_cluster_sat_id_bools] = (
                    highest_energy_by_cluster_sat
                )

        # end of mark_higher_energies

    def mark_bad_points(self):
        """mark_bad_points(self)

        Searches through each cluster for points that have an unexpected drop in
        energy level. The fitness for these points is marked as 0.

        INPUTS:
            self - class instance

        OUTPUTS:
            There are no explicit outputs. The fitness class member will be
            updated for each data point.
        """
        # grab all the cluster ids and sat ids in the data
        cluster_ids = np.unique(self.cluster_id)
        sat_ids = np.unique(self.sat_id)

        for cluster_id in cluster_ids:
            # skip the bad cluster
            if cluster_id == self.BAD_CLUSTER_ID:
                continue

            for sat_id in sat_ids:
                # get the points by the correct cluster and satellite
                ind = np.all(
                    [
                        self.cluster_id == cluster_id,
                        self.sat_id == sat_id,
                        self.highest_energy == 1,
                    ],
                    axis=0,
                )
                if np.all(~ind):
                    continue

                # sort by time
                time_ind = np.argsort(self.time_s[ind])

                energy_filter_width = 5
                max_valid_drop = 5
                # loop forward through the data looking for anomalous differences
                fitness_forward = energy_filter(
                    self.energy_joules[ind][time_ind],
                    0,
                    len(time_ind) - 1,
                    energy_filter_width,
                    max_valid_drop,
                )

                # loop backward through the data looking for anomalous
                # differences
                fitness_backward = energy_filter(
                    self.energy_joules[ind][time_ind],
                    len(time_ind) - 1,
                    0,
                    energy_filter_width,
                    max_valid_drop,
                )

                # combine the two results
                fitness_copy = self.fitness[ind]
                fitness_copy[time_ind] = np.max(
                    np.array([fitness_forward, fitness_backward]), axis=0
                )
                self.fitness[ind] = fitness_copy

        # end of mark_bad_points

    def mark_goes19_anomalies(self):
        """mark_goes19_anomalies(self)

        GOES-19 struggles with sensor anomalies repeatedly at several
        locations. This filter marks all triggers within a small distance
        around these areas as bad clusters. The anomaly locations are
        defined by GOES19_ANOMALY_LAT_LONS, and the window width (in
        degrees) around the anomalous locations is defined as
        GOES19_ANOMALY_TOLERANCE_DEG.

        Note: Since event level intensities have not been computed
        yet, if no event position was found using stereo estimates,
        then get_event_position_ecef() will return a cluster position
        based on the first point source with a higher energy feature = 1
        and a fitness feature = 1. This is sufficient for this
        filter since we are interested in filtering out clusters
        near the GOES-19 anomaly regions.

        INPUTS:
            self - class instance

        OUTPUTS:
            There are no explicit outputs. The bad cluster ID class member
            will be assigned to each cluster which falls within a window
            surrounding the anomalous locations.
        """
        # Grab all the cluster ids and GOES19 sat ID in the data
        unique_cluster_ids = np.unique(self.cluster_id)
        sat_ids = np.array([19.0])  # This only occurs on GOES-19

        # Identify the cluster location at peak brightness
        for unique_cluster_id in unique_cluster_ids:
            # skip the bad cluster
            if unique_cluster_id == self.BAD_CLUSTER_ID:
                continue

            in_cluster_bools = self.cluster_id == unique_cluster_id

            for sat_id in sat_ids:
                # Get the points by the correct cluster, satellite, fitness, and highest_energy
                in_cluster_sat_filtered_bools = np.all(
                    [
                        self.cluster_id == unique_cluster_id,
                        self.sat_id == sat_id,
                        self.highest_energy == 1,
                        self.fitness == 1,
                    ],
                    axis=0,
                )
                # Skip sats with 0 or 1 point in cluster
                if np.sum(in_cluster_sat_filtered_bools) < 2:
                    continue

                # Determine the cluster location
                cluster_position_ecef = self.get_event_position_ecef(
                    cluster_id=unique_cluster_id,
                    in_cluster_bools=in_cluster_sat_filtered_bools,
                )

                # Convert ECEF to geodetic
                (
                    cluster_position_geo_lat,
                    cluster_position_geo_lon,
                    _,
                ) = ghf.ecef2geodetic(
                    cluster_position_ecef[0],
                    cluster_position_ecef[1],
                    cluster_position_ecef[2],
                )

                # Mark the cluster ID as the bad cluster ID if close to
                # the anomalous regions
                for anomaly_lat_lon_tuple in GOES19_ANOMALY_LAT_LONS:
                    if GOES19_ANOMALY_TOLERANCE_DEG > abs(
                        cluster_position_geo_lat - anomaly_lat_lon_tuple[0]
                    ) and GOES19_ANOMALY_TOLERANCE_DEG > abs(
                        cluster_position_geo_lon - anomaly_lat_lon_tuple[1]
                    ):
                        self.cluster_id[in_cluster_bools] = self.BAD_CLUSTER_ID

        # end of mark_goes19_anomalies

    def rank_glm_clusters(self, min_energy_j):
        """rank_glm_clusters(self, min_energy_j)

        Ranks each of the GLM clusters based on the number of continuous points
        above min_energy_j and saves the ranking

        INPUTS:
            self - class instance

            min_energy_j - minimum energy (in joules) above which a point
            must be to count in the continuous curve. When points drop below
            this level the count restarts.

        OUTPUTS:
            There are no explicit outputs. The ranks class member will be
            updated for each cluster.
        """
        # grab all the cluster ids and sat ids in the data
        cluster_ids = np.unique(self.cluster_id)
        sat_ids = np.unique(self.sat_id)

        # Initialize a 2 column ranks array, where columns are
        # cluster_ids and ranks
        self.ranks = np.array([cluster_ids, np.zeros(cluster_ids.shape)]).transpose()

        # Rank using largest number of continuous points above baseline
        for cluster_id_ind, cluster_id in enumerate(cluster_ids):
            # skip the bad cluster
            if cluster_id == self.BAD_CLUSTER_ID:
                continue

            for sat_id in sat_ids:
                # get the points by the correct cluster, satellite, fitness, and highest_energy
                ind = np.all(
                    [
                        self.cluster_id == cluster_id,
                        self.sat_id == sat_id,
                        self.highest_energy == 1,
                        self.fitness == 1,
                    ],
                    axis=0,
                )
                # Skip sats with 0 or 1 point in cluster
                if np.sum(ind) < 2:
                    continue

                # determine the baseline
                sorted_e = np.sort(self.energy_joules[ind])
                subset10 = sorted_e[range(int(np.ceil(len(sorted_e) * 0.1)))]
                baseline = np.median(subset10)  # +subset10.std()

                # sort by time
                time_ind = np.argsort(self.time_s[ind])

                # determine number of continuous points above min_energy_j
                cur_rank = continuous_above_min(
                    self.energy_joules[ind][time_ind] - baseline, min_energy_j, 0
                )
                if cur_rank > self.ranks[cluster_id_ind, 1]:
                    self.ranks[cluster_id_ind, 1] = cur_rank

        # end of rank_glm_clusters

    def rocket_filter(self, cluster_ids, rocket_pipeline):
        """self.rocket_filter(cluster_ids, rocket_pipeline)

        After some data preprocessing, passes cluster data to the rocket
        model. The rocket model generates two "confidence-like"
        probabilities for how sure the model is that the provided data
        was generated by (0) a lightning or other false event or (1) a
        bolide.

        Note: The constants used in the data preprocessing were
        determined through an analysis of the training data and model
        performance. See the rocket_model scripts.

        INPUTS:
            self: class instance
            cluster_ids (numpy array): An array of cluster IDs
            rocket_pipeline (sktime pipeline): The rocket model pipeline
        OUTPUTS:
            cluster_ids (numpy array): An updated array of cluster IDs
        """
        num_clusters_before_filter = len(cluster_ids)

        for cluster_id_ind, cluster_id in enumerate(cluster_ids):
            # Skip the bad cluster IDs
            if cluster_id == self.BAD_CLUSTER_ID:
                continue

            in_cluster_bools = self.cluster_id == cluster_id
            if np.all(~in_cluster_bools):
                continue

            # Identify all sat IDs within cluster
            sat_ids = np.unique(self.sat_id[in_cluster_bools])

            # Initialize a list for sat metrics to be combined into a cluster metric
            sat_cluster_metrics = np.zeros(len(sat_ids))

            for sat_id_ind, sat_id in enumerate(sat_ids):
                # Index points with same cluster and satellite
                # Also, only include highest_energy points with good fitness
                in_cluster_sat_id_bools = (
                    in_cluster_bools
                    & (self.sat_id == sat_id)
                    & (self.fitness == 1)
                    & (self.highest_energy == 1)
                )
                if np.all(~in_cluster_sat_id_bools):
                    continue

                # Subset times and energies belonging to same cluster and sat
                energy_by_cluster_sats = self.energy_joules[in_cluster_sat_id_bools]
                cloud_top_lat_lon_by_cluster_sat_degs = self.cloud_top_lat_lon_deg[
                    in_cluster_sat_id_bools
                ]
                lat_by_cluster_sat_degs = cloud_top_lat_lon_by_cluster_sat_degs[:, 0]
                lon_by_cluster_sat_degs = cloud_top_lat_lon_by_cluster_sat_degs[:, 1]

                # Collect, format, and preprocess the data
                energy_lat_lon_df_list = [
                    DataFrame(
                        np.vstack(
                            (
                                energy_by_cluster_sats,
                                lat_by_cluster_sat_degs,
                                lon_by_cluster_sat_degs,
                            )
                        ).T,
                        columns=["energy", "lat", "lon"],
                    )
                ]

                # Randomly down sample unusually long signals
                energy_lat_lon_df_list = rocketUtils.down_sample_long_events(
                    energy_lat_lon_df_list,
                    settings.DOWN_SAMPLE_LENGTH,
                    settings.RANDOM_STATE_SEED,
                )
                # Z-score standardization across all variables
                energy_lat_lon_df_list = rocketUtils.preprocess_variables(
                    energy_lat_lon_df_list, rocketUtils.zscore
                )  # about 7 seconds

                # Pass the satellite data into the rocket model, the two probs
                # are "confidence-like" metrics for how sure the model is that
                # the provided data was generated by (0) a lightning or other
                # false event or (1) a bolide.
                y_hat_probs = rocket_pipeline.predict_proba(energy_lat_lon_df_list)

                # Store the metric for later analysis
                bolide_prob = y_hat_probs[0][1]  # Prob of bolide
                sat_cluster_metrics[sat_id_ind] = bolide_prob
                self.rocket_prob[str(cluster_id) + "_" + str(sat_id)] = bolide_prob

            # Combine the sat metrics into a cluster metric
            cluster_metric = np.array(max(sat_cluster_metrics))

            # Filter out clusters which fail a metric criteria
            if cluster_metric < settings.TRIGGER_PROB_THRESHOLD:
                cluster_ids[cluster_id_ind] = self.BAD_CLUSTER_ID

        cluster_ids = cluster_ids[cluster_ids != self.BAD_CLUSTER_ID]

        self.send_logs(
            [
                (
                    "debug",
                    f"{num_clusters_before_filter - len(cluster_ids)} clusters "
                    + f"filtered out by the rocket model ({len(cluster_ids)} remain).",
                )
            ]
        )

        return cluster_ids

    def get_event_position_ecef(self, cluster_id, in_cluster_bools):
        """get_event_position_ecef(self, cluster_id, in_cluster_bools)

        Return the estimated ECEF coordinates for the location of the
        bolide event if they exist. Otherwise, provide the peak intensity
        ECEF coordinates for an assumed altitude of 20 km.

        Args:
            self: class instance

            cluster_id (float): the cluster ID number

            in_cluster_bools (numpy array of booleans): A numpy array of
            booleans. True indicates data which belongs to the same
            cluster.

        Returns:
            (list of floats): the estimates ECEF coordinates (X, Y, Z)
            of the bolide event
        """
        if str(cluster_id) in self.location_ecef_m:
            location_ecef_xm = self.location_ecef_m[str(cluster_id)][0]
            location_ecef_ym = self.location_ecef_m[str(cluster_id)][1]
            location_ecef_zm = self.location_ecef_m[str(cluster_id)][2]
        else:
            # Find the indice of peak calibrated intensity
            max_pnt_ind = np.argmax(self.source_intensity_wpsr[in_cluster_bools])

            # Construct LOS vector for peak intensity
            sat_pos_ecef_m = self.sat_pos_ecef_m[in_cluster_bools][max_pnt_ind]
            high_pos_ecef_m = self.high_pos_ecef_m[in_cluster_bools][max_pnt_ind]

            # Compute where LOS vector intersects cloud top height
            location_ecef = ghf.find_pierce_point_at_alt(
                sat_pos_ecef_m.reshape(1, -1),
                high_pos_ecef_m.reshape(1, -1),
                DEFAULT_NONSTEREO_ALTITUDE_ESTIMATE_M,
            )[0]
            location_ecef_xm = location_ecef[0]
            location_ecef_ym = location_ecef[1]
            location_ecef_zm = location_ecef[2]

        return [location_ecef_xm, location_ecef_ym, location_ecef_zm]

    def get_total_radiated_energy(self, in_cluster_bools):
        """self.get_total_radiated_energy(in_cluster_bools)

        Computes a total radiated energy for the given cluster. Determined
        by the maximum energy amoung all of the viewing satellites.
        Source intensity Watts/steradian are converted into Joules by
        multiplying by 4 * pi (steradian) / 503 (seconds). See LPSC slides
        for more details.

        Args:
            in_cluster_bools (numpy array): A numpy array of booleans.
            True indicates data which belongs to the same cluster.

        Returns:
            (numpy array): A weighted average of the total radiated
            energy for the given cluster
        """

        sat_ids = np.unique(self.sat_id[in_cluster_bools])

        total_radiated_energy_by_sat = np.zeros(len(sat_ids))

        for sat_id_ind, sat_id in enumerate(sat_ids):
            in_cluster_sat_bools = in_cluster_bools & (self.sat_id == sat_id)

            source_intensities_wsr = self.source_intensity_wpsr[in_cluster_sat_bools]

            total_radiated_energy_by_sat[sat_id_ind] = (
                np.sum(source_intensities_wsr) * 4.0 * np.pi / 503.0
            )

        return np.max(total_radiated_energy_by_sat)

    def find_stereo_in_cluster_bools(self, cluster_id, debug_mode=False):
        """self.find_stereo_in_cluster_bools(cluster_id, debug_mode=False)

        Args:
            cluster_id (float): the cluster ID number
            debug_mode (bool, optional): Turn on additional output for
            troubleshooting the GLM trigger generator. Defaults to False.

        Returns:
            in_cluster_bools (list): A list of bools indicating which
            glm_data_set object indices qualify as being in the cluster.
        """
        # Index points with same cluster
        in_cluster_bools = self.cluster_id == cluster_id

        if np.all(~in_cluster_bools):
            return False

        # Get all stereo satellite IDs
        sat_ids_to_compare = self.get_stereo_pair(in_cluster_bools, debug_mode)

        # Skip cluster if no stereo satellites are found
        if len(sat_ids_to_compare) == 0:
            return False

        # Reduce in_cluster_bools to only have sat_ids_to_compare
        sat_ids_to_compare_bools = np.in1d(
            self.sat_id[in_cluster_bools], sat_ids_to_compare
        )
        in_cluster_bools[in_cluster_bools] = sat_ids_to_compare_bools

        # Use only the data which is above the ENERGY_PERCENT_FLOOR percentile of energy
        energy_j = self.energy_joules[in_cluster_bools]
        energy_percentile_threshold = np.max(energy_j) * (ENERGY_PERCENT_FLOOR / 100)
        higher_energy_bools = energy_j > energy_percentile_threshold
        in_cluster_bools[in_cluster_bools] = higher_energy_bools

        # Check that at least one point is included
        if np.all(~in_cluster_bools):
            return False

        # Omit points with only one GLM event (pixel)
        # (Points must be moving between pixels)
        group_ids = self.group_id[in_cluster_bools]

        group_cluster_large_enough_bools = []
        for group_id in group_ids:
            # Construct a vector of cluster sizes greater than 1 using the
            # group_ids that match the event_parent_group_ids
            group_cluster_large_enough_bools.append(
                np.sum(self.event_parent_group_id == group_id) > 1
            )
        in_cluster_bools[in_cluster_bools] = group_cluster_large_enough_bools

        # Further reduce point sources to be used for velocity estimates
        in_cluster_bools = (
            in_cluster_bools & (self.fitness == 1) & (self.highest_energy == 1)
        )

        return in_cluster_bools

    def get_stereo_los_data(self, in_cluster_bools):
        """self.get_stereo_los_data(in_cluster_bools)

        Args:
            in_cluster_bools (list): A list of bools indicating which
            glm_data_set object indices qualify as being in the cluster.

        Returns:
            tuple: (least_cluster_sat_data, most_cluster_sat_data, no_points_bool)
        """
        # Initialize the no_points_bool
        no_points_bool = False

        # Find the stereo event satellite with the least points
        (unique_sat_ids, unique_sat_counts) = np.unique(
            self.sat_id[in_cluster_bools],
            return_counts=True,
        )

        # Skip if cluster is no longer a stereo event
        if len(unique_sat_ids) <= 1:
            no_points_bool = True
            return (None, None, no_points_bool)

        # Label the Sat IDs with the least and most points
        sat_id_least = unique_sat_ids[np.argmin(unique_sat_counts)]
        sat_id_most = unique_sat_ids[unique_sat_ids != sat_id_least][0]

        # Index points with same cluster and satellite
        in_cluster_sat_least_bools = in_cluster_bools & (self.sat_id == sat_id_least)
        in_cluster_sat_most_bools = in_cluster_bools & (self.sat_id == sat_id_most)

        # Check if points exist for both stereo satellites
        if np.all(~in_cluster_sat_least_bools) or np.all(~in_cluster_sat_most_bools):
            no_points_bool = True
            return (None, None, no_points_bool)

        # Sort by time and subset energies and times belonging to same cluster and sat
        sorted_time_indices = np.argsort(self.time_s[in_cluster_sat_least_bools])
        # energies_cluster_sat_j = self.energy_joules[in_cluster_sat_id_bools]
        times_cluster_sat_least_s = self.time_s[in_cluster_sat_least_bools][
            sorted_time_indices
        ]
        high_pos_ecef_least_m = self.high_pos_ecef_m[in_cluster_sat_least_bools][
            sorted_time_indices
        ]
        low_pos_ecef_least_m = self.low_pos_ecef_m[in_cluster_sat_least_bools][
            sorted_time_indices
        ]

        sorted_time_indices = np.argsort(self.time_s[in_cluster_sat_most_bools])
        times_cluster_sat_most_s = self.time_s[in_cluster_sat_most_bools][
            sorted_time_indices
        ]
        high_pos_ecef_most_m = self.high_pos_ecef_m[in_cluster_sat_most_bools][
            sorted_time_indices
        ]
        low_pos_ecef_most_m = self.low_pos_ecef_m[in_cluster_sat_most_bools][
            sorted_time_indices
        ]

        least_cluster_sat_data = (
            times_cluster_sat_least_s,
            high_pos_ecef_least_m,
            low_pos_ecef_least_m,
        )
        most_cluster_sat_data = (
            times_cluster_sat_most_s,
            high_pos_ecef_most_m,
            low_pos_ecef_most_m,
        )

        return (least_cluster_sat_data, most_cluster_sat_data, no_points_bool)

    def estimate_velocities(
        self, cluster_ids, data_dir, debug_mode=False, save_pairs_plots=False
    ):
        """estimate_velocities(self, cluster_ids, debug_mode=False, save_pairs_plots=False)

        For stereo clusters, computes the estimated velocity of the event.

        INPUTS:
            self - class instance

            cluster_ids (numpy array): An array of the triggering cluster IDs

            data_dir (string): A directory for where to store the plots

            debug_mode (bool, optional): Turn on additional output for
            troubleshooting the GLM trigger generator. Defaults to False.

            save_pairs_plots (bool, optional): Save a pairs plot. Defaults to False.

        OUTPUTS:
            There are no explicit outputs. The velocity class members
            will be updated for each stereo event.
        """
        debug_print("\nStart estimate_velocities()", debug_mode)

        for cluster_id in cluster_ids:
            debug_print(f"\nCluster ID: {cluster_id}", debug_mode)
            # Skip the bad cluster IDs
            if cluster_id == self.BAD_CLUSTER_ID:
                continue

            # Find the stereo cluster point source bools
            in_cluster_bools = self.find_stereo_in_cluster_bools(cluster_id)

            # Check that at least one point is included
            if np.all(~in_cluster_bools):
                debug_print(
                    "\nToo few good LOSs to construct a velocity estimate.", debug_mode
                )
                continue

            # Get stereo event satellite LOS data
            (least_cluster_sat_data, most_cluster_sat_data, no_points_bool) = (
                self.get_stereo_los_data(in_cluster_bools)
            )

            # Check that at least one point is included
            if no_points_bool:
                debug_print(
                    "\nToo few LOSs to construct a velocity estimate.", debug_mode
                )
                continue

            # Associate LOS vectors which are near in time to each other
            time_los_vectors = vhf.associate_los_vectors(
                least_cluster_sat_data, most_cluster_sat_data
            )

            # Check if enough LOS vectors exist for both stereo satellites
            # Must have at least len(beta_vec) since the linear model needs at least len(beta_vec)
            if len(time_los_vectors) < MIN_NUM_POINTS_FOR_VEL_ESTIMATE:
                debug_print(
                    f"\nToo few points to construct a velocity estimate. "
                    f"Found {len(time_los_vectors)}, but need "
                    f"{MIN_NUM_POINTS_FOR_VEL_ESTIMATE}.",
                    debug_mode,
                )
                continue

            # Compute the points of nearest approach across all of the associated LOS vectors
            (
                intersection_points,
                estimated_lats,
                estimated_lons,
                estimated_alts,
                intersection_times,
            ) = vhf.compute_nearest_approach_points(time_los_vectors)

            if save_pairs_plots:
                plot_pairs(
                    cluster_id,
                    estimated_lats,
                    estimated_lons,
                    estimated_alts,
                    intersection_times,
                    data_dir,
                )

            # Set the initial time to be equal to zero
            intersection_times = intersection_times - np.min(intersection_times)

            # Estimate the velocity vector
            velocity_estimate_mps = vhf.estimate_velocity(
                intersection_times, intersection_points
            )

            # Check that the speed is reasonable (should be around 11-12 kmps)
            speed_estimate_kmps = np.linalg.norm(velocity_estimate_mps, ord=2) / 1000
            if speed_estimate_kmps > MAX_SPEED_THRESHOLD_KMPS:
                debug_print(
                    "\nEstimate speed too large. Discarding velocity estimate.",
                    debug_mode,
                )
                continue

            # Store the velocity within the glm_data_set object
            self.velocities[str(cluster_id)] = velocity_estimate_mps

        debug_print("\nEnd estimate_velocities()", debug_mode)

        return
        # end of estimate_velocities()

    def get_event_velocity(self, cluster_id):
        """get_event_velocity(self, cluster_id)

        Return the estimated velocity vector at peak intensity of the
        bolide event if it exists. Otherwise, return a zero vector.

        Args:
            self: class instance

            cluster_id (float): the cluster ID number

        Returns:
            (list of floats): the estimated velocity components (X, Y, Z)
            of the bolide event at peak intensity
        """
        if str(cluster_id) in self.velocities:
            velocity_ecef_x_mps = self.velocities[str(cluster_id)][0]
            velocity_ecef_y_mps = self.velocities[str(cluster_id)][1]
            velocity_ecef_z_mps = self.velocities[str(cluster_id)][2]
        else:
            velocity_ecef_x_mps = 0.0
            velocity_ecef_y_mps = 0.0
            velocity_ecef_z_mps = 0.0

        return [velocity_ecef_x_mps, velocity_ecef_y_mps, velocity_ecef_z_mps]

    def publish_cluster_over_zmq(self, socket, topic, cluster_ids, event_ids):
        """publish_cluster_over_zmq(self, socket, topic, cluster_ids, event_ids)

        Publish a message for each triggering satellite within each cluster'
        (across all cluster_ids) over the ZMQ socket and topic provided

        INPUTS:
            self - class instance

            socket - ZMQ publish socket that has been already setup

            topic - topic with which to publish the data

            cluster_ids - cluster ids whose data should be published

            event_ids - UUIDs assigned to the events (clusters) by the database

        OUTPUTS:
            There are no return outputs. The specified data will be published
            over the ZMQ socket.
        """
        # make sure we have some clusters
        if cluster_ids.size == 0:
            warnings.warn("No cluster ids were provided.  Publish function aborting.")
            return

        for cluster_id in cluster_ids:
            glm_proto = glm_pb2.EventMsg()
            msg_track_proto = msg_track_pb2.MsgTrack()
            peak_time = 0

            in_cluster_bools = self.cluster_id == cluster_id
            sat_ids = np.unique(self.sat_id[in_cluster_bools])
            for sat_id in sat_ids:
                # find the data in the cluster (get the actual indices)
                ind = np.array(range(self.cluster_id.size))[
                    (in_cluster_bools) & (self.sat_id == sat_id)
                ]

                # Save satellite level point measurement data to protobuf
                new_glm_meas = glm_proto.glm_data.meas.add()

                # Add all the event information
                max_pnt = np.argmax(self.source_intensity_wpsr[ind])
                max_pnt_time = self.basetime_ssue + self.time_s[ind][max_pnt]
                new_glm_meas.time_ssue = max_pnt_time
                if max_pnt_time > peak_time:
                    peak_time = max_pnt_time
                new_glm_meas.intensity_kwsr = (
                    self.source_intensity_wpsr[ind][max_pnt] / 1000
                )
                new_glm_meas.id = self.group_id[ind][max_pnt]
                # @TODO: Add size of groups provided in GLM data here
                new_glm_meas.cluster_size = 0
                new_glm_meas.sat_id = int(self.sat_id[ind][max_pnt])
                new_glm_meas.sat_pos_ecf_m.x = self.sat_pos_ecef_m[ind][max_pnt, 0]
                new_glm_meas.sat_pos_ecf_m.y = self.sat_pos_ecef_m[ind][max_pnt, 1]
                new_glm_meas.sat_pos_ecf_m.z = self.sat_pos_ecef_m[ind][max_pnt, 2]

                new_glm_meas.los_near_point_ecf_m.x = self.high_pos_ecef_m[ind][
                    max_pnt, 0
                ]
                new_glm_meas.los_near_point_ecf_m.y = self.high_pos_ecef_m[ind][
                    max_pnt, 1
                ]
                new_glm_meas.los_near_point_ecf_m.z = self.high_pos_ecef_m[ind][
                    max_pnt, 2
                ]
                new_glm_meas.los_far_point_ecf_m.x = self.low_pos_ecef_m[ind][
                    max_pnt, 0
                ]
                new_glm_meas.los_far_point_ecf_m.y = self.low_pos_ecef_m[ind][
                    max_pnt, 1
                ]
                new_glm_meas.los_far_point_ecf_m.z = self.low_pos_ecef_m[ind][
                    max_pnt, 2
                ]

            event_id = event_ids[np.where(cluster_ids == cluster_id)[0][0]]
            glm_proto.event_id = event_id
            time_string = dth.convert_ssue_to_string(peak_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            glm_proto.approx_trigger_time_iso_utc = time_string
            glm_proto.trigger_type = "GLM"
            glm_proto.processing_state = glm_proto.ProcessingState.NEW
            glm_proto.params.peak_brightness_time_iso_utc = time_string
            [
                glm_proto.params.peak_brightness_pos_ecf_m.x,
                glm_proto.params.peak_brightness_pos_ecf_m.y,
                glm_proto.params.peak_brightness_pos_ecf_m.z,
            ] = self.get_event_position_ecef(
                cluster_id=cluster_id, in_cluster_bools=in_cluster_bools
            )
            glm_proto.params.approx_total_radiated_energy = (
                self.get_total_radiated_energy(in_cluster_bools)
            )
            [
                glm_proto.params.peak_brightness_velocity_km_sec.x,
                glm_proto.params.peak_brightness_velocity_km_sec.y,
                glm_proto.params.peak_brightness_velocity_km_sec.z,
            ] = self.get_event_velocity(cluster_id)

            msg_track_proto.original_uuid = event_id
            msg_track_proto.uuid = event_id

            # export protobuf to json and publish the message
            json_proto = MessageToJson(glm_proto)
            socket.send_string(f"{topic}{json_proto}")

            # Email trigger info
            if settings.SMTP_SEND:
                smtp.email_trigger_info(self, peak_time, sat_ids)

        # end of publish_cluster_over_zmq

    def get_cluster_group_event_data(self, cluster_id):
        """get_cluster_group_event_data(self, cluster_id)

        INPUTS:
            cluster_id (int): a cluster ID assigned to data members by the
            cluster_glm_data method

        OUTPUTS:
            approx_trigger_time (float) - the approximate time of first max
            energy peak value

            location_ecef_m (list) - a list of estimated x, y, and z ecef
            coordinates of location of the event

            velocity_ecef_m () - a list of estimated x, y, and z ecef velocity
            vector components of the event

            approx_energy_j (float) - an estimated total energy of the event

            group_point_sources_dict (dict) - the group point source data for the event

            event_point_sources_dict (dict) - the event point source data for the event
        """
        # find the data in the cluster
        in_cluster_bools = self.cluster_id == cluster_id

        if sum(in_cluster_bools) == 0:
            warnings.warn("sum(in_cluster_bools) is zero!")
            return None

        # Gather cluster information
        max_pnt = np.argmax(self.energy_joules[in_cluster_bools])
        approx_trigger_time = (
            self.basetime_ssue + self.time_s[in_cluster_bools][max_pnt]
        )

        # Use the location estimate if one already exists for the
        # cluster. Otherwise, estimate the location using a mean midpoint
        location_ecef_m = self.get_event_position_ecef(cluster_id, in_cluster_bools)

        velocity_ecef_m = self.get_event_velocity(cluster_id)

        approx_energy_j = self.get_total_radiated_energy(in_cluster_bools)

        # Group and Event Point Sources
        ind = np.array(range(self.cluster_id.size))[in_cluster_bools]
        group_point_sources_dict = {}
        event_point_sources_dict = {}
        for ii in ind:
            sat_id = int(self.sat_id[ii])
            if sat_id not in group_point_sources_dict:
                group_point_sources_dict[sat_id] = []

            # Prep work for collecting all of the event level data
            group_id = self.group_id[ii]
            keep_event_bool = self.event_parent_group_id == group_id

            # Collect all of the group level data
            time = self.basetime_ssue + self.time_s[ii]
            intensity_kwpsr = float(self.source_intensity_wpsr[ii]) / 1000
            group_cluster_size = int(np.sum(keep_event_bool))
            cluster_sat_pos_ecef_m = self.sat_pos_ecef_m[ii]
            sat_ecef_x_m = cluster_sat_pos_ecef_m[0]
            sat_ecef_y_m = cluster_sat_pos_ecef_m[1]
            sat_ecef_z_m = cluster_sat_pos_ecef_m[2]
            sat_pos_ecef_m_str = f"{{{sat_ecef_x_m}, {sat_ecef_y_m}, {sat_ecef_z_m}}}"
            near_ecef_x_m = self.high_pos_ecef_m[ii, 0]
            near_ecef_y_m = self.high_pos_ecef_m[ii, 1]
            near_ecef_z_m = self.high_pos_ecef_m[ii, 2]
            near_ecef_m_str = f"{{{near_ecef_x_m}, {near_ecef_y_m}, {near_ecef_z_m}}}"
            far_ecef_x_m = self.low_pos_ecef_m[ii, 0]
            far_ecef_y_m = self.low_pos_ecef_m[ii, 1]
            far_ecef_z_m = self.low_pos_ecef_m[ii, 2]
            far_ecef_m_str = f"{{{far_ecef_x_m}, {far_ecef_y_m}, {far_ecef_z_m}}}"
            group_point_sources_dict[sat_id].append(
                (
                    time,
                    intensity_kwpsr,
                    group_cluster_size,
                    sat_pos_ecef_m_str,
                    near_ecef_m_str,
                    far_ecef_m_str,
                )
            )

            # Collect all of the event level data
            if sat_id not in event_point_sources_dict:
                event_point_sources_dict[sat_id] = []

            event_times_s = self.basetime_ssue + self.event_time[keep_event_bool]
            event_lats_deg = self.event_lat[keep_event_bool]
            event_lons_deg = self.event_lon[keep_event_bool]
            event_intensities_kwpsr = self.event_intensity_wsr[keep_event_bool] / 1000
            event_cluster_size = 1  # Since event data are single pixels

            # Ensure longitudinals are within -180 to 180
            event_lons_deg = ghf.wrap_longitudes(event_lons_deg, 180)

            ## Assuming the event occurred at cloud-top-height, convert
            ## lat and lon to Ecef
            event_lat_lon_deg = np.column_stack((event_lats_deg, event_lons_deg))
            event_cloud_top_pos_ecefs_m = ghf.adjusted_lat_lon_to_ecef(
                event_lat_lon_deg,
                self.CLOUD_TOP_EQUATOR_M,
                self.CLOUD_TOP_POLE_M,
            )

            for event_ind, event_intensity_kwpsr in enumerate(event_intensities_kwpsr):
                event_high_pos_ecef_m = ghf.find_pierce_point_at_alt(
                    cluster_sat_pos_ecef_m.reshape(1, -1),
                    event_cloud_top_pos_ecefs_m[event_ind].reshape(1, -1),
                    self.HIGH_ALTITUDE_M,
                )[0]
                event_low_pos_ecef_m = ghf.find_pierce_point_at_alt(
                    cluster_sat_pos_ecef_m.reshape(1, -1),
                    event_cloud_top_pos_ecefs_m[event_ind].reshape(1, -1),
                    self.LOW_ALTITUDE_M,
                )[0]
                near_ecef_m_str = (
                    f"{{{event_high_pos_ecef_m[0]}, "
                    f"{event_high_pos_ecef_m[1]}, "
                    f"{event_high_pos_ecef_m[2]}}}"
                )
                far_ecef_m_str = (
                    f"{{{event_low_pos_ecef_m[0]}, "
                    f"{event_low_pos_ecef_m[1]}, "
                    f"{event_low_pos_ecef_m[2]}}}"
                )

                # Subset event data
                event_point_sources_dict[sat_id].append(
                    (
                        event_times_s[event_ind],
                        event_intensity_kwpsr,
                        event_cluster_size,
                        sat_pos_ecef_m_str,
                        near_ecef_m_str,
                        far_ecef_m_str,
                    )
                )

        return (
            approx_trigger_time,
            location_ecef_m,
            velocity_ecef_m,
            approx_energy_j,
            group_point_sources_dict,
            event_point_sources_dict,
        )
