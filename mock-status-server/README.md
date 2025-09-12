<!-- 
# ------------------------------------------------------------------------
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
# ------------------------------------------------------------------------
-->

# Mock Status Server

Listens for a status request message and responds with mock status information.

## Project Setup

```sh
npm install
```

## Run mock-status-server

```sh
npm run serve
```

By default the server will listen on port 6666 but you can change the port with
the `-p` or `--port` flag.

When running with `npm run serve` include `--` between npm arguments and
arguments for the mock status server

```sh
npm run serve -- -p 3000
```

The server must be configured to point to the mock status server(s) in
[starfall-server/src/config/starfall-viewer-server-development.config](../starfall-server/src/config/starfall-viewer-server-development.config)
