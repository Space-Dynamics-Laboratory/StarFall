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

import smtplib
import ssl

import src.helper_funs.datetime_helpers as dth
import src.helper_funs.gcloud_helpers as ghf
from config import glmtriggergenconfig as settings
from src.helper_funs.util_helpers import in_glm_file_latter_half


def create_download_string(event_time, sat_ids):
    """create_download_string(event_time, sat_ids)

    Create a string of links to download the gcloud files

    Args:
        event_time (float): The event time in SSUE
        sat_ids (list): A list of satellite IDs

    Returns:
        string: A string of links to download the gcloud files
    """
    # Create two file times depending on if the event time is in first
    # or latter half of file
    if not in_glm_file_latter_half(event_time):
        file_times = [
            event_time - settings.PROCESS_INTERVAL_S,
            event_time,
        ]
    else:
        file_times = [
            event_time,
            event_time + settings.PROCESS_INTERVAL_S,
        ]

    # Download the URIs from the gcloud for the file times
    download_uris = []

    for file_time in file_times:
        [year, doy, hour, minute, second] = dth.get_year_doy_time_from_ssue(file_time)
        # Floor seconds to 0, 20, or 40.
        second = int(second - second % settings.PROCESS_INTERVAL_S)
        for sat_id in sat_ids:
            uri = ghf.get_file_list_from_gcloud(
                int(sat_id), year, doy, hour, minute, second
            )
            download_uris.append(uri[0])

    # Reformat the gsutil URIs into public URLs
    download_links = [
        "\thttps://storage.googleapis.com/" + string[5:] + "\n"
        for string in download_uris
    ]

    # Convert list of download links into a single string
    return "".join(download_links)


def compose_email(event_time_string, download_links_string):
    """compose_email(event_time_string, download_links_string)

    Compose the trigger info email message and output it as a string

    Args:
        event_time_string (string): The event time formatted as %Y-%m-%d %H:%M:%SZ
        download_links_string (string): A string of links to download the gcloud files

    Returns:
        string: A trigger info email message
    """
    message = (
        f"Subject: StarFall GLM Event Detected {event_time_string}"
        f"\n\nThe StarFall GLM Trigger Generator detected an "
        f"event with the following peak intensity time: "
        f"{event_time_string}.\n\nClick the links below to "
        f"download the GOES netCDF files for the event:\n\n"
        f"{download_links_string}\n"
        f"A GLM Trigger Generator can re-trigger the event by "
        f"ingesting the downloaded files with the following "
        f"command:\n\n\tpython3 <path-to-glmtriggergen>/"
        f"GlmTriggerGen.py -g -l -d <path-to-netCDFs>\n\n"
        f"Feel free to email StarFall-Support@sdl.usu.edu if "
        f"you have any questions."
    )
    return message


def email_trigger_info(glm_data_obj, event_time, sat_ids):
    """email_trigger_info(glm_data_obj, event_time, sat_ids)

    Create an SSL session and send a trigger info email over TLS.

    Args:
        glm_data_obj (GlmDataSet instance): An instance of the GlmDataSet class
        event_time (float): The event time in SSUE
        sat_ids (list): A list of satellite IDs
    """

    # Convert the event time into a string for the email
    event_time_string = dth.convert_ssue_to_string(event_time, "%Y-%m-%d %H:%M:%SZ")

    # Create a string of links to download the gcloud files
    download_links_string = create_download_string(event_time, sat_ids)

    # Compose the trigger email message
    message = compose_email(event_time_string, download_links_string)

    context = ssl.create_default_context()
    try:
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls(context=context)
        if settings.SENDER_PASSWORD != "":
            server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
        server.sendmail(settings.SENDER_EMAIL, settings.RECEIVER_EMAILS, message)
    except ssl.SSLCertVerificationError as err:
        print(f"\nFailed to send trigger info email.\n{err}")
        glm_data_obj.send_logs(
            [
                (
                    "error",
                    f"Failed to send trigger info email. {err}",
                )
            ]
        )
    except Exception as err:
        print(f"\nFailed to send trigger info email.\n{err}")
        glm_data_obj.send_logs(
            [
                (
                    "error",
                    f"Failed to send trigger info email. {err}",
                )
            ]
        )

    try:
        server.quit()
    except smtplib.SMTPServerDisconnected as err:
        print(f"Could not quit the server. {err}")
        glm_data_obj.send_logs(
            [
                (
                    "error",
                    f"Could not quit the server. {err}",
                )
            ]
        )
