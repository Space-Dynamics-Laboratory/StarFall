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

import DatabaseHandler from './Handlers/DatabaseHandler';
import EventHandler from './Handlers/EventHandler';
import HeartbeatHandler from './Handlers/HeartbeatHandler';
import MessageHandler from './Handlers/MessageHandler';
import { io } from 'socket.io-client';
import topics from 'starfall-common/topics';

type Handler = (msg: any) => void;
export default class SocketIOManager {
  private io;
  private topicHandlerMap: Map<string, Handler>;

  constructor() {
    this.io = io({
      transports: ['websocket']
    });
    this.topicHandlerMap = new Map();
    this.topicHandlerMap.set(topics.EventList, DatabaseHandler.onEventList);
    this.topicHandlerMap.set(topics.EventDetails, DatabaseHandler.onEventDetails);
    this.topicHandlerMap.set(topics.PointSourceDetails, DatabaseHandler.onPointSourceDetails);
    this.topicHandlerMap.set(topics.EventHistory, DatabaseHandler.onEventHistory);
    this.topicHandlerMap.set(topics.AddUpdateEventSummary, DatabaseHandler.onAddUpdateEventSummary);
    this.topicHandlerMap.set(topics.SensorsForEvent, DatabaseHandler.onSensorsForEvent);
    this.topicHandlerMap.set(topics.DeleteEvent, DatabaseHandler.onDeleteEvent);
    this.topicHandlerMap.set(topics.AllPlatforms, DatabaseHandler.onAllPlatforms);
    this.topicHandlerMap.set(topics.UpdateSightings, DatabaseHandler.onUpdateSightings);
    this.topicHandlerMap.set(topics.PointSourceFilterExtents, DatabaseHandler.onPointSourceFilterExtents);
    this.topicHandlerMap.set(topics.NewEventStart, EventHandler.onNewEventStart);
    this.topicHandlerMap.set(topics.NewEventFinish, EventHandler.onNewEventFinish);
    this.topicHandlerMap.set(topics.Toast, MessageHandler.onToast);
    this.topicHandlerMap.set(topics.UpdateStatus, MessageHandler.onUpdateStatus);
    this.topicHandlerMap.set(topics.Heartbeat, HeartbeatHandler.onHeartbeat);

    this.topicHandlerMap.forEach((handle: Handler, topic: string) => {
      this.io.on(topic, (msg: any): void => {
        handle(msg);
      });
    });
  }

  public emit(event: string, ...args: any[]): void {
    this.io.emit(event, ...args);
  }
}
