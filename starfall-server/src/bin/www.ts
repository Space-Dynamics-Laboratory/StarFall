#!/usr/bin/env node

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

import MessageRouter from '../Messaging/MessageRouter';
import 'dotenv/config';
import { app, server } from '../app';
import config from '../config';
import log from '../log';

log.info(JSON.stringify(config, null, '  '));

const messageRouter = new MessageRouter(server, config);
server.listen(config.appPort);
server.on('error', onError);
server.on('listening', onListening);

// var debug = require('debug')('web-server:server')

/**
 * Event listener for HTTP server "error" event.
 */
function onError(error: any) {
  if (error.syscall !== 'listen') {
    throw error;
  }

  const bind = 'port ' + config.appPort;

  // handle specific listen errors with friendly messages
  switch (error.code) {
  case 'EACCES':
    // eslint-disable-next-line no-console
    log.error(bind + ' requires elevated privileges');
    process.exit(1);
  // eslint-disable-next-line no-fallthrough
  case 'EADDRINUSE':
    // eslint-disable-next-line no-console
    log.error(bind + ' is already in use');
    process.exit(1);
  // eslint-disable-next-line no-fallthrough
  default:
    throw error;
  }
}

/**
 * Event listener for HTTP server "listening" event.
 */
function onListening() {
  const addr = server.address();
  const bind = typeof addr === 'string' ? `pipe ${addr}` : `${addr!.address}:${addr!.port}`;
  log.info('Listening on ' + bind);
};

/**
 * clean up on exit
 */
process.on('SIGINT', async function() {
  log.info('\nShutting Down...');
  await messageRouter.close();
  server.close();
  process.exit(0);
});
