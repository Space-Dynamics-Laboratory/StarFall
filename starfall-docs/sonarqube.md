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
# SonarQube

SonarQube® is an automatic code review tool to detect bugs, vulnerabilities and code smells in your code. [https://docs.sonarqube.org/latest/](https://docs.sonarqube.org/latest/)

## SonarQube Server

The first part of SonarQube is the server which can be installed as a docker container.

```sh
docker pull sonarqube:lts
docker run -d --name sonarqube -p 9000:9000 sonarqube:lts
```

There is a `docker-compose.yml` in `/sonarqube` to bring a server container up

Once the container is running you can navigate to `localhost:9000` to access it. The default username and password are `admin`. You will need to generate an access token to authenticate scans.

## Sonar Scanner

`sonar-scanner` is the program that scans the code and it communicates with the SonarQube server to store and display scan results. To install sonar-scanner follow the steps below.

```sh
cd /opt
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.3.0.2102-linux.zip
unzip sonar-scanner-cli-4.3.0.2102-linux.zip
rm sonar-scanner-cli-4.3.0.2102-linux.zip
ln -s /opt/sonar-scanner-4.3.0.2102-linux/bin/sonar-scanner /usr/bin/sonar-scanner
```

If you are running the server and scanner on the same machine follow the steps below to get them talking on the same network

```sh
docker network create my-net
docker network connect my-net sonarcube
docker network connect my-net <devcontainer>
docker network inspect my-net
```

Note the sonarqube ip address for running sonar-scanner

## Run sonar-scanner

Navigate to the root of a project (ex. `cd starfall/starfall-viewer`)

Fill in the \<tags\> with your information

```sh
NODE_PATH=./node_modules sonar-scanner \
  -Dsonar.projectKey=<project name> \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://<sonar server ip>:9000 \
  -Dsonar.login=<token>
```

## Misc

If you need to run commands in the SonarQube as root, you can get a root shell

```sh
docker exec -u 0 -it <container name> bash
```
