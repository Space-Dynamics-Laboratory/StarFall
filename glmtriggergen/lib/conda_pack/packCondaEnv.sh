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
   echo "Usage: $0 -n <envName>"
   echo -e "\t-n Miniconda env name"
   echo ""
   echo -e "Example: $0 -n py3117\n"
   exit 1 # Exit script after printing help
}

while getopts "n:" opt
do
   case "$opt" in
      n ) envName="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$envName" ]
then
   echo "The environment name argument is missing.";
   helpFunction
fi

# Activate the conda env
eval "$(conda shell.bash hook)" # This enables activating from inside a shell script
conda activate $envName
echo "$(conda env list)" # Verify the correct environment is being used

# Pack environment $envName into $envName.tar.gz
conda pack -n $envName
