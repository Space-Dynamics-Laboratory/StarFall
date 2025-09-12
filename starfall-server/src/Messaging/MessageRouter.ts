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

import ClientManager from './ClientManager';
import ServerManager from './ServerManager';
import log from '../log';

// Import and add all handlers to the list
import ChainHandler from './Handlers/ChainHandler';
import DataBaseHandler from './Handlers/DataBaseHandler';
import HeartbeatHandler from './Handlers/HeartbeatHandler';
import LogHandler from './Handlers/LogHandler';
import StatusHandler from './Handlers/StatusHandler';
const eventHandlerTypes = [ChainHandler, DataBaseHandler, HeartbeatHandler, LogHandler, StatusHandler];

export default class MessageRouter {
  private clientManager: ClientManager;
  private serverManager: ServerManager;
  private handlers: any[];

  /**
   * @param server Http-Express-Server-App
   * @param config configuration parameters
   */
  constructor(server: Express.Application, config: any) {
    this.handlers = [];
    this.clientManager = new ClientManager(server);
    this.serverManager = new ServerManager(config.subConnection);
    
    // const handlerHelper = new handlerHelper(this.serverManager, this.clientManager);
    // const subscriptionHandler = new SubscriptionHandler(handlerHelper);

    this.serverManager.init()
      .then((msg: string) => {
        log.info(msg);
        for (const handler of eventHandlerTypes) {
          this.handlers.push(new handler(this.serverManager, this.clientManager));
        }
        this.serverManager.listen();
      })
      .catch(err => {
        log.error('Error occurred initializing Server Manager');
        log.error(err.message);
      });
  }

  async close(): Promise<void> {
    log.debug('Message Router Closing');

    for (const handler of this.handlers) {
      if (typeof handler.close == 'function') {
        await handler.close();
      }
    }
    this.serverManager.close();
    this.clientManager.close();
    this.handlers.length = 0;

    log.info('Message Router Closed');
  }
}