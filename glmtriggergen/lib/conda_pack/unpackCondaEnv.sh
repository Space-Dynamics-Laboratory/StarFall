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
   echo "Usage: $0 -n <envName> -p <envPath>"
   echo -e "\t-n Miniconda env name"
   echo -e "\t-p Miniconda env path"
   echo ""
   echo -e "Example: $0 -n py3117 -p /home/developer/miniconda3/envs\n"
   exit 1 # Exit script after printing help
}

while getopts "n:p:" opt
do
   case "$opt" in
      n ) envName="$OPTARG" ;;
      p ) envPath="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$envName" ] || [ -z "$envPath" ]
then
   echo "One or more flags are missing.";
   helpFunction
fi

# Unpack environment into directory `py3117`
mkdir -p $envPath/$envName
tar -xzvf $envName.tar.gz -C $envPath/$envName

# Activate the environment. This adds `py3117/bin` to your path
source $envPath/$envName/bin/activate

# Cleanup prefixes from in the active environment.
conda-unpack

# Additionally, the following command deactivates the environment and removes it from your path
# source $envPath/$envName/bin/deactivate
