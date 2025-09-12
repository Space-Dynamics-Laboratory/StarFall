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

import { ArcType, Color, PolylineArrowMaterialProperty, Cartesian3, Entity, PolylineDashMaterialProperty, Viewer } from 'cesium';
import type { EventListItem } from 'starfall-common/Types/EventListItem';
import type { IDrawHandlerArgs } from './IDrawHandlerArgs';
import { MUTATIONS as EVENT_MUTATIONS } from '@/store/modules/EventModule';

const color = '#e8670c';
let velocityVectorA: Entity | null = null;
let velocityVectorB: Entity | null = null;
let eventSphere: Entity | null = null;

function drawEventDetailsWithVelocity(viewer: Viewer, event: EventListItem) {
  if (event.location_ecef_m === null || event.velocity_ecef_m_sec === null) return;

  const eventLocation = new Cartesian3(event.location_ecef_m[0], event.location_ecef_m[1], event.location_ecef_m[2]);
  const velocity = Cartesian3.fromArray(event.velocity_ecef_m_sec);
  const velocityNorm = Cartesian3.normalize(velocity, new Cartesian3());

  if (velocityVectorA !== null || velocityVectorB !== null) console.warn('velocity vector was not cleared');

  const scaleFactor = 5e4;

  const start = Cartesian3.add(
    Cartesian3.multiplyByScalar(velocityNorm, -scaleFactor, new Cartesian3()),
    eventLocation,
    new Cartesian3()
  );

  const end = Cartesian3.add(
    Cartesian3.multiplyByScalar(velocityNorm, scaleFactor, new Cartesian3()),
    eventLocation,
    new Cartesian3()
  );

  velocityVectorA = viewer.entities.add({
    polyline: {
      positions: [start, eventLocation],
      width: 20,
      material: new PolylineArrowMaterialProperty(Color.fromCssColorString(color)),
      arcType: ArcType.NONE
    }
  });

  velocityVectorB = viewer.entities.add({
    polyline: {
      positions: [eventLocation, end],
      width: 3,
      material: new PolylineDashMaterialProperty({
        color: Color.fromCssColorString(color)
      }),
      arcType: ArcType.NONE
    }
  });
}

function drawEventDetailsWithoutVelocity(viewer: Viewer, event: EventListItem) {
  if (event.location_ecef_m === null) return;
  const eventLoc = new Cartesian3(event.location_ecef_m[0], event.location_ecef_m[1], event.location_ecef_m[2]);
  if (eventSphere !== null) console.warn('event sphere was not cleared');
  const radius = 3000;
  eventSphere = viewer.entities.add({
    position: eventLoc,
    ellipsoid: {
      radii: new Cartesian3(radius, radius, radius),
      material: Color.fromCssColorString(color)
    }
  });
}

function drawEventDetails({ viewer, payload }: IDrawHandlerArgs): void {
  const event: EventListItem = payload.selectedEventSummary;
  if (event.location_lat_lon_alt_m === null || event.location_ecef_m === null) return;

  if (event.velocity_ecef_m_sec !== null
    && event.velocity_ecef_m_sec[0] !== 0
    && event.velocity_ecef_m_sec[1] !== 0
    && event.velocity_ecef_m_sec[2] !== 0) {
    drawEventDetailsWithVelocity(viewer, event);
  } else {
    drawEventDetailsWithoutVelocity(viewer, event);
  }
};

const removeEntity = (viewer: Viewer, entity: Entity|null) => {
  if (entity !== null) {
    viewer.entities.removeById(entity.id);
  }
};

function clearViewer({ viewer }: IDrawHandlerArgs): void {
  removeEntity(viewer, velocityVectorA);
  velocityVectorA = null;
  removeEntity(viewer, velocityVectorB);
  velocityVectorB = null;
  removeEntity(viewer, eventSphere);
  eventSphere = null;
};

export default {
  [EVENT_MUTATIONS.SET_EVENT_DETAILS]: drawEventDetails,
  [EVENT_MUTATIONS.CLEAR_VIEWER]: clearViewer
};
