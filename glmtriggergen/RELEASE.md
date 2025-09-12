<!--
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
-->

# Release Notes for the StarFall GLM Trigger Generator

This document contains a history of noteworthy changes to the StarFall GLM Trigger Generator Code. The current version number of the code can be accessed by running the following Python command.

```bash
python3 ./GlmTriggerGen.py --version
```

## v1.3.0

- [improvement] Cleaned up the repo for public release
- [feature] Removed the need for the GLM Status microservice by building a rolling queue for status and logs
- [improvement] Trained a new ROCKET model (v2) on an updated dataset
- [bigfix] Add all available .env files to the Docker containers

## v1.2.0

- [feature] Added a git hook for auto running the unit tests with each push
- [improvement] Updated the Python version to 3.11.7 along with dependencies
- [improvement] Migrated Python environments to Conda in dockerfiles
- [improvement] Clarified the dev, and prod docker compose and dockerfiles
- [feature] Enabled the version to display the git commit branch name and hash
- [bigfix] Improved database queries for new platform and sensor IDs

## v1.1.0

- [feature] Generate velocity estimates for applicable stereo events
- [feature] Add pytest unit tests and generate a coverage report
- [feature] Enable the unclassed GLM trigger messages to be emailed via SMTP
- [improvement] Migrate the docker container to RedHat 8
- [refactor] Refactor the Python code into PEP 8 compliant modules
- [bugfix] Prevent duplicate triggers which occur near the boundary of files
- [bugfix] Print datetime strings instead of SSUE when no files are found

## v1.0.0

- [feature] Add ROCKET bolide probability to internal plot legends
- [feature] Integrate the ROCKET filter into the processing pipeline
- [feature] Create scripts for the rocket data generation and model training
- [feature] Design GOES netCDF file ingest to more appropriately handle files
- [feature] Calculate total radiated energy using continuos calibration tables
- [feature] Send status and logs to GlmStatus microservice
- [feature] Filter lightning false events with large GLM event data spread
- [feature] Filter false events with unreasonably long durations
- [feature] Enable ingest of GLM data from GOES-18 satellite
- [feature] Filter stereo events below a configurable altitude threshold
- [feature] Estimate altitude for stereo events
- [feature] Rank GLM clusters using number of continuos energy points above a threshold
- [feature] Mark duplicate energies and unusual jumps in energy
- [feature] Database triggers using ZMQ connections and protobuf messages
- [feature] Create custom GLM groups / clusters using geospatial-temporal clustering
