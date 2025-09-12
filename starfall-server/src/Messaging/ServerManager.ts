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

import * as zmq from 'zeromq';

import log from '../log';
import { safeJSONParse } from '../helpers/json-object-service';
import { EventEmitter } from 'events';

/**
 * ServerManager
 * 
 * Responsible for communicating with the chain.
 */
export default class ServerManager extends EventEmitter {
  private subSocket: zmq.Subscriber;
  private subConnection: string;

  constructor(subConnection: string) {
    super();
    this.subSocket = new zmq.Subscriber();
    this.subConnection = subConnection;
  }

  async init(): Promise<string> {
    return new Promise((res, _) => {
      this.subSocket.connect(this.subConnection);
      this.subSocket.subscribe();
      res(`ZMQ sub socket connected to: ${this.subConnection}`);
    });
  }

  async listen(): Promise<void> {
    for await (const [topic_buf, msg_buf] of this.subSocket) {
      if (msg_buf === undefined) {
        const raw = topic_buf.toString('utf8').split(',');
        const topic = raw[0];
        const msg = raw[1];
        const payload = safeJSONParse(msg);
        if (payload) {
          this.emit(topic, payload);
        } else {
          log.error(`invalid message received: ${topic}, ${msg}`);
        }
      }
      else {
        const payload = safeJSONParse(msg_buf.toString('utf8'));
        if (payload) {
          this.emit(topic_buf.toString('utf8'), payload);
        } else {
          log.error(`invalid message received: ${topic_buf.toString('utf8')}, ${msg_buf.toString('utf8')}`);
        }
      }
    }
  }

  close(): void {
    log.debug('Server Manager Closing');

    this.subSocket.close();

    log.info('Server Manager Closed');
  }
}
