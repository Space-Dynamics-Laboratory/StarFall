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

import config from './config';
import express from 'express';
import fs from 'fs';
import https from 'https';
import http from 'http';
import { EventEmitter } from 'events';
import path from 'path';
import routes from './routes';

export const EventsManager = new EventEmitter();
export const app = express();

const contentSecurityHeader = `
  default-src 'self';
  img-src 'self' data: blob:;
  script-src 'self' 'unsafe-eval' 'unsafe-inline' https://dev.virtualearth.net https://dev.virtualearth.net;
  style-src 'self' 'unsafe-inline';
  connect-src *;
`.replace(/(?:\r\n|\r|\n)/g, '');
app.use(function(req, res, next) {
  res.setHeader('Content-Security-Policy', contentSecurityHeader);
  return next();
});

app.use(
  express.static(
    path.join(__dirname, '../../starfall-viewer/dist')
  )
);

app.use('/api', routes);

let serverApp;
if (config.sslKey !== '' && config.sslCert !== '') {
  const options = {
    key: fs.readFileSync(config.sslKey),
    cert: fs.readFileSync(config.sslCert),
    // I think this should only need to be turned off
    // for development with self signed certs
    // false in development, true otherwise
    rejectUnauthorized: config.nodeEnv != 'development'
  };
  serverApp = https.createServer(options, app);

} else {
  serverApp = http.createServer(app);
}

export const server = serverApp;