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

import { createLogger, format, Logger, transports } from 'winston';

import ClientManager from '@/Messaging/ClientManager';
import ServerManager from '@/Messaging/ServerManager';
import config from '../../config';
import constants from '../MessagingConstants';
import log from '../../log';
import topics from 'starfall-common/dist/topics';
import { IHandler } from './IHandler';

export default class LogHandler implements IHandler {
  private loggers: Map<string, Logger>;
  private client: ClientManager;

  constructor(server: ServerManager, client: ClientManager) {
    log.debug('Log Handler Initializing');

    this.client = client;
    this.loggers = new Map<string, Logger>();

    client.on(constants.CLIENT_DISCONNECT, (clientId: string) => {
      this.loggers.delete(clientId);
    });
  
    client.on(topics.SaveViewerLog, (message: string, clientId: string) => {
      if(!this.loggers.has(clientId)) {
        this.addLogger(clientId);
      }
      this.loggers.get(clientId)?.info(clientId + ' ' + message);
    });
  
    log.info('Log Handler Initialized');
  };
  
  private addLogger(clientId: string): void {
    const socket = this.client.clients.get(clientId);
    let ip: null | string = null;
    if (socket !== undefined) {
      ip = socket.handshake.address.substring(7);
    }

    this.loggers.set(
      clientId,
      LogHandler.buildLogger(`${config.viewerLogDir}${ip?ip:clientId}.log`)
    );
  }
    
  static buildLogger(filePath: string): Logger {
    return createLogger ({
      format: format.printf((info) => {
        return info.message;
      }),
      transports: [
        new transports.File({filename: filePath})
      ]
    });
  }

  public close(): void {
    log.debug('Log Handler Closing');
    this.loggers.clear();
    log.info('Log Handler Closed');
  }
}
