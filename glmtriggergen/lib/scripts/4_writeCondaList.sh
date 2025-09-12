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

# This script writes the conda environment list to a text file created from
# installConda.sh

helpFunction()
{
   echo ""
   echo "Usage: $0 -n envName -e envType"
   echo -e "\t-n Miniconda env name"
   echo -e "\t-e Miniconda env type"
   echo ""
   echo -e "Example: $0 -n py3117 -e unclass_dev_env"
   echo -e "Example: $0 -n py3117 -e unclass_prod_env\n"
   exit 1 # Exit script after printing help
}

while getopts "n:e:" opt
do
   case "$opt" in
      n ) envName="$OPTARG" ;;
      e ) envType="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$envName" ] || [ -z "$envType" ]
then
   echo "One or more flags are missing.";
   helpFunction
fi

# Activate the conda env
eval "$(conda shell.bash hook)" # This enables activating from inside a shell script
conda activate $envName
echo "$(conda env list)" # Verify the correct environment is being used

# Write the conda list to a text file
FILE_NAME=${envType}_${envName}.txt
conda list > /home/developer/glmtriggergen/lib/conda_envs/$FILE_NAME
echo "Wrote the conda env to the text file: /home/developer/glmtriggergen/lib/conda_envs/$FILE_NAME"
