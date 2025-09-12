/*************************************************************************************************
* Licensed to the Apache Software Foundation (ASF) under one
* or more contributor license agreements.  See the NOTICE file
* distributed with this work for additional information
* regarding copyright ownership.  The ASF licenses this file
* to you under the Apache License, Version 2.0 (the
* "License"); you may not use this file except in compliance
* with the License.  You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing,
* software distributed under the License is distributed on an
* "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
* KIND, either express or implied.  See the License for the
* specific language governing permissions and limitations
* under the License.
**************************************************************************************************/

import convict from 'convict';
import path from 'path';

import { parse } from './ConfigParser';

const config = convict({
  nodeEnv: {
    format: ['production', 'development', 'test'],
    default: 'production',
    env: 'NODE_ENV'
  },
  energyThreshold: {
    format: Number,
    default: 0,
    env: 'ENERGY_THRESHOLD'
  },
  pointSourceColumnNames: {
    format: Object,
    default: {}
  },
  appHostname: {
    format: String,
    default: 'localhost',
    env: 'APP_IP_ADDRESS'
  },
  appPort: {
    format: Number,
    default: 8443,
    env: 'APP_PORT'
  },
  sslCert: {
    format: String,
    default: '',
    env: 'SSL_CERT'
  },
  sslKey: {
    format: String,
    default: '',
    env: 'SSL_KEY'
  },
  subConnection: {
    format: String,
    default: 'tcp://127.0.0.1:5556',
    env: 'SUB_CONNECTION'
  },
  dbUser: {
    format: String,
    default: 'starfall_admin',
    env: 'DB_USER'
  },
  dbHost: {
    format: String,
    default: 'database',
    env: 'DB_HOST'
  },
  dbDatabase: {
    format: String,
    default: 'starfall_database',
    env: 'DB_DATABASE'
  },
  dbPassword: {
    format: String,
    default: 'password',
    env: 'DB_PASSWORD'
  },
  dbPort: {
    format: 'port',
    default: 5432,
    env: 'DB_PORT'
  },
  logLevel: {
    format: ['error', 'warn', 'info', 'debug'],
    default: 'info',
    env: 'LOG_LEVEL'
  },
  logFile: {
    format: String,
    // default: '/var/log/starfall/starfall-server.log',
    default: '/opt/starfall/log/starfall-server.log',
    env: 'LOG_FILE'
  },
  mapTileServerURL: {
    format: String,
    default: ''
  },
  mapTileSetID: {
    format: String,
    default: ''
  },
  mapTileSetName: {
    format: String,
    default: ''
  },
  mapTileSetAttribution: {
    format: String,
    default: ''
  },
  viewerLogDir: {
    format: function check(dir: string) {
      if (typeof dir !== 'string')
        throw new Error('viewerLogDir must be a string');
      if (dir[dir.length - 1] !== '/')
        throw new Error('viewerLogDir must end with \'/\'');
    },
    // default: '/var/log/starfall/starfall-viewer',
    default: '/opt/StarFall/log/starfall-viewer/',
    env: 'VIEWER_LOG_DIR'
  },
  statusServers: {
    format: Object,
    default: {}
  },
  statusUpdateInterval: {
    format: Number,
    default: 30,
    env: 'STATUS_UPDATE_INTERVAL'
  },
  statusTimeoutDuration: {
    format: Number,
    default: 5,
    env: 'STATUS_TIMEOUT_DURATION'
  }
});

const env = config.get('nodeEnv');
const dir = env === 'production' ? '/etc/starfall' : './config';
const file = `starfall-viewer-server-${env}.config`;
export const filePath = path.resolve(__dirname, dir, file);
config.load(parse(filePath));
config.validate({ allowed: 'strict' });

export default config.getProperties();
