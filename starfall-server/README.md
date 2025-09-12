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

# StarFall Server

The server is written in typescript and serves starfall viewer. It handles
requests for data from connected clients via socket.io. It also listens to
database notification channels for new events and event updates so it can
update connected clients when new events begin processing and enter user
analysis.

The server also has zmq sockets which can be used to communicate directly with
the microservices, however, this is not yet implemented.

## Project Setup

```sh
npm install
```

## Run the dev server

```sh
npm run serve
```

Removes the previously compiled files, recompiles the server in the `dist`
directory, and runs the server. Edits to files in the server will trigger
rebuilding and restarting the server.

### Compile for production

```sh
npm run build
```
