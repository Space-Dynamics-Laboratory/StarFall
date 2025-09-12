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
import { getSensorColor } from '@/store/Helpers/getSensorColor';
import { MUTATIONS as EVENT_MUTATIONS } from '@/store/modules/EventModule';
import { MUTATIONS as SETTINGS_MUTATIONS } from '@/store/modules/SettingsModule';
import type { Platform } from '@/types/Platform';
import type { Sensor } from '@/types/Sensor';
import { ConstantProperty, Cartesian3, Color, ColorBlendMode, ColorMaterialProperty, ConstantPositionProperty, Entity, Viewer, Math as CMath } from 'cesium';
import type { IDrawHandlerArgs } from './IDrawHandlerArgs';

const platforms: Record<string, Entity> = {};
const fovs: Entity[] = [];

function createPlatformModel({ viewer, payload }: IDrawHandlerArgs): Entity {
  const id = String(payload);
  if (id in platforms) {
    viewer.entities.removeById(id);
    console.warn('platform already exists');
  }
  const sat = new Entity({
    show: false,
    id: id,
    model: {
      uri: 'CloudSat.glb',
      scale: 1300000,
      color: Color.WHITE,
      colorBlendMode: ColorBlendMode.MIX,
      colorBlendAmount: 0.5
    }
  });
  return viewer.entities.add(sat);
};

function createFovFootprint(viewer: Viewer, platform: Platform, sensor: Sensor): Entity | null {
  if (sensor.fov === null
  || platform.posLatLonAlt === null
  || platform.posEcef == null) {
    return null;
  }

  const th = CMath.toRadians(sensor.fov / 2);
  const alt = platform.posLatLonAlt[2];
  const diameter = 2 * alt * Math.tan(th);
  const color = getSensorColor(sensor.id);
  const fov = viewer.entities.add({
    id: `fov_${sensor.id}`,
    position: Cartesian3.fromDegrees(platform.posLatLonAlt[1], platform.posLatLonAlt[0]),
    show: false,
    ellipse: {
      semiMajorAxis: diameter,
      semiMinorAxis: diameter,
      height: 0,
      material: color,
      outline: true,
      granularity: 0.003
    }
  });

  return fov;
}

const preparePlatformsAndFovs = function({ viewer, collections }: IDrawHandlerArgs): void {
  const event_platforms = store.state.eventModule.eventPlatforms;

  event_platforms.forEach((platform) => {
    if (platform.id in platforms) return;
    platforms[platform.id] = createPlatformModel({ viewer: viewer, payload: platform.id, collections });
  });

  event_platforms.forEach((platform) => {
    const entity: Entity | undefined = platforms[platform.id];
    if (!entity) return;
    if (!platform.posEcef) return;
    entity.position = new ConstantPositionProperty(Cartesian3.fromArray(platform.posEcef));
    entity.show = false;
    let color = Color.fromRgba(0x646464FF);
    platform.sensors.forEach((sensor) => {
      const fov = createFovFootprint(viewer, platform, sensor);
      if (fov === null) return;
      fovs.push(fov);
      color = getSensorColor(sensor.id);
    });

    // TODO: how do we color satellite models that have multiple sensors onboard?
    if (entity.model && platform.sensors.length === 1) {
      entity.model.color = new ConstantProperty(color.withAlpha(1));
    }
  });
};

const showHidePlatform = function({ viewer, payload }: IDrawHandlerArgs): void {
  const { platform, show }: { platform: Platform; show: boolean; } = payload;

  const platformEntity = platforms[String(platform.id)];
  if (platformEntity === undefined) {
    console.warn(`no platform entity ${platform.id}`);
    return;
  }

  platformEntity.show = show;
};

const showHideFov = function({ viewer, payload }: IDrawHandlerArgs): void {
  const { sensor, platform, showPlatform }: { showPlatform: boolean; sensor: Sensor; platform: Platform; } = payload;

  const platformEntity = platforms[String(platform.id)];
  if (platformEntity === undefined) {
    console.warn(`no platform entity ${platform.id}`);
    return;
  }

  const fovEntity = viewer.entities.getById(`fov_${sensor.id}`);
  if (fovEntity === undefined) {
    console.warn(`no fov entity fov_${sensor.id}`);
    return;
  }
  if (fovEntity.ellipse) {
    fovEntity.ellipse.material = new ColorMaterialProperty(getSensorColor(sensor.id));
  }
  fovEntity.show = !fovEntity.show;
};

const updateFovColor = function({ viewer, payload }: IDrawHandlerArgs): void {
  const fovEntity = viewer.entities.getById(`fov_${payload.id}`);
  if (fovEntity && fovEntity.show && fovEntity.ellipse) {
    fovEntity.show = false;
    fovEntity.ellipse.material = new ColorMaterialProperty(getSensorColor(payload.id));
    fovEntity.show = true;
  }
};

function clearViewer({ viewer }: IDrawHandlerArgs): void {
  Object.values(platforms).forEach(entity => { entity.show = false; });
  fovs.forEach(fov => viewer.entities.remove(fov));
}

export default {
  [EVENT_MUTATIONS.CLEAR_VIEWER]: clearViewer,
  [EVENT_MUTATIONS.SET_EVENT_PLATFORMS]: preparePlatformsAndFovs,
  [EVENT_MUTATIONS.SHOW_HIDE_PLATFORM]: showHidePlatform,
  [EVENT_MUTATIONS.SHOW_HIDE_FOV]: showHideFov,
  [SETTINGS_MUTATIONS.SET_SENSOR_COLOR]: updateFovColor
};
