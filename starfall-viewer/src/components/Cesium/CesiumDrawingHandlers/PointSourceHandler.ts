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

import type { IDrawHandlerArgs } from './IDrawHandlerArgs';
import { MUTATIONS as EVENT_MUTATIONS } from '@/store/modules/EventModule';
import type { EventDetails } from '@/store/modules/EventModule';
import { MUTATIONS as SETTINGS_MUTATIONS } from '@/store/modules/SettingsModule';
import { Cartesian3, Color, Material, Polyline, PolylineCollection } from 'cesium';
import { getSensorColor } from '@/store/Helpers/getSensorColor';
import { getSensorLine } from '@/store/Helpers/getSensorLine';
import type { PointSourceDetails } from '@/types/PointSourceDetails';

type options = {
  show: boolean,
  positions: Cartesian3[];
  width: number;
  material: Material;
  id: string;
};

const pointSourcePrimitives: Polyline[] = [];
let selectedPointSourcePrimitiveIndex = -1;
let currentEvent: EventDetails | undefined;
function getPointSourcePrimitives(event: EventDetails) {
  const pointSources: options[] = [];

  Object.values(event.sightings).forEach(sighting => {
    if (sighting.length === 0) return;

    for (const ps of sighting) {
      const material = Material.fromType('Color', {
        color: getSensorColor(ps.sensor_id)
      });
      const points = [
        Cartesian3.fromArray(ps.meas_far_point_ecef_m),
        Cartesian3.fromArray(ps.meas_near_point_ecef_m)
      ];
      pointSources.push({
        show: getSensorLine(ps.sensor_id),
        positions: points,
        width: 3,
        material: material,
        id: ps.point_source_id
      });
    }
  });

  return pointSources;
}

function addPointSources(primitives: options[], collection: PolylineCollection): void {
  for (let i = 0; i < primitives.length; ++i) {
    pointSourcePrimitives.push(collection.add(primitives[i]));
  }
}

function removePointSources(collection: PolylineCollection): void {
  for (let i = 0; i < pointSourcePrimitives.length; ++i) {
    collection.remove(pointSourcePrimitives[i]);
  }
  pointSourcePrimitives.length = 0;
};

function removePointSource(pointSourcePrimitivesIndex: number, collection: PolylineCollection): void {
  collection.remove(pointSourcePrimitives[pointSourcePrimitivesIndex]);
  pointSourcePrimitives.splice(pointSourcePrimitivesIndex, 1);
};

const clear = function({ collections }: IDrawHandlerArgs): void {
  removePointSources(collections.pointsourcePolylines);
  currentEvent = undefined;
};

const drawPointSources = function({ viewer, payload, collections }: IDrawHandlerArgs): void {
  const event: EventDetails = payload.eventDetails;
  currentEvent = event;
  const primitives = getPointSourcePrimitives(event);
  removePointSources(collections.pointsourcePolylines);
  addPointSources(primitives, collections.pointsourcePolylines);
};

function getSelectedPointSourcePrimitive(point: PointSourceDetails) {
  const points = [
    Cartesian3.fromArray(point.meas_far_point_ecef_m),
    Cartesian3.fromArray(point.meas_near_point_ecef_m)
  ];
  const pointSources: options[] = [];
  pointSources.push({
    show: true,
    positions: points,
    width: 6,
    material: Material.fromType('Color', {
      color: Color.CRIMSON
    }),
    id: point.point_source_id
  });
  return pointSources;
}

const selectPointSource = function({ payload, collections }: IDrawHandlerArgs): void {
  const point: PointSourceDetails = payload;
  if (selectedPointSourcePrimitiveIndex > -1) {
    removePointSource(selectedPointSourcePrimitiveIndex, collections.pointsourcePolylines);
    selectedPointSourcePrimitiveIndex = -1;
  }
  if (point) {
    const primitives = getSelectedPointSourcePrimitive(point);
    selectedPointSourcePrimitiveIndex = pointSourcePrimitives.length;
    addPointSources(primitives, collections.pointsourcePolylines);
  }
};

const updatePointSource = function({ payload, collections }: IDrawHandlerArgs): void {
  if (currentEvent !== undefined) {
    const primitives = getPointSourcePrimitives(currentEvent);
    removePointSources(collections.pointsourcePolylines);
    addPointSources(primitives, collections.pointsourcePolylines);
  }
};

export default {
  [EVENT_MUTATIONS.SET_EVENT_DETAILS]: drawPointSources,
  [EVENT_MUTATIONS.UPDATE_SIGHTINGS]: drawPointSources,
  [EVENT_MUTATIONS.CLEAR_VIEWER]: clear,
  [EVENT_MUTATIONS.SET_POINT_SOURCE_DETAILS]: selectPointSource,
  [SETTINGS_MUTATIONS.SET_SENSOR_COLOR]: updatePointSource,
  [SETTINGS_MUTATIONS.SET_SENSOR_LINE]: updatePointSource
};
