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

import numpy as np

import src.helper_funs.geo_helpers as ghf

# A window in seconds for which stereo point sources are associated with each other
POINT_SOURCE_ASSOCIATION_TIME_WINDOW_S = 0.02


def associate_los_vectors(least_cluster_sat_data, most_cluster_sat_data):
    """associate_los_vectors(least_cluster_sat_data, most_cluster_sat_data)

    For every LOS in the least_cluster_sat_data, find the LOS (if it exists)
    in the most_cluster_sat_data which occurs nearest in time (within a
    window of width POINT_SOURCE_ASSOCIATION_TIME_WINDOW_S seconds).

    Args:
        least_cluster_sat_data (tuple): A tuple of LOS times, high alt
        points, and low alt points for the satellite with the least LOSs
        in the cluster
        most_cluster_sat_data (tuple): A tuple of LOS times, high alt
        points, and low alt points for the satellite with the most LOSs
        in the cluster

    Returns:
        list: A list of associated times and LOS vectors
    """
    # Extract the LOS data
    (times_cluster_sat_least_s, high_pos_ecef_least_m, low_pos_ecef_least_m) = (
        least_cluster_sat_data
    )

    (times_cluster_sat_most_s, high_pos_ecef_most_m, low_pos_ecef_most_m) = (
        most_cluster_sat_data
    )

    # Initialize the time_los_vectors list
    time_los_vectors = []

    # For every point in the sat with least points, look for associated points with other sat
    for least_time_index, least_time_s in enumerate(times_cluster_sat_least_s):
        # Subset all of the sat with most points within a window around the least_time_s
        time_diffs_s = np.abs(times_cluster_sat_most_s - least_time_s)

        if (
            np.min(time_diffs_s) < POINT_SOURCE_ASSOCIATION_TIME_WINDOW_S
        ):  # There is at least one point within the time window
            # Hence, initialize a time_los_vector
            time_los_vector = [None] * 6

            # Add least-sat time and los points to time_los_vector
            time_los_vector[0] = least_time_s
            time_los_vector[1] = high_pos_ecef_least_m[least_time_index]
            time_los_vector[2] = low_pos_ecef_least_m[least_time_index]

            # Add most-sat time and los points to time_los_vector
            most_time_index = np.argmin(time_diffs_s)

            time_los_vector[3] = times_cluster_sat_most_s[most_time_index]
            time_los_vector[4] = high_pos_ecef_most_m[most_time_index]
            time_los_vector[5] = low_pos_ecef_most_m[most_time_index]

            # Add time_los_vector to time_los_vectors list
            time_los_vectors.append(time_los_vector)

    return time_los_vectors


def compute_nearest_approach_points(time_los_vectors):
    """compute_nearest_approach_points(time_los_vectors)

    Args:
        time_los_vectors (list): A list of associated times and LOS vectors

    Returns:
        tuple: A tuple of lists of nearest approach point data
    """

    closest_distances = [None] * len(time_los_vectors)
    nearest_approach_points = [None] * len(time_los_vectors)
    nearest_approach_times = [None] * len(time_los_vectors)
    estimated_lats = [None] * len(time_los_vectors)
    estimated_lons = [None] * len(time_los_vectors)
    estimated_alts = [None] * len(time_los_vectors)

    # For all of the associated LOSs, compute points of nearest intersections
    for time_los_index, time_los_vector in enumerate(time_los_vectors):

        # Extract LOS high and low points
        high_pos_ecef0m = time_los_vector[1]
        low_pos_ecef0m = time_los_vector[2]
        high_pos_ecef1m = time_los_vector[4]
        low_pos_ecef1m = time_los_vector[5]

        # Compute the min distance vector between two lines-of-sight
        [closest_distance, seg0p_min, seg1p_min] = ghf.dist3d_segment_to_segment(
            high_pos_ecef0m,
            low_pos_ecef0m,
            high_pos_ecef1m,
            low_pos_ecef1m,
        )

        closest_distances[time_los_index] = closest_distance

        # Find the middle point of the min distance vector
        min_dist_seg_ecef_ave = np.mean(np.stack([seg0p_min, seg1p_min]), axis=0)

        # Store the estimated location
        nearest_approach_points[time_los_index] = min_dist_seg_ecef_ave

        # Compute intersection times
        nearest_approach_times[time_los_index] = np.mean(
            [time_los_vector[0], time_los_vector[3]]
        )

        # Convert the middle point to Geodetic to estimate altitude
        (estimated_lat, estimated_lon, estimated_alt) = ghf.ecef2geodetic(
            min_dist_seg_ecef_ave[0],
            min_dist_seg_ecef_ave[1],
            min_dist_seg_ecef_ave[2],
        )

        estimated_lats[time_los_index] = estimated_lat
        estimated_lons[time_los_index] = estimated_lon
        estimated_alts[time_los_index] = estimated_alt

    return (
        nearest_approach_points,
        estimated_lats,
        estimated_lons,
        estimated_alts,
        nearest_approach_times,
    )


def estimate_velocity(nearest_approach_times, nearest_approach_points):
    """estimate_velocity(nearest_approach_times, nearest_approach_points)

    Construct a parametric linear model assuming a constant velocity, i.e.,
    x(t) = x_0 + v_x * t
    y(t) = y_0 + v_y * t
    z(t) = z_0 + v_z * t

    The parameters needed to be solved for form the beta vectors, e.g.,
    beta_x_vec = [x_0, v_x], etc. These beta vectors can be solved for
    using a linear least squares solution, e.g., beta_x_vec = (T'T)^-1T'X,
    where T is a nx2 matrix of 1's and intersection point times, T' is the
    transpose of T, and X is the vector of intersection point x coordinates
    at the associated times. This solution is performed three times, one
    for each of the x, y, and z nearest-approach point coordinates.

    Args:
        nearest_approach_times (list): A list of times in seconds
        nearest_approach_points (array): An array of ECEF points in meters

    Returns:
        List: Containing the velocity vector estimates in meters per second
    """
    # Extract the ECEF point coordinates
    nearest_approach_points_mat = np.vstack(nearest_approach_points)
    x_m = nearest_approach_points_mat[:, 0]
    y_m = nearest_approach_points_mat[:, 1]
    z_m = nearest_approach_points_mat[:, 2]

    # Construct a parametric linear model assuming a constant velocity
    t_mat_trans = np.vstack(
        [
            np.ones(len(nearest_approach_times)),
            nearest_approach_times,
        ]
    )
    t_mat = t_mat_trans.transpose()

    # Compute the linear least squares solutions for each coordinate
    t_mats_mat = np.linalg.inv(t_mat_trans @ t_mat) @ t_mat_trans
    beta_x_vec = t_mats_mat @ x_m
    beta_y_vec = t_mats_mat @ y_m
    beta_z_vec = t_mats_mat @ z_m

    # Extract the velocity estimates for each coordinate direction
    vel_x = beta_x_vec[1]
    vel_y = beta_y_vec[1]
    vel_z = beta_z_vec[1]

    return [vel_x, vel_y, vel_z]
