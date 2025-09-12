#!/bin/bash

##################################################################
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
##################################################################

# exit if a command fails
set -e 

if [[ "$SKIP_INIT_3" == "true" ]]; then
  echo "Skipping migrations due to SKIP_INIT_3=true"
else

# using an unset variable is an error
set -u

display_help_message() {
    echo ""
    echo "Usage: 2_run_migrations.sh [OPTION]..."
    echo "Create the StarFall database"
    echo ""
    echo "--help                show this help message"
    echo "-h, --host            database host"
    echo "-p, --port            database port"
    echo "-P, --password        user password"
    echo "-U, --username        database username"
    echo "-D, --database        database"
    echo "-d, --root_directory  root directory for other scripts"
    echo ""
    exit 0
}

# docker default values
host="/var/run/postgresql"
port="5432"
username="starfall_admin"
database="starfall_database"
password="password"
root_directory="/docker-entrypoint-initdb.d/"

# read in parameters
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--host) host="$2"; shift;;
        -p|--port) port="$2"; shift;;
        -P|--password) password="$2"; shift;;
        -U|--username) username="$2"; shift;;
        -D|--database) database="$2"; shift;;
        -d|--root_directory)
            root_directory="$2"
            [[ "$root_directory" != */ ]] && root_directory="${root_directory}/"
            shift;;
        --help) display_help_message;;
        *) echo "unknown option $1"; #display_help_message;;
    esac
    shift
done

# run migrations using shmig - https://github.com/mbucc/shmig
eval "${root_directory}shmig -m ${root_directory}migrations -t postgresql -d ${database} -H ${host} -l ${username} -p ${password} -P ${port} -s shmig_version migrate"


fi