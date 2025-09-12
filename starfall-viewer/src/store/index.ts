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

import { createStore } from 'vuex'

import eventModule from './modules/EventModule';
import globalModule from './modules/GlobalModule';
import microserviceStatusModule from './modules/MicroserviceStatusModule';
import settingsModule from './modules/SettingsModule';
import popupModule from './modules/PopupsModule';
import messageModule from './modules/MessageModule';

const store = createStore({
  modules: {
    eventModule,
    globalModule,
    microserviceStatusModule,
    settingsModule,
    popupModule,
    messageModule
    // TODO: double check circular dependency
    // messageModule is registered in main.ts to avoid circular dependencies
  }
})

export default store;
