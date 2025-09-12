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
"""This file provides a status and logging helper class. This class stores status in a queue and
# returns status messages based on UI request.
"""
import threading
import warnings
from datetime import datetime, timedelta

import zmq

import src.helper_funs.datetime_helpers as dth
from config import glmtriggergenconfig as settings
from src.protobuf.status_reply_pb2 import StatusInformation
from src.protobuf.status_request_pb2 import StatusRequest


class StatusHelperQueue:
    """StatusHelperQueue

    This StatusHelperQueue class provides basic methods for storing status
    and logs inside a message queue. It also provides methods to request those
    logs from the UI.
    """

    def __init__(self, connection) -> None:
        """__init__(self, connection) -> None

        INPUTS:
        connection: The server ip address.
        """
        # Setup Self Vars
        self.status_proto = StatusInformation()
        self.LOG_KEY_STRING = "Recent Logs"
        self._stop_event = threading.Event()
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(connection)

    def __del__(self):
        print("Closing zmq socket")
        self.socket.close()

    def run_status_server_thread(self):
        """This is the status message thread

        Args:
            context (_type_): zmq context
            socket (_type_): zmq socket
            status_proto (_type_): message that is needing to be sent.
        """

        while True:
            # Server waiting for request
            message = self.socket.recv()
            request = StatusRequest()
            request.ParseFromString(message)
            # print(f"Queue Size: {len(self.status_proto.record)}")
            self.socket.send(self.status_proto.SerializeToString())

            # Check for queue size and remove records as specified
            if len(self.status_proto.record) > settings.MAX_QUEUED_STATUS_RECORDS:
                number_of_records_to_delete = (
                    len(self.status_proto.record) - settings.MAX_QUEUED_STATUS_RECORDS
                )
                # print(f"Deleting Records: {number_of_records_to_delete}")
                del self.status_proto.record[0:number_of_records_to_delete]

    def send_status(self, status_tuples_list):
        """send_status(status_tuples_list)

        Store status into queue

        INPUTS:
            status_tuples_list - A list of tuples, where each tuple is a pair
            of strings. The first string is the status key, and the second
            string is the status message.

        OUTPUTS:
            There are no return outputs. The specified data will be stored to the queue.
        """
        # Check if the StatusHelper object was provided a socket and topic
        if self.socket is None:
            return

        # Make sure we have a non-empty status list
        if not status_tuples_list:
            warnings.warn("No status_tuples_list provided. Publish function aborting.")
            return

        # For each key-value pair in the status list...
        for status_key, status_value in status_tuples_list:
            current_time = datetime.utcnow().strftime("%Y-%m-%d %j %H:%M:%S.%f")
            # Add a new status record to the status message object
            new_status_record = self.status_proto.record.add()

            # Give the status record a key and value
            new_status_record.main_key = status_key
            new_status_record.sub_key = ""

            status_item = new_status_record.status.add()
            status_item.timestamp = current_time
            status_item.status = f"{status_value}"
            status_item.error_flag = False

    def send_logs(self, log_tuples_list):
        """send_logs(self,log_tuples_list)

        Store log message into queue

        Args:
            log_tuples_list (list): A list of tuples, where each tuple is a pair
            of strings. The first string is the log type, and the second
            string is the log message. Log types must be one of "debug",
            "info", "warning", or "error".

        OUTPUTS:
            There are no return outputs. The specified data will be stored in a queue
        """

        if self.socket is None:
            return

        for log_type, log_message in log_tuples_list:
            current_time = datetime.utcnow().strftime("%Y-%m-%d %j %H:%M:%S.%f")
            # Add a new status record to the status message object

            new_status_record = self.status_proto.record.add()
            # Give the status record a key and value
            new_status_record.main_key = f"{log_type} Log"
            new_status_record.sub_key = self.LOG_KEY_STRING

            status_item = new_status_record.status.add()
            status_item.timestamp = current_time
            status_item.status = f"{current_time}: ({log_type}) {log_message}"
            status_item.error_flag = False


def send_setup_status(setup, event_dates_que, status_helper):
    """send_setup_status(setup, event_dates_que, status_helper)

    Print and log the setup of the GLM trigger generator

    Args:
        setup (tuple): A named tuple of the GLM trigger generator setup
        event_dates_que (deque): An deque of event dates to be processed
        status_helper (StatusHelper Instance): An instance of the StatusHelper class
    """
    start_time = datetime.utcnow() - timedelta(seconds=settings.WAIT_TIME_S)

    # Create strings for printing and logging
    smtp_send_string = f"Sending trigger info via SMTP:\t{settings.SMTP_SEND}"
    events_specified_string = f"Events specified:\t\t{len(event_dates_que)}"
    events_start_date_string = (
        "Specified events start:\t\t"
        + dth.convert_ssue_to_string(event_dates_que[0], "%Y/%m/%d %H:%M:%S")
    )
    events_end_date_string = "Specified events end:\t\t" + dth.convert_ssue_to_string(
        event_dates_que[-1], "%Y/%m/%d %H:%M:%S"
    )
    continuous_mode_string = f"Continuous mode:\t\t{setup.continuous_mode}"
    start_time_string = f"Start time:\t\t\t{start_time.strftime('%Y/%m/%d %H:%M:%S')}"
    end_time = dth.convert_ssue_to_datetime(setup.processing_end_time)
    end_time_string = f"End time:\t\t\t{end_time.strftime('%Y/%m/%d %H:%M:%S')}"
    data_dir_string = f"Data directory to use:\t\t{setup.data_dir}"
    use_local_files_string = f"Use only local netCDF files:\t{setup.local_only}"
    keep_netcdf_files_string = f"Keep local netCDF files:\t{setup.keep_netcdfs}"
    create_plots_string = f"Create plots:\t\t\t{setup.do_plots}"
    debug_mode_string = f"Debug mode:\t\t\t{setup.debug_mode}"

    # Print the setup strings
    print(smtp_send_string)
    print(events_specified_string)
    print(events_start_date_string)
    print(events_end_date_string)
    print(continuous_mode_string)
    print(start_time_string)
    print(end_time_string)
    print(data_dir_string)
    print(use_local_files_string)
    print(keep_netcdf_files_string)
    print(create_plots_string)
    print(debug_mode_string)

    # Log the setup
    status_helper.send_logs(
        [
            ("info", smtp_send_string),
            ("info", events_specified_string),
            ("info", events_start_date_string),
            ("info", events_end_date_string),
            ("info", continuous_mode_string),
            ("info", start_time_string),
            ("info", end_time_string),
            ("info", data_dir_string),
            ("info", use_local_files_string),
            ("info", keep_netcdf_files_string),
            ("info", create_plots_string),
            ("info", debug_mode_string),
        ]
    )
