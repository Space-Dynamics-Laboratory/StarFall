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

import ClientManager from '@/Messaging/ClientManager';
import ServerManager from '@/Messaging/ServerManager';
import log from '../../log';
import topics from 'starfall-common/dist/topics';
import { IHandler } from './IHandler';

export default class ChainHandler implements IHandler {
  constructor(server: ServerManager, client: ClientManager) {
    log.debug('Chain Handler Initializing');

    server.on(topics.NewEventStart, (payload: any) => {
      log.info(`Chain Handler received ${topics.NewEventStart}`);
      client.emit(topics.NewEventStart, payload);
    });

    server.on(topics.NewEventFinish, (payload: any) => {
      log.info(`Chain Handler received ${topics.NewEventFinish}`);
      client.emit(topics.NewEventFinish, payload);
    });

    log.info('Chain Handler Initialized');
  }

  public close(): void {
    log.debug('Chain Handler Closing');
    log.info('Chain Handler closed');
  }
}
