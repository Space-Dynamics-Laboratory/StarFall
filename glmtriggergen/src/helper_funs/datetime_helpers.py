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
from datetime import datetime, timedelta

EPOCH = datetime(1970, 1, 1, 0, 0, 0, 0)


def get_year_doy_time_from_ssue(time_ssue):
    """[year, doy, hour, minute, second] = get_year_doy_time_from_ssue(time_ssue)

    Convert the incoming time in seconds since unix epoch to a standard date
    vector with year, day of year, hour, minute, and second (all ints with
    sub-second portion ignored)

    Args:
        time_ssue (int): Seconds since unix epoch

    Returns:
        list: A list of datetime values ([year, doy, hour, minute, second])
    """

    # calculate the date represented by SSUE
    date = EPOCH + timedelta(seconds=time_ssue)
    year = int(date.year)

    # calculate the delta in days
    ddays = (date - datetime(year, 1, 1, 0, 0, 0)) / timedelta(days=1)
    doy = int(ddays) + 1

    return [year, doy, int(date.hour), int(date.minute), int(date.second)]


def get_ssue_from_datetime_string(datetime_string):
    """get_ssue_from_datetime_string(datetime_string)

    Convert the incoming time string of the form YYYYmmddHHMMSS into seconds
    since the unix epoch.

    Args:
        datetime_string (string): A datetime string of the form YYYYmmddHHMMSS

    Returns:
        int: Seconds since unix epoch.
    """

    # Convert the string into a datetime object
    datetime_obj = datetime.strptime(datetime_string, "%Y%m%d%H%M%S")

    # Convert into seconds since unix epoch
    return (datetime_obj - EPOCH).total_seconds()


def convert_ssue_to_datetime(ssue):
    """convert_ssue_to_datetime(ssue)

    Add the seconds since unix epoch timedelta to the epoch datetime object.

    Args:
        ssue (int): Seconds since the UNIX epoch

    Returns:
        datetime: A datetime object
    """
    return EPOCH + timedelta(seconds=ssue)


def convert_ssue_to_string(ssue, string_format="%Y-%m-%d %H:%M:%S"):
    """convert_ssue_to_string(ssue)

    Args:
        ssue (int): Seconds since the UNIX epoch
        string_format (string): Format for the string. Default is %Y-%m-%d %H:%M:%S

    Returns:
        string: Datetime string of the format string_format
    """
    datetime_obj = convert_ssue_to_datetime(ssue)
    return datetime_obj.strftime(string_format)


# def convert_to_doy(date_time):
#     """convert_to_doy(date_time)

#     Converts a datetime structure to a time string with doy of year instead
#     (YYYYDOYhhmmss)

#     INPUTS:
#         date_time - datetime structure

#     OUTPUTS:
#         time_with_doy - string representing the same time with DOY instead of
#         months and day of month (YYYYDOYhhmmss)
#     """
#     # calculate the day of year
#     doy = (
#         int(
#             (date_time - datetime(date_time.year, 1, 1, 0, 0, 0, 0)) / timedelta(days=1)
#         )
#         + 1
#     )

#     # create the string
#     time_with_doy = (
#         str(date_time.year) + str(doy).zfill(3) + date_time.strftime("%H%M%S")
#     )

#     return time_with_doy
