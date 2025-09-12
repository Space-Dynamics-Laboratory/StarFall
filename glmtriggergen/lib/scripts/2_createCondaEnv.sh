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
   echo "Usage: $0 -p <envFilePath>"
   echo -e "\t-p Miniconda env file path"
   echo ""
   echo -e "Example: $0 -p conda_envs/unclass_dev_env_py3117.yml"
   echo -e "Example: $0 -p conda_envs/unclass_prod_env_py3117.yml\n"
   exit 1 # Exit script after printing help
}

while getopts "p:" opt
do
   case "$opt" in
      p ) envFilePath="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$envFilePath" ]
then
   echo "The flag -p <envFilePath> must be provided";
   helpFunction
fi

# Attempt to create a conda env
conda env create -n py3117 -f $envFilePath --solver=libmamba
