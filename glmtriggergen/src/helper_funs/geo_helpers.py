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

# GRS80 parameters (Semimajor and Semiminor axes)
GRS80_PARAMS = [6378137, 6356752.31414]
# GRS80 parameters
GRS80_SEMIMAJOR_AXIS_M = GRS80_PARAMS[0]
GRS80_SEMIMINOR_AXIS_M = GRS80_PARAMS[1]

EPSILON = 1e-8  # For checking if differences are approximately zero


def adjusted_lat_lon_to_ecef(lat_lon_array, eq_adj=0.0, pole_adj=0.0):
    """adjusted_lat_lon_to_ecef(lat_lon_array, eq_adj=0.0, pole_adj=0.0)

    Convert geodetic coordinates (lat/lon in decimal degrees) to
    earth-centered-earth-fixed (ecef) coordinates (in meters).

    Uses the GRS80 ellipsoid as the base earth model.

    See: http://en.wikipedia.org/wiki/Geodetic_datum

    Args:
        lat_lon_array (array): latitude and longitude in degrees. Can also include
        height (in meters) in the array (i.e. NX2 or Nx3 array)
        eq_adj (float, optional): GRS80 semimajor axes adjustment (can be used
        to renavigate data at a different height) in meters. Defaults to 0.0.
        pole_adj (float, optional): GRS80 semiminor axes adjustment (can be used
        to renavigate data at a different height) in meters. Defaults to 0.0.

    Returns:
        array: ecef coordinates as number of points x 3
        (earth-centered-earth-fixed xyz in meters)
    """
    # Get inflated semi-major and semi-minor axes
    infl_major_axis_m = GRS80_SEMIMAJOR_AXIS_M + eq_adj
    infl_minor_axis_m = GRS80_SEMIMINOR_AXIS_M + pole_adj

    # Compute flattening and square of eccentricity
    flattening = (infl_major_axis_m - infl_minor_axis_m) / infl_major_axis_m
    e2 = 2 * flattening - flattening**2

    # Convert decimal degrees to radians
    if len(lat_lon_array.shape) == 1:
        lat = np.radians(lat_lon_array[0])
        lon = np.radians(lat_lon_array[1])
        height = 0
        if lat_lon_array.shape[-1] == 3:
            height = lat_lon_array[2]
    else:
        lat = np.radians(lat_lon_array[:, 0])
        lon = np.radians(lat_lon_array[:, 1])
        height = np.zeros(lat.shape)
        if lat_lon_array.shape[-1] == 3:
            height = lat_lon_array[:, 2]

    # Compute the normal, or distance from the surface to the z-axis along the
    # ellipsoid normal, for each point
    norm_dist = infl_major_axis_m / np.sqrt(1 - e2 * (np.sin(lat)) ** 2)

    # Compute ecef coordinates
    return np.vstack(
        [
            (norm_dist + height) * np.cos(lat) * np.cos(lon),
            (norm_dist + height) * np.cos(lat) * np.sin(lon),
            (norm_dist * (1 - e2) + height) * np.sin(lat),
        ]
    ).transpose()


def ecef2geodetic(x, y, z):
    """lat, lon, alt = ecef2geodetic(x, y, z)

    Convert earth-centered-earth-fixed (ecef) coordinates (in meters) to
    geodetic coordinates (lat/lon in decimal degrees).

    Uses the GRS80 ellipsoid as the base earth model

    See: http://en.wikipedia.org/wiki/Geodetic_datum

    Args:
        x (float): earth-centered-earth-fixed x coordinate in meters
        y (float): earth-centered-earth-fixed y coordinate in meters
        z (float): earth-centered-earth-fixed z coordinate in meters

    Returns:
        floats: lat, lon, alt are the latitude and longitude in degrees, and height (in meters)
    """
    e12 = (
        GRS80_SEMIMAJOR_AXIS_M**2 - GRS80_SEMIMINOR_AXIS_M**2
    ) / GRS80_SEMIMAJOR_AXIS_M**2  # first eccentricity (squared)
    e22 = (
        GRS80_SEMIMAJOR_AXIS_M**2 - GRS80_SEMIMINOR_AXIS_M**2
    ) / GRS80_SEMIMINOR_AXIS_M**2  # second eccentricity (squared)

    # longitude
    lon = np.arctan2(y, x)

    # distance from the polar axis to the point (squared)
    p2 = x**2 + y**2

    # latitude using Bowring's iterative method

    # initial value of beta
    beta = np.arctan2(z * GRS80_SEMIMAJOR_AXIS_M, np.sqrt(p2) * GRS80_SEMIMINOR_AXIS_M)

    # iterate 3 times
    for _ in range(3):

        # numerator and denominator to estimate latitude
        n = z + GRS80_SEMIMINOR_AXIS_M * e22 * (np.sin(beta)) ** 3
        d = np.sqrt(p2) - GRS80_SEMIMAJOR_AXIS_M * e12 * (np.cos(beta)) ** 3

        # latitude estimate
        lat = np.arctan2(n, d)

        # update beta estimate
        beta = np.arctan2(
            GRS80_SEMIMINOR_AXIS_M * np.sin(lat), GRS80_SEMIMAJOR_AXIS_M * np.cos(lat)
        )

    # height
    norm_dist = GRS80_SEMIMAJOR_AXIS_M / np.sqrt(1 - e12 * (np.sin(lat)) ** 2)
    alt = (np.sqrt(p2) / np.cos(lat)) - norm_dist

    # convert lat long to decimal degrees
    lat = lat * 180 / np.pi
    lon = lon * 180 / np.pi
    return lat, lon, alt


