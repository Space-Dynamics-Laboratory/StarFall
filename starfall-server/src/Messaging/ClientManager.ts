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

import SocketIO from 'socket.io';

import constants from './MessagingConstants';
import log from '../log';
import topics from 'starfall-common/dist/topics';
import { EventEmitter } from 'events';

/**
 * ClientManager
 *
 * Responsible for sending to and receiving from the connected clients. Uses
 * Socket.IO to publish and subscribe to topics
 *
 * @fires on {topic_name} for each topic received from the client
 */
export default class ClientManager extends EventEmitter {
  private io: SocketIO.Server;
  private activeRootPathClients: Map<string, SocketIO.Socket>;

  /**
   * @param server Https-Express-Server-App
   */
  constructor(server: Express.Application) {
    super();
    this.io = new SocketIO.Server(server);
    this.activeRootPathClients = new Map<string, SocketIO.Socket>();
    this.io.on(constants.CLIENT_CONNECT, (socket: SocketIO.Socket) => {
      log.info(`Socket.io connect: ${socket.id}`);
      
      this.activeRootPathClients.set(socket.id, socket);
      this.emit(constants.CLIENT_CONNECT, socket.id);

      socket.on(constants.CLIENT_DISCONNECT, () => {
        log.info(`Socket.io disconnect: ${socket.id}`);
        this.activeRootPathClients.delete(socket.id);
        this.emit(constants.CLIENT_DISCONNECT, socket.id);
      });

      socket.onAny((events, ...args) => {
        if (args.length > 1) {
          log.warn('socket.onAny received more arguements than expected');
        }
        this.emit(events, args[0], socket.id);
      });
    });
  }

  get socket(): SocketIO.Server {
    return this.io;
  }

  get clients(): Map<string, SocketIO.Socket> {
    return this.activeRootPathClients;
  }

  /**
   * @param topic topic to publish to the clients
   * @param data all serializable datastructures are supported, including Buffer
   * @param clientId the id of the client to publish to. null for all clients
   */
  publish(topic: string, data: any, clientId: string | null = null): void {
    if (clientId !== null) {
      log.debug(`Socket.io sending: ${topic} to ${clientId}`);
      this.activeRootPathClients.get(clientId)?.emit(topic, data);
    } else {
      for (const [socketId, client] of this.activeRootPathClients.entries()) {
        log.debug(`Socket.io sending: ${topic} to ${socketId}`);
        client.emit(topic, data);
      }
    }
  }

  /**
   * Popup a toast message on a web client
   * @param icon one of [success, warning, error, info, question]
   * @param title text to display in toast message
   * @param clientId which client to toast, null for all connected clients
   */
  toast(icon: string, title: string, clientId: string | null = null): void {
    this.publish(topics.Toast, {icon, title}, clientId);
  }

  sendMessage(type: string, obj: any): void {
    this.emit(type, obj);
  }

  close(): void {
    log.info('Closing Client Manager');
    this.io.close();
    this.activeRootPathClients.clear();
  }
}
