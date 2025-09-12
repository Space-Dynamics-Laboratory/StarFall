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

The Global Lightning Mapper (GLM) Bolide Trigger Generator

# Introduction

The GLM Trigger Generator attempts to detect bolide events in GLM files pulled from a specified directory or from the NOAA google cloud buckets depending on the configuration. See below for additional information on installation, setup, configuration, and usage examples. See the StarFall Software User Manual for more details on how to connect the GLM Trigger Generator to the rest of the StarFall back-end microservices.

# Installation

The source code was built to run using Python 3.11.7. The GLM Trigger Generator and GLM Status executable are packaged together in a glm.tar.gz compressed archive. Provided the environment contains all of the necessary GLM Trigger Generator software dependencies (see ./requirements.txt for the main dependencies), the GLM Trigger Generator software can be unpacked to the desired location using the following command:

```bash
tar -xzvf glm.tar.gz .
```

See the conda environment YAML and text files in `lib/conda_envs` for a comprehensive list of all dependencies for the environment necessary to run the GLM Trigger Generator.

# Development

This directory uses git hooks to run tests before pushes. Run the following command in a terminal to add the custom hook to your git hooks path: `git config --local include.path git_hooks`

# Setup and Configuration

A list of configuration settings can be found in the config/glmtriggergenconfig.py file. Some of these settings can be adjusted by creating a `.env` file. For example, you may specify in a `.env` file whether the GlmTriggerGen.py should database triggers by adding the line `SAVE_TO_DATABASE=True`. Other configuration settings may also be specified in a `.env` file including the base path (if not running from a docker container), and port assignments for triggers, logs, and status messaging. See the `example.env` file for additional usage cases.

# Usage

The following usage code assumes you have changed directory to the code location.

```bash
cd /<path-to-glm-trigger-gen-files>/
```

## Command

```bash
python3 ./GlmTriggerGen.py
```
The GLM trigger generator attempts to detect bolide events in GLM files pulled from the google cloud service or stored locally depending or specified input options. All inputs are optional. If no inputs are provided, it assumes the google cloud is accessible and starts in continuous mode from current time.

## Flags

**-c** \
continuous mode: From the current system time, or specified starting time (```-s \<start-time\>```), will process all files moving forward in a continuous manner. Will continue to run until killed (e.g., with ctrl-c). Note, however, that current files are given priority over other events in the list so it may take a while to get through all events provided by ```-f```, ```-e```, and ```-g``` as they will only be processed during the down time while waiting for new files to be uploaded to GLM's cloud archive.

**-s \<start-time\>** \
Time to start in the format YYYYMMDDhhmmss. If not provided, starts at the current time minus the continuous mode wait period required by the config file (see WAIT_TIME_S in config/glmtriggergenconfig.py) for data generation purposes.

**-n \<end-time\>** \
Time to end in the format YYYYMMDDhhmmss. If not specified, continuous mode will run until ctrl-c is pressed.

**-d \<data-path\>** \
Directory path to which data should be saved. If none provided, default behavior will create a /data/ directory.

**-f \<event-file-path\>** \
Name of the event txt file to load event times from. Should contain a column of dates in the format YYYYMMDDhhmmss.

**-e \<event-time\>** \
Event time to add to the list to be processed. Should be in the format YYYYMMDDhhmmss. Will be appended to the list provided by the event file if it is specified (see ```-f```).

**-g** \
generate events list: Generate event times to analyze based on the start times of all files currently in the data directory. Will be appended to the list provided by eventFile if it is specified.

**-l** \
local only mode: Only uses data already present in data_dir. Will not download any new files. Also assumes local files should be kept after processing (i.e., silently turns on the --keep-netcdfs flag).

**-p** \
generate plots: Diagnostic plots are made for the triggering clusters and near misses. Plots are saved in \<data-path\> (see ```-d```). (NOT RECOMMENDED IN CONTINUOUS MODE)

**-o** \
output trigger data: Save a .csv file of trigger times and number of triggers to \<data-path\> (see ```-d```). (NOT RECOMMENDED IN CONTINUOUS MODE)

