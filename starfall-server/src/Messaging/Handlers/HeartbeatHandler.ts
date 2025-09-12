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
import version from 'starfall-common/dist/config/version';
import log from '../../log';
import topics from 'starfall-common/dist/topics';
import { IHandler } from './IHandler';

const setIntervalImmediately = (func: { (): void; (...args: any[]): void; }, interval: number | undefined): NodeJS.Timeout => {
  func();
  return setInterval(func, interval);
};

export default class HeartbeatHandler implements IHandler {
  private heartbeatInterval: NodeJS.Timeout | undefined;
  private server: ServerManager;
  private client: ClientManager;

  constructor(server: ServerManager, client: ClientManager) {
    log.debug('Heartbeat Handler Initializing');
    
    this.server = server;
    this.client = client;

    // send status updates to connected clients at the same interval
    // as querying new status but with a few seconds delay
    this.heartbeatInterval = setIntervalImmediately(
      this.heartbeat.bind(this),
      10 * 1000
    );
    
    log.info('Heartbeat Handler Initialized');
  }


  private heartbeat(): void {
    this.client.publish(topics.Heartbeat, { version });
  }
  
  public close(): void {
    log.debug('Heartbeat Handler Closing');

    if (this.heartbeatInterval !== undefined){
      clearInterval(this.heartbeatInterval);
    }

    log.info('Heartbeat Handler Closed');
  }
}