def find_pierce_point_at_alt(sat_pos_ecef_m, look_point_ecef_m, desired_alt_m):
    """pierce_point_ecef_m = find_pierce_point_at_alt(sat_pos_ecef_m, look_point_ecef_m, desired_alt_m)

    Find the pierce point of a line-of-sight based on a satellite position and
    look direction.

    This uses the GRS80 ellipsoid as the base earth model.

    See: http://en.wikipedia.org/wiki/Geodetic_datum

    Args:
        sat_pos_ecef_m (array): Nx3 vector of satellite positions (same size as
        look points)
        look_point_ecef_m (array): Nx3 vector of the point at which the
        satellite is looking (could be a unit vector but does not have to be)
        desired_alt_m (float): altitude in meters at which to find the pierce point

    Returns:
        array: The ECEF position where the line-of-sight pierces the desired
        altitude above the Earth's surface. If no intersection is made, returns
        0's for that point.
    """
    # make sure the shape of the inputs match
    if sat_pos_ecef_m.shape != look_point_ecef_m.shape:
        raise ValueError("sat_pos and lookPoint must have the same length")

    # Get inflated semi-major and semi-minor axes
    infl_major_axis_m = GRS80_SEMIMAJOR_AXIS_M + desired_alt_m
    infl_minor_axis_m = GRS80_SEMIMINOR_AXIS_M + desired_alt_m
    a2overb2 = infl_major_axis_m**2 / infl_minor_axis_m**2

    # create a direction vector
    dir_vec = look_point_ecef_m - sat_pos_ecef_m
    dir_vec_norm = dir_vec / (
        np.tile(np.linalg.norm(dir_vec, axis=1), [3, 1]).transpose()
    )

    # calculate pierce point for all vectors
    a1 = (
        dir_vec_norm[:, 0] ** 2
        + dir_vec_norm[:, 1] ** 2
        + a2overb2 * dir_vec_norm[:, 2] ** 2
    )
    a2 = 2 * (
        sat_pos_ecef_m[:, 0] * dir_vec_norm[:, 0]
        + sat_pos_ecef_m[:, 1] * dir_vec_norm[:, 1]
        + a2overb2 * sat_pos_ecef_m[:, 2] * dir_vec_norm[:, 2]
    )
    a3 = (
        sat_pos_ecef_m[:, 0] ** 2
        + sat_pos_ecef_m[:, 1] ** 2
        + a2overb2 * sat_pos_ecef_m[:, 2] ** 2
        - infl_major_axis_m**2
    )
    a4 = a2**2 - 4 * a1 * a3
    t2 = (-a2 - np.sqrt(a4)) / (2 * a1)

    # find valid pierce points and record the location
    pierce_point_ecef_m = np.zeros(dir_vec.shape)
    ind = np.any([a4 >= 0, a1 != 0, t2 > 0], axis=0)
    if any(ind):
        pierce_point_ecef_m[ind, :] = np.array(
            [
                sat_pos_ecef_m[ind, 0] + t2[ind] * dir_vec_norm[ind, 0],
                sat_pos_ecef_m[ind, 1] + t2[ind] * dir_vec_norm[ind, 1],
                sat_pos_ecef_m[ind, 2] + t2[ind] * dir_vec_norm[ind, 2],
            ]
        ).transpose()

    return pierce_point_ecef_m


