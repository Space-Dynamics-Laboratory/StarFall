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

FROM node:12.20.1 as server_builder
LABEL Description="StarFall server builder"
# Setup environment
# Install apt packages
RUN cat /etc/os-release
RUN apt-get update --yes --quiet

RUN apt-get install --yes --quiet \
    wget build-essential libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev

WORKDIR /tmp
RUN wget https://www.python.org/ftp/python/3.9.4/Python-3.9.4.tgz
RUN tar xzf Python-3.9.4.tgz \
    && cd Python-3.9.4 \
    && ./configure --enable-optimizations \
    && make install

RUN apt-get install --yes --quiet \
      libnetcdf-dev \
    && apt-get clean --yes --quiet \
    && rm -rf /var/lib/apt/lists/*
RUN npm i -g npm@6.14.10
# Import code
COPY ./starfall-common /workspace/starfall-common
COPY ./starfall-server /workspace/starfall-server
# Build
WORKDIR /workspace/starfall-common
RUN npm i
WORKDIR /workspace/starfall-server
RUN npm i && npm run build


FROM node:12.20.1 as gui_builder
LABEL Description="StarFall viewer builder"
RUN npm i -g npm@6.14.10
# Install git
RUN apt-get update --yes --quiet \
    && apt-get install --yes --quiet \
    git
# Import code
COPY ./.git /workspace/.git
COPY ./starfall-common /workspace/starfall-common
COPY ./starfall-viewer /workspace/starfall-viewer
# Build
WORKDIR /workspace/starfall-common
RUN npm i
WORKDIR /workspace/starfall-viewer
RUN npm i && npm run build


FROM node:12.20.1 as production
LABEL Description="StarFall production server"
# Setup environment
# Install apt packages
RUN npm i -g npm@6.14.10
#COPY --from=server_builder /usr/bin/python /usr/bin/python
RUN apt-get update --yes --quiet \
    && apt-get install --yes --quiet \
      libnetcdf-dev \
    && apt-get clean --yes --quiet \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
RUN wget https://www.python.org/ftp/python/3.9.4/Python-3.9.4.tgz
RUN tar xzf Python-3.9.4.tgz \
    && cd Python-3.9.4 \
    && ./configure --enable-optimizations \
    && make install

RUN apt-get install --yes --quiet \
      libnetcdf-dev \
    && apt-get clean --yes --quiet \
    && rm -rf /var/lib/apt/lists/*
# Copy code
COPY --from=server_builder /workspace/starfall-common /workspace/starfall-common
COPY --from=server_builder /workspace/starfall-server/package*json /workspace/starfall-server/
COPY --from=server_builder /workspace/starfall-server/dist /workspace/starfall-server/dist
COPY --from=gui_builder /workspace/starfall-viewer/dist /workspace/starfall-viewer/dist
COPY ./starfall-server/src/config/starfall-viewer-server-production.config /etc/starfall/starfall-viewer-server-production.config
# Run
WORKDIR /workspace/starfall-server
RUN npm i --omit=dev
CMD [ "npm", "run", "prod-serve" ]
