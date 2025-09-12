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

FROM node:22.11.0-bookworm-slim AS node
# FROM node:22.11.0-alpine AS node
RUN corepack enable
RUN apt-get update && apt-get install -y git

COPY ./starfall-common /starfall-common
WORKDIR /starfall-common

RUN npm install
RUN npm run build

FROM postgis/postgis:16-3.4
# FROM postgis/postgis:16-3.4-alpine
# PostgreSQL with PostGIS installed
# Also comes with postgis_topology, fuzzystrmatch, and postgis_tiger_geocoder
# https://github.com/postgis/docker-postgis

USER root

# Install Node into the final image (no apt/curl needed)
COPY --from=node /usr/local/ /opt/node/
ENV PATH="${PATH}:/opt/node/bin"

# # Optional: verify versions
RUN node -v
RUN npm -v 
RUN corepack --version

# # Install all the db init scripts
COPY ./starfall-database/startup_scripts /docker-entrypoint-initdb.d
COPY --from=node /starfall-common /starfall-common
RUN chown --recursive postgres:postgres /docker-entrypoint-initdb.d

# When switching images you will have to change group and owner permissions of the docker volume
# Debian `id -u postgres` ==> 70
# Alpine `id -u postgres` ==> 999
USER postgres
