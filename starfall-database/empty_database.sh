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

# read in parameters
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--host) host="$2"; shift;;
        -p|--port) port="$2"; shift;;
    esac
    shift
done

psql \
    --host=$host \
    --port=$port \
    --dbname=starfall_database \
    --username=starfall_admin \
    --command="DELETE FROM starfall_db_schema.tags;
    DELETE FROM starfall_db_schema.point_source_accessory;
    DELETE FROM starfall_db_schema.point_sources;
    DELETE FROM starfall_db_schema.light_curves;
    DELETE FROM starfall_db_schema.sightings;
    DELETE FROM starfall_db_schema.locations;
    DELETE FROM starfall_db_schema.sensors;
    DELETE FROM starfall_db_schema.platforms;
    DELETE FROM starfall_db_schema.history;
    DELETE FROM starfall_db_schema.events;
    DELETE FROM starfall_db_schema.meta;"
