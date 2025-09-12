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

FROM redhat/ubi8

LABEL \
    description="StarFall RH8 UBI Dev container" \
    vendor="Space Dynamics Laboratory" \
    version="1.0"


# add RHEL 8 EPEL repo
RUN dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm

# Install yum packages
RUN set -eux; \
    yum update --assumeyes --quiet; \
    yum install --assumeyes --quiet \
    unzip \
    wget \
    vim \
    xz \
    git \
    python39 \
    gcc \
    gcc-c++ \
    make \
    cmake \
    rpm-build \
    ;

# Clear out caches to reduce contianer size
RUN yum clean all --assumeyes --quiet

# Install and configure node.js
ARG NODE_VERSION=22.11.0
WORKDIR /opt/
RUN set -eux; \
    curl --location --remote-name --silent https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.xz; \
    tar --extract --file=node-v${NODE_VERSION}-linux-x64.tar.xz; \
    rm /opt/node-v${NODE_VERSION}-linux-x64.tar.xz; \
    ln -s /opt/node-v${NODE_VERSION}-linux-x64/ /opt/node;
ENV PATH "$PATH:/opt/node-v${NODE_VERSION}-linux-x64/bin"

# TODO: Upgrade protobuf
# ARG PROTO_VERSION=29.3
ARG PROTO_VERSION=3.15.8
RUN set -eux; \
    wget https://github.com/protocolbuffers/protobuf/releases/download/v${PROTO_VERSION}/protoc-${PROTO_VERSION}-linux-x86_64.zip; \
    unzip protoc-${PROTO_VERSION}-linux-x86_64.zip -d protoc-${PROTO_VERSION}; \
    ln -s /opt/protoc-${PROTO_VERSION}/bin/protoc /usr/local/bin/protoc;

RUN git config --global --add safe.directory /workspace

RUN mkdir /var/log/starfall

CMD [ "/bin/bash", "-c", "echo \"DevContainer started. Idling...\" && sleep infinity" ]
