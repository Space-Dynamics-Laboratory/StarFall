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
# The GLM TG Conda Environments

This document describes how to use Conda to create python environments to run the GLM Trigger Generator (TG). The shell scripts enable installing Miniconda, creating the Conda Python environment, conducting a basic test of functionality with the created Conda environment, and writing the Conda environment dependencies list to a requirements text file. Each of the shell scripts used for accomplishing the above tasks can be found within the `lib/scripts/` directory. When running the shell scripts from the command line, flags and associated specified arguments must be provided. Running the scripts without providing the necessary flags and arguments will cause the script to display a help message with a usage statement.

## Miniconda Installation

The file called `scripts/1_installMiniconda.sh` can be used to install Miniconda (which includes Conda) from the command line. The script requires a `-p <installPath>` argument be provided:

```
./scripts/1_installMiniconda.sh -p /home/developer/miniconda3/
```

After installation, this script also initializes bash for Conda, and then restarts the current shell.

## Creating Conda Environments

Once Conda is installed, two types of environments can be created for the GLM TG: (1) the unclassed development environment, and (2) the unclassed production environment. The unclassed development environment includes extra python tools mainly used for development purposes.

The script `scripts/2_createCondaEnv.sh` uses the YAML files within the `conda_envs` directory to create the Conda environments, e.g.,

```
# Create the unclassed development environment
./scripts/2_createCondaEnv.sh -p conda_envs/unclass_dev_env_py3117.yml

# Create the unclassed production environment
./scripts/2_createCondaEnv.sh -p conda_envs/unclass_prod_env_py3117.yml
```

## Testing the Conda Environments

The script `scripts/3_testCondaEnv.sh` activates the environment and runs a simple test case to check basic functionality, e.g.,

```
# Test the unclassed development environment
./scripts/3_testCondaEnv.sh -n py3117 -e unclass_dev_env

# Test the unclassed production environment
./scripts/3_testCondaEnv.sh -n py3117 -e unclass_prod_env
```

## Documenting the Conda Environments

The script `scripts/4_writeCondaList.sh` activates the provided environment name and writes a text file to `/home/developer/glmtriggergen/lib/conda_envs/` which contains a list of all dependencies in the environment along with their version numbers, build numbers, and source channels (if different than the Anaconda default channels), e.g.,

```
# Write the unclassed development environment's requirements text file
./scripts/4_writeCondaList.sh -n py3117 -e unclass_dev_env

# Write the unclassed production environment's requirements text file
./scripts/4_writeCondaList.sh -n py3117 -e unclass_prod_env
```

## Packing and Unpacking Conda Environments

The files within `lib/conda_pack` enable a user to pack and unpack portable Conda environments using the python package `conda-pack`. To package up a Conda environment, an environment must first be created using the files referenced above. (These environments include the `conda-pack` python package.) Then, the file `conda_pack/packCondaEnv.sh` can be used to pack up a Conda environment into a portable tarball.

The script `conda_pack/unpackCondaEnv.sh` creates a directory for the environment, uncompresses the tarball, activates the environment by sourcing the conda-pack activate file, and cleans up the package prefixes.

Additionally, a text file containing a list of all dependencies in the environment along with their version numbers, build numbers, and source channels (if different than the Anaconda default channels) can be created by running the `conda_pack/writeCondaPackEnvList.sh` script.

Examples of how to pack, unpack, and create a requirements file for a Conda environment is shown as follows:

```
# Change directories into the conda_pack directory
cd conda_pack

# Pack a Conda environment into a tarball
./packCondaEnv.sh -n py3117

# Unpack environment into created directory py3117
./unpackCondaEnv.sh -n py3117 -p /home/developer/miniconda3/envs/

# Write the environment's requirements text file from the unpacked Conda environment
./writeCondaPackEnvList.sh -n py3117 -p /home/developer/miniconda3/envs/
```
