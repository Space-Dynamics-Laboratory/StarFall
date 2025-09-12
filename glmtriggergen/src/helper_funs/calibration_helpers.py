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


def find_nearest_unmasked_value(lookup_table, table_coord):
    """
    Finds the nearest non-masked value in a masked array to a given coordinate.

    Args:
        lookup_table (numpy masked array): An array that maps pixel
        x-y coordinates to calibration lookup table values
        table_coord: A tuple representing the x-y table coordinate,
        e.g., (pixel_x, pixel_y)

    Returns:
        The nearest non-masked value at the given coordinate.
    """

    # Access the mask of the lookup table
    mask = lookup_table.mask

    # Find indices where the mask is False (unmasked)
    unmasked_indices = np.where(~mask)

    # Calculate Euclidean distances to unmasked elements
    distances = np.linalg.norm(
        np.array(unmasked_indices).T - np.array(table_coord), axis=1
    )

    # Find index of the closest unmasked element
    nearest_index = np.argmin(distances)

    # Return the lookup table value at the nearest unmasked index
    nearest_x = unmasked_indices[0][nearest_index]
    nearest_y = unmasked_indices[1][nearest_index]

    return lookup_table[nearest_x, nearest_y]
