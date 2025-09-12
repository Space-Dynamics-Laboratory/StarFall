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

import store from '@/store';
import { MUTATIONS as EVENT_MUTATIONS } from '@/store/modules/EventModule';
import { MUTATIONS as POPUP_MUTATIONS } from '@/store/modules/PopupsModule';
import type { EventListItem } from 'starfall-common/Types/EventListItem';
import DataBaseHandler from './DatabaseHandler';

export default class EventHandler {
  public static onNewEventStart(message: EventListItem): void {
    DataBaseHandler.processEvent(message);
    store.commit(EVENT_MUTATIONS.ADD_UPDATE_EVENT_SUMMARY, message);
  };

  public static onNewEventFinish(message: EventListItem): void {
    DataBaseHandler.processEvent(message);
    store.commit(EVENT_MUTATIONS.ADD_UPDATE_EVENT_SUMMARY, message);
    if (store.state.settingsModule.alertOnlyIfAboveEnergyThreshold) {
      if (message.approx_energy_j !== null && message.approx_energy_j >= store.state.settingsModule.energyThreshold) {
        store.commit(POPUP_MUTATIONS.CREATE_EVENT_ALERT_POPUP, { eventSummary: message });
      }
    } else {
      store.commit(POPUP_MUTATIONS.CREATE_EVENT_ALERT_POPUP, { eventSummary: message });
    }
  };
}
