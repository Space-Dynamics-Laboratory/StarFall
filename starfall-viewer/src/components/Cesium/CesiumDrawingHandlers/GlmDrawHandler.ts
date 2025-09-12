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
import store from '@/store';
import { Cartesian3, HeadingPitchRange, JulianDate, BoundingSphere } from 'cesium';
import type { EventListItem } from 'starfall-common/Types/EventListItem';
import { MUTATIONS as EVENT_MUTATIONS } from '@/store/modules/EventModule';
import type { Platform } from '@/types/Platform';

const lookAtEvent = function(stayCloseToEarth: boolean, { viewer, payload }: IDrawHandlerArgs): void {
  const eventSummary: EventListItem = payload;
  if (eventSummary?.location_lat_lon_alt_m === null) {
    flyHome({ viewer } as IDrawHandlerArgs);
    return;
  }

  const [lat, lon, alt] = eventSummary.location_lat_lon_alt_m;

  viewer.camera.flyToBoundingSphere(new BoundingSphere(Cartesian3.fromDegrees(lon, lat, alt), 1e5), {
    duration: 1,
    maximumHeight: stayCloseToEarth ? 1000000 : undefined,
    complete: () => {
      const start = Cartesian3.fromDegrees(lon, lat, alt);
      viewer.camera.constrainedAxis = Cartesian3.UNIT_Z;

      const heading = new HeadingPitchRange(viewer.camera.heading, viewer.camera.pitch, 3e5);
      viewer.camera.lookAt(start, heading);
    }
  });
  store.state.eventModule.lockedView = true;
};

const flyToEvent = lookAtEvent.bind(null, true);
const returnToEvent = lookAtEvent.bind(null, true);

const drawEventDetails = function({ viewer, payload, collections }: IDrawHandlerArgs): void {
  const selectedEventSummary: EventListItem = payload.selectedEventSummary;

  if (store.state.settingsModule.zoomToEvent) {
    flyToEvent({ viewer: viewer, payload: selectedEventSummary, collections });
  }
};

const unlockView = function({ viewer }: IDrawHandlerArgs): void {
  store.state.eventModule.lockedView = false;
  viewer.camera.flyHome();
  viewer.camera.cancelFlight();
};

const flyHome = function({ viewer }: IDrawHandlerArgs): void {
  store.state.eventModule.lockedView = false;
  viewer.camera.flyHome();
};

function movePointAwayFromEarth(point: Cartesian3, distance: number): Cartesian3 {
  // Calculate the magnitude of the point vector
  const norm = Math.sqrt(point.x ** 2 + point.y ** 2 + point.z ** 2);

  if (norm === 0) {
    console.error("The point is at the Earth's center, cannot determine a radial direction.");
    return point
  }

  // Determine the unit vector in the direction of the point
  const unitVector = {
    x: point.x / norm,
    y: point.y / norm,
    z: point.z / norm
  };

  // Move the point further away by adding the scaled unit vector
  return new Cartesian3(
    point.x + unitVector.x * distance,
    point.y + unitVector.y * distance,
    point.z + unitVector.z * distance
  );
}

const flyToPlatform = function({ viewer, payload }: IDrawHandlerArgs): void {
  const platform: Platform = payload;
  const entity = viewer.entities.getById(String(platform.id));
  const position = entity?.position?.getValue(JulianDate.now());

  if (position) {
    const newPosition = movePointAwayFromEarth(position, 15e6)
    viewer.camera.flyTo({
      destination: newPosition,
      duration: 1,
      convert: false
    });
  }
};

export default {
  [EVENT_MUTATIONS.SET_EVENT_DETAILS]: drawEventDetails,
  [EVENT_MUTATIONS.LOCK_VIEW]: returnToEvent,
  [EVENT_MUTATIONS.UNLOCK_VIEW]: unlockView,
  [EVENT_MUTATIONS.FLY_HOME]: flyHome,
  [EVENT_MUTATIONS.FLY_TO_PLATFORM]: flyToPlatform
};