**--keep-netcdfs** \
If --keep-netcdfs is included, none of the downloaded GLM netCDF files will be deleted after processing. (NOT RECOMMENDED IN CONTINUOUS MODE)

**--debug** \
debug mode: Turn on additional output for troubleshooting the GLM trigger generator.

**-v**, **--version** \
version: Return the version number of the GLM trigger generator code. See RELEASE.md for a history of the main changes in the versions.

## Examples

### Running in Continuous Mode

Running the GLM trigger generator without providing any flags will default to continuous mode (```-c```) starting from the current time. It will also download GOES netCDFs from the respective satellite's Google clouds, hunt for triggers, and remove the downloaded netCDFs upon completion. Hence, the following two calls will run the same.

```bash
python3 ./GlmTriggerGen.py
```

```bash
python3 ./GlmTriggerGen.py -c -s <current-time>
```

An end time may also be provided to allow continuous processing over a desired window of time.

```bash
python3 ./GlmTriggerGen.py -c -s <start-time> -n <end-time>
```

The `--keep-netcdfs` flag causes the downloaded netcdfs to be saved locally. This is NOT RECOMMENDED for continuous mode as the amount of saved data may grow to be very large over time.

### Processing Local GLM netCDF Files

The default location for the downloaded netCDFs is a created /data/ directory. However, this can be overridden by providing a path to the `-d` flag.

```bash
python3 ./GlmTriggerGen.py -c -d <data-path>
```

Additionally, the `-l` flag tells the GLM trigger generator to hunt for the desired netCDFs locally (in the default or provided data directory) instead of downloading them. (The GLM trigger generator silently provides the `--keep-netcdfs` flag when the `-l` flag is provided to prevent local netCDFs from being removed after processing.)

```bash
python3 ./GlmTriggerGen.py -c -l -d <data-path>
```

The start and end time flags (`-s` and `-n`, respectively) can also be used to process local historic data. Simply provide the start time of the oldest netCDF file to the `-s` flag and the end time of the newest netCDF file to the `-n` flag. Keep in mind, if there are gaps between local netCDF files, the GLM trigger generator will skip those missing intervals until it reaches the next netCDF file that falls within the given start and end times.

```bash
python3 ./GlmTriggerGen.py -c -l -d <data-path> -s <start-time> -n <end-time>
```

### Running in Non-Continuous Mode

The GLM trigger generator can also be provided a specific date to hunt for triggers. The window of time centered on the provided date (for which the GLM trigger generator hunts for triggers) is configurable in the config/glmtriggergenconfig.py file (as the `PROCESS_TIME_SIZE_S`).

```bash
python3 ./GlmTriggerGen.py -e <event-time>
```

Alternatively, a text file with a column of dates (formatted as YYYYMMDDhhmmss) can be provided if the user wants to hunt for triggers across multiple dates.

```bash
python3 ./GlmTriggerGen.py -f <event-file-path>
```

Providing either the `-e` or `-f` flags will override the GLM trigger generator's continuous mode. Instead, the trigger generator will exit after searching for triggers at the provided date(s).

A user can also have the GLM trigger generator infer dates from provided GLM netCDF files in the `DATA_DIR` by using the `-g` flag, e.g.,

```bash
python3 ./GlmTriggerGen.py -g
```

### Additional Processing Details

Detailed processing output can be seen by providing the GLM trigger generator with the `--debug` flag. This is also NOT RECOMMENDED for continuous mode as the amount of output may grow to be very large over time.

```bash
python3 ./GlmTriggerGen.py --debug -e <event-time>
```

Additional plots, including the triggered light curves, can be saved (to the default or provided data directory) if the `-p` flag is provided. However, this is NOT RECOMMENDED in continuous mode.

```bash
python3 ./GlmTriggerGen.py -p -e <event-time>
```

### Help Documentation

The GLM trigger generator contains additional documentation which can be accessed by the `--help` flag.

```bash
python3 ./GlmTriggerGen.py --help
```

Additionally, the version of the GLM trigger generator code can be accessed via the `-v` or `--version` flags.

```bash
python3 ./GlmTriggerGen.py --version
```