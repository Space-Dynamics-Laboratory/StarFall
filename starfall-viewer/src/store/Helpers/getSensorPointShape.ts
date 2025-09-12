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
import { MUTATIONS as SETTINGS_MUTATIONS, GETTERS as SETTINGS_GETTERS, PointShape } from '@/store/modules/SettingsModule';
import type { SensorPointShape } from '@/store/modules/SettingsModule'

export const getSensorPointShape = (sensorId: number): PointShape => {
  const shape = store.getters[SETTINGS_GETTERS.GET_SENSOR_POINT_SHAPE](sensorId);
  if (shape !== undefined) return shape;

  const newShape = PointShape.circle;
  store.commit(
    SETTINGS_MUTATIONS.PUSH_SENSOR_POINT_SHAPE_LIST,
    { id: sensorId, shape: newShape } as SensorPointShape
  );
  return newShape;
};
