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

This document describes how to generate the `pb2.py` protobuf python files. The `protoc` protobuf compile commands use the version of protobuf specified in the conda environment YAML file.

1. Open a terminal in a developer environment
1. Change directories to this file's location
1. Run the following script to generate the `pb2.py` protobuf python files:
    - `./generate_pb2_py_files.sh`
