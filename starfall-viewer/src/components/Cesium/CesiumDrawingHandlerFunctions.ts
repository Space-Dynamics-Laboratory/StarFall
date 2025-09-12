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

import * as R from 'ramda';
import AllEventDrawHandler from './CesiumDrawingHandlers/AllEventDrawHandler';
import DayNightTerminator from './CesiumDrawingHandlers/DayNightTerminator';
import EventPathDrawHandler from './CesiumDrawingHandlers/EventPathDrawHandler';
import GlmDrawHandler from './CesiumDrawingHandlers/GlmDrawHandler';
import PlatformDrawHandler from './CesiumDrawingHandlers/PlatformDrawHandler';
import PointSourceHandler from './CesiumDrawingHandlers/PointSourceHandler';
import type { IDrawHandlerArgs } from './CesiumDrawingHandlers/IDrawHandlerArgs';

const handlers = [
  AllEventDrawHandler,
  DayNightTerminator,
  EventPathDrawHandler,
  GlmDrawHandler,
  PlatformDrawHandler,
  PointSourceHandler
];
const cesiumDrawingHandlerMap: Map<string, Array<(arg0: IDrawHandlerArgs) => void>> = new Map();

R.forEach((handler: any) => {
  R.forEachObjIndexed((value, key) => {
    if (cesiumDrawingHandlerMap.get(key as string)) {
      cesiumDrawingHandlerMap.get(key as string)!.push(value);
    } else {
      cesiumDrawingHandlerMap.set(key as string, [value]);
    }
  }, handler);
}, handlers);

/**
 * @param mutationType Type of mutation that was made.
 */
const cesiumDrawingHandlerFunctions = function(mutationType: string): (Array<(arg0: IDrawHandlerArgs) => void>) {
  // return empty list if mutation type is not in map
  return cesiumDrawingHandlerMap.get(mutationType) || [];
};

export default cesiumDrawingHandlerFunctions;
