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

FROM redhat/ubi8 AS build

LABEL \
  description="StarFall GLM Trigger RH8 UBI Image" \
  vendor="Space Dynamics Laboratory"

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# Update system packages
RUN set -eux; \
  yum update --assumeyes --quiet; \
  yum install --assumeyes --quiet \
  unzip \
  git \
  bash-completion \
  vim \
  sudo \
  wget; \
  yum clean all --assumeyes --quiet;

# Download protobuf-compile NOTE: If updated, also change the version in starfall.
WORKDIR /opt
ARG PROTO_VERSION=29.3
RUN set -eux; \
  wget https://github.com/protocolbuffers/protobuf/releases/download/v${PROTO_VERSION}/protoc-${PROTO_VERSION}-linux-x86_64.zip; \
  unzip protoc-${PROTO_VERSION}-linux-x86_64.zip -d protoc-${PROTO_VERSION};

# Add developer user
ARG USER=developer
ARG UID=1000
RUN set -eux; \
  mkdir -p /home/$USER; \
  groupadd --gid $UID $USER; \
  adduser --shell $(which bash) --uid $UID --gid $UID --home /home/$USER $USER; \
  echo "$USER ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers; \
  chown $USER:$USER /home/$USER;

# Create the non-root user working directory
ENV HOME=/home/$USER
ENV WORKSPACE=$HOME/glmtriggergen
WORKDIR ${WORKSPACE}

# Copy over the other necessary files
COPY ./lib/conda_envs/unclass_prod_env_py3117.yml ./unclass_prod_env_py3117.yml
RUN chown -R developer:developer .

# Switch to our non-root user
USER $UID

# Set miniconda environment variables
ARG CONDA_VERSION="py311_25.1.1-2"
ARG MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-${CONDA_VERSION}-Linux-x86_64.sh"
ARG SHA256SUM="d8c1645776c0758214e4191c605abe5878002051316bd423f2b14b22d6cb4251"
ARG CONDA_INSTALL_DIR="${HOME}/miniconda3"

RUN set -eux; \
  # Install, check the sha256sum, and cleanup
  mkdir -p $CONDA_INSTALL_DIR; \
  wget $MINICONDA_URL -O $CONDA_INSTALL_DIR/miniconda.sh; \
  echo "${SHA256SUM} ${CONDA_INSTALL_DIR}/miniconda.sh" > $CONDA_INSTALL_DIR/shasum; \
  sha256sum --check $CONDA_INSTALL_DIR/shasum; \
  bash $CONDA_INSTALL_DIR/miniconda.sh -b -u -p $CONDA_INSTALL_DIR; \
  rm -rf $CONDA_INSTALL_DIR/miniconda.sh $CONDA_INSTALL_DIR/shasum;

# Add conda to path
ENV PATH="${CONDA_INSTALL_DIR}/bin:${PATH}"

# Initialize all shells to use conda environments
RUN set -eux; \
  source $CONDA_INSTALL_DIR/bin/activate; \
  conda init --all

# Copy environment yaml file over and create the python environment
ARG CONDA_ENV_PREFIX="py3117"
# Create the conda env
RUN conda env create -n $CONDA_ENV_PREFIX -f ./unclass_prod_env_py3117.yml --solver=libmamba

# Install conda-pack:
RUN conda install -c conda-forge conda-pack

# Use conda-pack to create a standalone enviornment
# in /venv:
RUN conda-pack -n py3117 -o /tmp/env.tar && \
  mkdir ${WORKSPACE}/venv && cd ${WORKSPACE}/venv && \
  tar xf /tmp/env.tar && rm /tmp/env.tar

# We've put venv in same path it'll be in final image,
# so now fix up paths:
RUN ${WORKSPACE}/venv/bin/conda-unpack



FROM redhat/ubi8 AS production

ARG PROTO_VERSION=29.3
COPY --from=build /opt/protoc-${PROTO_VERSION} /opt/
RUN ln -s /opt/protoc-${PROTO_VERSION}/bin/protoc /usr/local/bin/protoc

# Add developer user
# Defaulted for Windows developers,
# Linux developers can override in devcontainer.json build.args
ARG USER=developer
ARG UID=1000
RUN set -eux; \
  mkdir -p /home/$USER; \
  groupadd --gid $UID $USER; \
  adduser --shell $(which bash) --uid $UID --gid $UID --home /home/$USER $USER; \
  echo "$USER ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers; \
  chown $USER:$USER /home/$USER;

# Create the non-root user working directory
ENV HOME=/home/$USER
ENV WORKSPACE=$HOME/glmtriggergen
WORKDIR ${WORKSPACE}

# Copy /venv from the previous stage:
COPY --from=build ${WORKSPACE}/venv /venv

# Copy over the other necessary files
COPY . .
RUN chown -R developer:developer .

# Switch to our non-root user
USER $UID

# Set the ENV variables for the Conda environment
ENV FONTCONFIG_PATH=/venv/etc/fonts
ENV FONTCONFIG_FILE=/venv/etc/fonts/fonts.conf
ENV PATH="/venv/bin:$PATH"
ENV CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1
