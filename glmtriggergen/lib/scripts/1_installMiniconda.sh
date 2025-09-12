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

helpFunction()
{
   echo ""
   echo "Usage: $0 -p <installPath>"
   echo -e "\t-p Miniconda installation directory"
   echo ""
   echo -e "Example: $0 -p /home/developer/miniconda3/\n"
   exit 1 # Exit script after printing help
}

while getopts "p:" opt
do
   case "$opt" in
      p ) installPath="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$installPath" ]
then
   echo "The flag -p <installPath> must be provided";
   helpFunction
fi

# Install miniconda
CONDA_VERSION="py311_25.1.1-2"
MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-${CONDA_VERSION}-Linux-x86_64.sh"
SHA256SUM="d8c1645776c0758214e4191c605abe5878002051316bd423f2b14b22d6cb4251"
INSTALL_PATH="$installPath/miniconda3"

mkdir -p $INSTALL_PATH
wget $MINICONDA_URL -O $INSTALL_PATH/miniconda.sh
echo "${SHA256SUM} $INSTALL_PATH/miniconda.sh" > $INSTALL_PATH/shasum
sha256sum --check $INSTALL_PATH/shasum
bash $INSTALL_PATH/miniconda.sh -b -u -p $INSTALL_PATH
rm -rf $INSTALL_PATH/miniconda.sh $INSTALL_PATH/shasum

# Add conda to path
export PATH=$INSTALL_PATH/bin:$PATH

# Initialize conda for bash
conda init bash

# Restart the current shell
echo 'Restarting the current shell'
exec "$SHELL"
