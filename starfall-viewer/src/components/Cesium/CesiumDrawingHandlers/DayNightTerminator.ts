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
import type { IDrawHandlerArgs } from './IDrawHandlerArgs';
import { Cartesian3, Color, Entity, JulianDate, Matrix3, PolylineGraphics, Quaternion, Viewer } from 'cesium';

const createPenumbraSunlightPolyline = () => new Entity({
  name: 'sunlight/penumbra polygon',
  polyline: {
    positions: Cartesian3.fromDegreesArray([
      0, 0,
      1, 0
    ]),
    width: 2,
    material: Color.YELLOW,
    show: true
  }
});

const createPenumbraUmbraPolyline = () => new Entity({
  name: 'sunlight/penumbra polygon',
  polyline: {
    positions: Cartesian3.fromDegreesArray([
      0, 0,
      1, 0
    ]),
    width: 2,
    material: Color.DARKGREY,
    show: true
  }
});

const penumbraSunlightPolyline = createPenumbraSunlightPolyline();
const penumbraUmbraPolyline = createPenumbraUmbraPolyline();

const penumbraVertexCount = 6;
const penumbraVertexRotation = 2 * Math.PI / penumbraVertexCount;
const simUpdateStep = 1; // update time step in seconds; will be scaled by clock multiplier
const sunRadius = 696.3; // mean radius in 10^6 meters
const earthRadius = 6.372797560856; // mean radius in 10^6 meters
let lastUpdateTime = new JulianDate(0, 0);

// https://github.com/CesiumGS/cesium/issues/4123
function updatePenumbraLines(viewer: Viewer, currentTime: JulianDate) {
  // updating too often brings cesium to a halt
  if (JulianDate.equalsEpsilon(lastUpdateTime, currentTime, Math.abs(viewer.clock.multiplier) * simUpdateStep)) { return; }
  // sun position
  const spwc = (viewer.scene as any).context.uniformState.sunPositionWC;
  const D = Cartesian3.magnitude(spwc) / 1000000.0; // distance from earth to sun in 10^6 meters
  if (D) { // prevent NaN errors
    lastUpdateTime = currentTime;
    const sv = Cartesian3.normalize(spwc, new Cartesian3());
    // vertex rotation
    const q = Quaternion.fromAxisAngle(sv, penumbraVertexRotation);
    const R = Matrix3.fromQuaternion(q);
    // sunlight line
    let angle = Math.acos((sunRadius + earthRadius) / D); // sunlight cone inner half-angle
    let v = new Cartesian3(0, 0, 1);
    Cartesian3.cross(sv, v, v); // get vector orthogonal to sv
    const qs = Quaternion.fromAxisAngle(v, angle);
    const Rs = Matrix3.fromQuaternion(qs);
    Matrix3.multiplyByVector(Rs, sv, v);
    let pos: Cartesian3[] = [];
    let w;
    for (let i = 0; i <= penumbraVertexCount; ++i) {
      Matrix3.multiplyByVector(R, v, v);
      w = Cartesian3.clone(v);
      viewer.scene.globe.ellipsoid.scaleToGeocentricSurface(w, w);
      pos.push(w);
    }
    ((penumbraSunlightPolyline as Entity).polyline as PolylineGraphics).positions = pos as unknown as any;
    // umbra line
    Cartesian3.negate(sv, sv); // umbra cone points away from sun
    angle = Math.acos((sunRadius - earthRadius) / D); // umbra cone inner half-angle
    v = new Cartesian3(0, 0, 1);
    Cartesian3.cross(sv, v, v); // get vector orthogonal to sv
    const qu = Quaternion.fromAxisAngle(v, angle);
    const Ru = Matrix3.fromQuaternion(qu);
    Matrix3.multiplyByVector(Ru, sv, v);
    pos = [];
    for (let i = 0; i <= penumbraVertexCount; ++i) {
      Matrix3.multiplyByVector(R, v, v);
      w = Cartesian3.clone(v);
      viewer.scene.globe.ellipsoid.scaleToGeocentricSurface(w, w);
      pos.push(w);
    }
    ((penumbraUmbraPolyline as Entity).polyline as PolylineGraphics).positions = pos as unknown as any;
    penumbraSunlightPolyline.show = true;
    penumbraUmbraPolyline.show = true;
  }
}

function init({ viewer }: IDrawHandlerArgs): void {
  viewer.entities.add(penumbraSunlightPolyline);
  viewer.entities.add(penumbraUmbraPolyline);
}

function onSelectedEvent({ viewer, payload }: IDrawHandlerArgs): void {
  const eventId = payload as string;
  const eventSummary = store.state.eventModule.eventList.data.find((event) => event.event_id === eventId);
  if (eventSummary === undefined) return;
  const currentTime = JulianDate.fromDate(new Date(eventSummary.approx_trigger_time));
  viewer.clock.currentTime = currentTime;
  viewer.scene.globe.enableLighting = true;

  // without this delay, the lines are not drawn in the right place
  setTimeout(
    () => updatePenumbraLines(viewer, currentTime)
  );
};

function clearViewer({ viewer }: IDrawHandlerArgs): void {
  viewer.scene.globe.enableLighting = false;
  penumbraSunlightPolyline.show = false;
  penumbraUmbraPolyline.show = false;
}

export default {
  [EVENT_MUTATIONS.INIT]: init,
  [EVENT_MUTATIONS.CLEAR_VIEWER]: clearViewer,
  [EVENT_MUTATIONS.SET_SELECTED_EVENT]: onSelectedEvent
};
