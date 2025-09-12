#!/bin/sh

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
#
# Adds a version.txt file in the top level directory that contains the
# most recent commit hash, date-time, tag, and branch.

topDir=$(git rev-parse --show-toplevel)
outfile="${topDir}/version.txt"
commHash=$(git rev-parse HEAD)
commDate=$(git show -s --format=%ci)
commVersion=$(git describe --tags)
commBranch=$(git rev-parse --abbrev-ref HEAD)
printf "${commHash}\n${commDate}\n${commVersion}\n${commBranch}" > $outfile
echo "Created a ${outfile} file"
