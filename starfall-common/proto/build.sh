#!/usr/bin/env bash

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

# Path to this plugin
PROTOC_GEN_TS_PATH="../../node_modules/.bin/protoc-gen-ts"

# Directory to write generated code to (.js and .d.ts files)
OUT_DIR="."
protoc \
  --proto_path="/workspace/starfall-common/proto" \
  --plugin="protoc-gen-ts=${PROTOC_GEN_TS_PATH}" \
  --js_out="import_style=commonjs,binary:${OUT_DIR}" \
  --ts_out="${OUT_DIR}" \
  /workspace/starfall-common/proto/LightCurve.proto
protoc \
  --proto_path="/workspace/starfall-common/proto" \
  --plugin="protoc-gen-ts=${PROTOC_GEN_TS_PATH}" \
  --js_out="import_style=commonjs,binary:${OUT_DIR}" \
  --ts_out="${OUT_DIR}" \
  /workspace/starfall-common/proto/Message.proto

OUT_DIR="./Status/"
protoc \
  --proto_path="./Status/" \
  --plugin="protoc-gen-ts=${PROTOC_GEN_TS_PATH}" \
  --js_out="import_style=commonjs,binary:${OUT_DIR}" \
  --ts_out="${OUT_DIR}" \
  ./Status/StatusReply.proto
protoc \
  --proto_path="./Status/" \
  --plugin="protoc-gen-ts=${PROTOC_GEN_TS_PATH}" \
  --js_out="import_style=commonjs,binary:${OUT_DIR}" \
  --ts_out="${OUT_DIR}" \
  ./Status/StatusRequest.proto