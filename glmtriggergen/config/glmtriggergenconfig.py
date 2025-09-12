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
"""
Config file for the GLM Trigger Generator
"""
import os
import subprocess

from dotenv import load_dotenv

from config.parse_version_file import parse_version_file

load_dotenv()

## Version of the GLM Trigger Generator
GLM_TG_VERSION = "1.3.0"

## Append the commit hash and branch to the version number
try:
    results = subprocess.run(
        ["sh", "config/commitHashAndBranchName.sh"],
        capture_output=True,
        text=True,
        check=True,
    )
    COMMIT_HASH_AND_BRANCH_NAME = "." + results.stdout
except subprocess.CalledProcessError:
    try:
        VERSION_FILE_STRING = "version.txt"
        version_dict = parse_version_file(VERSION_FILE_STRING)
        if version_dict is None:
            COMMIT_HASH_AND_BRANCH_NAME = ""
        else:
            COMMIT_HASH_AND_BRANCH_NAME = (
                "." + version_dict["commit_name"] + "/" + version_dict["short_hash"]
            )
    except Exception:
        print(
            "Could not retrieve git commit hash or branch name for full version number."
        )
        COMMIT_HASH_AND_BRANCH_NAME = ""
GLM_TG_VERSION_FULL = GLM_TG_VERSION + COMMIT_HASH_AND_BRANCH_NAME

## Load the environment configurations, otherwise use defaults

# All environment configurations, including path information, port
# settings, and database credentials, are found in the .env file

# Path information for glm processing
GS_UTIL = os.environ.get("GS_UTIL", "gsutil")
BASE_PATH = os.environ.get("BASE_PATH", "/home/developer/glmtriggergen/")
DATA_PATH = os.path.join(BASE_PATH, os.environ.get("DATA_DIR", "data/"))
L2_CAL_TABLES_PATH = os.path.join(
    BASE_PATH, os.environ.get("CAL_TABLES_DIR", "glm_cal_tables/l2_cal_tables/")
)

# Port to use for notification of new event
PUB_CONNECTION = os.environ.get("PUB_CONNECTION", "tcp://hostname:5666")
TRIGGER_TOPIC = os.environ.get("TRIGGER_TOPIC", "trigger.1")
STATUS_CONNECTION = os.environ.get("STATUS_CONNECTION", "tcp://*:5668")

# StarFall database credentials
DB_USER = os.environ.get("DB_USER", "starfall_admin")
DB_NAME = os.environ.get("DB_NAME", "starfall_database")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
DB_HOST = os.environ.get("DB_HOST", "database")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))

# Save results to database
SAVE_TO_DATABASE = os.environ.get("SAVE_TO_DATABASE", "True") == "True"

# SMTP credentials for emailing trigger info
SMTP_SEND = (os.environ.get("SMTP_SEND", "False") == "True")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "changeme.server.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "25"))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "changeme@server.com")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "")
receiver_emails_list = os.environ.get("RECEIVER_EMAILS", "").split(";")
RECEIVER_EMAILS = [x.strip() for x in receiver_emails_list]


## Constants used for GLM processing
# GOES sats to hunt for possible data on gcloud. Note: Omitting a sat
# here will prevent the GLM trigger generator from downloading that GOES
# sat data for processing.
# Note: Start and stop dates were obtained from the respective gclouds, a start
# date must be specified, but end dates do not need to be specified for
# currently operational satellites. However, GOES satellites do not
# always generate data between their start and stop dates. There have
# been occasional gaps in coverage for various reasons.
SAT_INFO_DICT = {
    "GOES-16": {
        "ID": 16,
        "GCLOUD_START_STRING": "20180213161000",
        "GCLOUD_END_STRING": "20250407200340",
    },
    "GOES-17": {
        "ID": 17,
        "GCLOUD_START_STRING": "20181002162420",
        "GCLOUD_END_STRING": "20230110182009",
    },
    "GOES-18": {"ID": 18, "GCLOUD_START_STRING": "20221104212440"},
    "GOES-19": {"ID": 19, "GCLOUD_START_STRING": "20250115135500"},
}
SAT_ID_NUMS = [satellite_info["ID"] for satellite_info in SAT_INFO_DICT.values()]
CLUSTER_TIME_S = 2.0
CLUSTER_DISTANCE_M = 25.0e3
# Will filter out all clusters with durations beyond this limit
CLUSTER_DURATION_LIMIT_S = 10.0
MIN_ENERGY_LVL_J = 5e-15
VALID_RANK = 30
# Occasionally, GOES satellites experience many noisy FP events almost
# simultaneously (e.g., 2023-09-21 at 17:59:53)
# MAX_NUM_TRIGGERS limits the number of triggers from a single batch of files
# to less than MAX_NUM_TRIGGERS
MAX_NUM_TRIGGERS = 20
STRONG_SIGNAL_RANK_THRESHOLD = 175
# For the Rocket model data preprocessing
ROCKET_MODEL_NAME = "rocket_pipeline_v2.joblib"
DOWN_SAMPLE_LENGTH = 1000  # Chosen due to distributions in training data
RANDOM_STATE_SEED = 321
TRIGGER_PROB_THRESHOLD = 0.44  # Chosen due to a model performance analysis

### NetCDF File Processing Configurations ###
# Time (in secs) to wait before attempting to download next .nc files
WAIT_TIME_S = 200.0
# Time steps (in secs) for processing new data in continuous mode. This is
# chosen to match the 20 secs of data in each GLM .nc files.
PROCESS_INTERVAL_S = 20.0
# Time window size (in secs) centered on eventDateStrings to search for related .nc files
PROCESS_TIME_SIZE_S = 20.0
# The max time (in secs) to hold off processing files until all are downloaded
MAX_HOLD_TIME = 10000
# The max number of status and log records to hold in the queue and send on each status request
MAX_QUEUED_STATUS_RECORDS = 300
