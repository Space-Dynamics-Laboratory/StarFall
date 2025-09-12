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


def comb(n, k):
    """comb(n, k)

    Compute the number of ways to choose $k$ elements out of a total of
    $n$ elements, where elements cannot be chosen more than once and the
    order in which elements are chosen does not matter.

    This function uses an iterative approach with the multiplicative
    formula:
    $$\\frac{n!}{k!(n - k)!} =
    \\frac{n(n - 1)\\dots(n - k + 1)}{k(k-1)\\dots(1)} =
    \\prod_{i = 1}^{k}\\frac{n + 1 - i}{i}$$

    Also leverage the symmetry: $C_n^k = C_n^{n - k},$ so the product
    can be calculated up to $\\min(k, n - k).$

    Args:
        n (int): the total number of elements to choose from
        k (int): the number of elements chosen

    Returns:
        (int): the number of ways to choose $k$ elements out of a total
        of $n$ elements
    """
    # When k is less than zero or more than n, return zero.
    if k < 0 or k > n:
        return 0

    if k in (0, n):
        return 1

    num_combinations = 1
    for i in range(min(k, n - k)):
        num_combinations = num_combinations * (n - i) // (i + 1)

    return num_combinations


def energy_filter(energy_array, first_pnt, last_pnt, filter_width, max_valid_drop=5):
    """fitness = energy_filter(energy_array, first_pnt, last_pnt, filter_width, max_valid_drop=5)

    Filter the incoming energy_array curve starting and first_pnt and going to last_pnt.
    Each point is compared to a running average of difference between points
    determined by filter_width. The following comparison is then made:

            current_pnt - last_pnt
            ---------------------- > max_valid_drop
                   meanDiff

    If the comparison is true and the currentPoint is less than the last point
    then the point is flagged as likely bad (only values less than previous are
    flagged to avoid removing parts when the data starts to rise rapidly to
    respond to an event). If the point is good, the meanDiff is updated. In
    either case the algorithm continues through the data.

    The specification of first_pnt and last_pnt let you go through the data
    forwards or backwards.

    INPUTS:
        energy_array - numpy array containing the vector of energy to evaluate

        first_pnt - the element of the array to start with

        last_pnt - the element of the array to end with

        filter_width - the size of the running average of point difference

        max_valid_drop - the maximum ratio between current difference and expected
        difference for points to mark as valid. This parameter is optional,
        default value is 5.

    OUTPUTS:
        fitness - numpy array the same size as energy with 1 for valid points
        and 0 for invalid points
    """
    # if we have a single point, no need to check
    if first_pnt == last_pnt:
        return np.array([1])

    # initialize the output variables
    fitness = np.ones(energy_array.shape)

    # figure out the looping direction and get an initial estimate of
    #  energy difference
    loop_sign = np.sign(last_pnt - first_pnt)
    last_pnt += loop_sign  # works better with range after this
    if np.abs(last_pnt - first_pnt) < filter_width:
        var_range = range(first_pnt, last_pnt, loop_sign)
    else:
        var_range = range(first_pnt, first_pnt + loop_sign * filter_width, loop_sign)
    last_diff = energy_array[var_range].max() - energy_array[var_range].min()

    # loop through the data looking for anomalous differences
    last_checked = first_pnt
    for point_ind in range(first_pnt + 1 * loop_sign, last_pnt, loop_sign):
        # check the energy difference
        #  if very large, remove it from the group and continue
        #  if reasonable, continue
        delta_energy = energy_array[point_ind] - energy_array[last_checked]
        delta_energy_sign = np.sign(delta_energy)
        delta_energy = np.abs(delta_energy)
        if delta_energy_sign == -1 and delta_energy > max_valid_drop * last_diff:
            fitness[point_ind] = 0
            # if we haven't found a valid pnt for an entire filter_width, start over
            if loop_sign * (point_ind - last_checked) > filter_width:
                last_diff *= 2
        else:
            last_checked = point_ind
            # average last few points (also ensure a minimum check of 1e-15)
            last_diff = max(
                [((filter_width - 1) * last_diff + delta_energy) / filter_width, 1e-15]
            )

    return fitness  # end of energy_filter


def continuous_above_min(energy_array, energy_threshold, max_mistakes):
    """max_num = continuous_above_min(energy_array,energy_threshold,max_mistakes)

    Computed the number of continuous points above a threshold (energy_array is
    assumed to be temporally sorted).

    INPUTS:
        energy_array - numpy array containing the vector to evaluate

        energy_threshold - the energy threshold level

        max_mistakes - the number of points that can drop below the threshold
        before the current continuous set is marked as done

    OUTPUTS:
        max_num - the number of points in the largest continuous set found
    """
    # initialize all the counters
    max_num = 0
    cur_num = 0
    num_mistakes = 0

    # loop through energy_array points
    for energy_val in energy_array:
        if energy_val > energy_threshold:
            cur_num += 1
            if cur_num > max_num:
                max_num = cur_num
        elif num_mistakes <= max_mistakes:
            num_mistakes += 1
        else:
            num_mistakes = 0
            cur_num = 0

    return max_num
