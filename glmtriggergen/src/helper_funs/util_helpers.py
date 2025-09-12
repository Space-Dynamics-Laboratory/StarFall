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

import sys

from config import glmtriggergenconfig as settings


def debug_print(string_to_print, debug_mode):
    """debug_print(string_to_print, debug_mode)

    Args:
        string_to_print (str): String to be printed during debugging
        debug_mode (bool): A boolean to print only when debug_mode = True
    """
    if debug_mode:
        print(string_to_print)


def in_glm_file_latter_half(ssue):
    """in_glm_file_latter_half(ssue)

    Determine if a SSUE time is in the latter half of a GLM netCDF file.

    Args:
        ssue (int): a seconds since unix epoch time

    Returns:
        bool: A boolean indicating if the time is in the latter half
    """
    return (ssue % settings.PROCESS_INTERVAL_S) >= (settings.PROCESS_INTERVAL_S / 2)


def signal_handler(sig, frame):
    """signal_handler(sig, frame)

    When Ctrl+C is pressed, this will close out the socket before terminating
    the process
    """
    print("Closing DB and exiting.")
    sys.exit(0)
