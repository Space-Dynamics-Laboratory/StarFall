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

# set default values
host="localhost"
port="5432"
username="postgres"
password="password"
database="starfall_database"

# read in parameters
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--host) host="$2"; shift;;
        -p|--port) port="$2"; shift;;
        -P|--password) password="$2"; shift;;
        -U|--username) username="$2"; shift;;
        -D|--database) database="$2"; shift;;
    esac
    shift
done

# The setup script creates the following:
# - starfall_admin, starfall_microservice users
# - the starfall_database
./startup_scripts/1_setup_database.sh \
    --host $host \
    --port $port \
    --database $database \
    --username $username \
    --root_directory "./startup_scripts/dbscripts/"

./startup_scripts/2_run_migrations.sh \
    --host $host \
    --port $port \
    --database $database \
    --username $username \
    --password $password \
    --root_directory "./startup_scripts/"