def dist3d_segment_to_segment(seg1p0, seg1p1, seg2p0, seg2p1):
    """[closest_distance_m, seg1p, seg2p] = dist3d_segment_to_segment(seg1p0, seg1p1, seg2p0, seg2p1)

    Compute the closest distance between two finite 3D line segments

    see http://geomalgorithms.com/a07-_distance.html#dist3d_segment_to_segment()

    Args:
        seg1p0 (array): start point of segment 1 (1x3)
        seg1p1 (array): end point of segment 1 (1x3)
        seg2p0 (array): start point of segment 2 (1x3)
        seg2p1 (array): end point of segment 2 (1x3)

    Returns:
        list: A list including the closest distance in meters, along with
        the points along the two segments where the closest distance occurs.
    """
    # Optimized for computational efficiency
    # u = np.diff(seg1,axis=0)[0] # S1.P1 - S1.P0
    # v = np.diff(seg2,axis=0)[0] # S2.P1 - S2.P0
    # w = seg1[0]-seg2[0] # S1.P0 - S2.P0
    # a = np.dot(u,u) # always >= 0
    # b = np.dot(u,v)
    # c = np.dot(v,v) # always >= 0
    # d = np.dot(u,w)
    # e = np.dot(v,w)
    u = np.array([seg1p1[0] - seg1p0[0], seg1p1[1] - seg1p0[1], seg1p1[2] - seg1p0[2]])
    v = np.array([seg2p1[0] - seg2p0[0], seg2p1[1] - seg2p0[1], seg2p1[2] - seg2p0[2]])
    w = seg1p0 - seg2p0
    a = u[0] ** 2 + u[1] ** 2 + u[2] ** 2
    b = u[0] * v[0] + u[1] * v[1] + u[2] * v[2]
    c = v[0] ** 2 + v[1] ** 2 + v[2] ** 2
    d = u[0] * w[0] + u[1] * w[1] + u[2] * w[2]
    e = v[0] * w[0] + v[1] * w[1] + v[2] * w[2]
    dd = a * c - b * b  # always >= 0
    # sc = s_n / s_d, default s_d = dd >= 0
    s_d = dd
    # tc = t_n / t_d, default t_d = dd >= 0
    t_d = dd

    # compute the line parameters of the two closest points
    if dd < EPSILON:  # the lines are almost parallel
        s_n = 0.0  # force using point P0 on segment S1
        s_d = 1.0  # to prevent possible division by 0.0 later
        t_n = e
        t_d = c
    else:  # get the closest points on the infinite lines
        s_n = b * e - c * d
        t_n = a * e - b * d
        if s_n < 0.0:  # sc < 0 => the s=0 edge is visible
            s_n = 0.0
            t_n = e
            t_d = c
        elif s_n > s_d:  # sc > 1  => the s=1 edge is visible
            s_n = s_d
            t_n = e + b
            t_d = c

    if t_n < 0.0:  # tc < 0 => the t=0 edge is visible
        t_n = 0.0
        # recompute sc for this edge
        if -d < 0.0:
            s_n = 0.0
        elif -d > a:
            s_n = s_d
        else:
            s_n = -d
            s_d = a
    elif t_n > t_d:  # tc > 1  => the t=1 edge is visible
        t_n = t_d
        # recompute sc for this edge
        if (-d + b) < 0.0:
            s_n = 0
        elif (-d + b) > a:
            s_n = s_d
        else:
            s_n = -d + b
            s_d = a

    # finally do the division to get sc and tc
    if abs(s_n) < EPSILON:  # sc = (abs(s_n) < EPSILON ? 0.0 : s_n / s_d)
        sc = 0.0
    else:
        sc = s_n / s_d
    if abs(t_n) < EPSILON:  # tc = (abs(t_n) < EPSILON ? 0.0 : t_n / t_d);
        tc = 0.0
    else:
        tc = t_n / t_d

    # get the difference of the two closest points
    d_p = w + (sc * u) - (tc * v)  # =  S1(sc) - S2(tc)

    # calculate the return parameters
    # closest_distance_m = np.linalg.norm(d_p) # optimized out for speed
    closest_distance_m = np.sqrt(d_p[0] ** 2 + d_p[1] ** 2 + d_p[2] ** 2)
    seg1p = seg1p0 + sc * u
    seg2p = seg2p0 + tc * v
    return [closest_distance_m, seg1p, seg2p]


def wrap_longitudes(lon_array, upper_discontinuity):
    """wrap_longitudes(lon_array, upper_discontinuity)

    Ensures that longitudinal angles are within (upper_discontinuity -
    360) to upper_discontinuity degrees.

    Args:
        lon_array (numpy array): An array of longitudinals not
        necessarily within (upper_discontinuity - 360) to
        upper_discontinuity
        upper_discontinuity (float): the maximum value within the window
        with which to wrap the longitudes within

    Returns:
        (numpy array): An array of longitudinals each within
        (upper_discontinuity - 360) to upper_discontinuity
    """
    lower_discontinuity = upper_discontinuity - 360
    return ((lon_array + upper_discontinuity) % 360) + lower_discontinuity
