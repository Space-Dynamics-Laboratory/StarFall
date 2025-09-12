#!/bin/bash

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

# exit if a command fails
set -e 

if [[ "$SKIP_INIT_1" == "true" ]]; then
  echo "Skipping setup database due to SKIP_INIT_1=true"
else

# using an unset variable is an error
set -u

display_help_message() {
    echo ""
    echo "Usage: 1_create_database.sh [OPTION]..."
    echo "Create the StarFall database"
    echo ""
    echo "--help                show this help message"
    echo "-h, --host            database host"
    echo "-p, --port            database port"
    echo "-U, --Username        database username"
    echo "-d, --root_directory  root directory for other scripts"
    echo ""
    exit 0
}

# docker default values
host="/var/run/postgresql"
port="5432"
username="postgres"
root_directory="/docker-entrypoint-initdb.d/dbscripts/"

# read in parameters
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--host) host="$2"; shift;;
        -p|--port) port="$2"; shift;;
        -U|--username) username="$2"; shift;;
        -d|--root_directory)
            root_directory="$2"
            [[ "$root_directory" != */ ]] && root_directory="${root_directory}/"
            shift;;
        --help) display_help_message;;
        *) echo "unknown option $1"; #display_help_message;;
    esac
    shift
done

echo "*******************************"
echo "Starting startup script"
echo "*******************************"
echo "Connecting to $username@$host:$port"

echo "*******************************"
echo "Creating users..."
echo "*******************************"
psql --host=$host --port=$port --username=$username --file="${root_directory}create_users.sql"

echo "*******************************"
echo "Creating database..."
echo "*******************************"
psql --host=$host --port=$port --username=$username --file="${root_directory}create_database.sql"


fi