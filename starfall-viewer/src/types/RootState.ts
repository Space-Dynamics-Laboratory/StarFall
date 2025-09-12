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

import type { State as EventState } from '@/store/modules/EventModule';
import type { State as GlobalState } from '@/store/modules/GlobalModule';
import type { State as MessageState } from '@/store/modules/MessageModule';
import type { State as SettingsState } from '@/store/modules/SettingsModule';
import type { State as MicroserviceStatusModule } from '@/store/modules/MicroserviceStatusModule';
import type { State as PopupState } from '@/store/modules/PopupsModule';

export type RootState = {
  eventModule: EventState;
  global: GlobalState;
  messageModule: MessageState;
  microserviceStatusModule: MicroserviceStatusModule;
  settingsModule: SettingsState;
  popupModule: PopupState;
};
