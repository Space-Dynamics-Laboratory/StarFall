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
import { MUTATIONS as SETTINGS_MUTATIONS, GETTERS as SETTINGS_GETTERS } from '@/store/modules/SettingsModule';
import type { SensorLine } from '@/store/modules/SettingsModule';

export const getSensorLine = (sensorId: number): boolean => {
  const line = store.getters[SETTINGS_GETTERS.GET_SENSOR_LINE](sensorId);
  if (line !== undefined) {
    return line;
  } else {
    // MUTATION: Init the sensor line if it doesn't exist
    store.commit(
      SETTINGS_MUTATIONS.PUSH_SENSOR_LINE_LIST,
      { id: sensorId, line: true } as SensorLine
    );
    return true;
  }
};
