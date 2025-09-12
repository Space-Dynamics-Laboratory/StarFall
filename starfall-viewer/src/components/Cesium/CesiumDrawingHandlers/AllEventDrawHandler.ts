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
import { Cartesian3, Color, PointPrimitiveCollection, PointPrimitive } from 'cesium';
import type { EventListItem } from 'starfall-common/Types/EventListItem';
import { GETTERS as EVENT_GETTERS, MUTATIONS as EVENT_MUTATIONS, ACTIONS as EVENT_ACTIONS } from '@/store/modules/EventModule';
import type { IDrawHandlerArgs } from './IDrawHandlerArgs';
import type { PageData } from 'starfall-common/Types/Paging';

function createPointPrimitive(event: EventListItem) {
  if (event.location_ecef_m === null) return undefined;
  const energy = event.approx_energy_j !== null ? event.approx_energy_j : 0;
  return {
    id: event.event_id,
    position: Cartesian3.fromArray(event.location_ecef_m),
    pixelSize: 10,
    color: Color.fromCssColorString(`#${store.state.eventModule.energyGradient.colorAt(energy || 0)}`),
    outlineWidth: 0.5,
    outlineColor: Color.fromCssColorString('#BEBEBE')
  };
};

function drawAllEvents({ viewer, payload, collections }: IDrawHandlerArgs): void {
  store.commit(EVENT_MUTATIONS.CLEAR_VIEWER);
  // store.dispatch(EVENT_ACTIONS.CLEAR_SELECTED_EVENT);
  const { events, flyHome = true } = payload as { events: PageData, flyHome: boolean };

  const fullEventList: EventListItem[] = store.getters[EVENT_GETTERS.FULL_EVENT_LIST].data;
  let minEnergy = Number.MAX_VALUE;
  let maxEnergy = Number.MIN_VALUE;
  for (const event of fullEventList) {
    if (event.approx_energy_j !== null) {
      minEnergy = Math.min(minEnergy, event.approx_energy_j);
      maxEnergy = Math.max(maxEnergy, event.approx_energy_j);
    }
  }
  store.state.eventModule.energyGradient.setNumberRange(minEnergy, maxEnergy);
  store.state.eventModule.energyGradient.setNumberOfColors(events.data.length);

  events.data.forEach((event) => {
    const options = createPointPrimitive(event);
    if (options) {
      collections.allEventPoints.add(options);
    }
  });
  if (flyHome) viewer.camera.flyHome(2);
};

function getById(collection: PointPrimitiveCollection, id: string): PointPrimitive | undefined {
  for (let i = 0; i < collection.length; ++i) {
    if (collection.get(i).id === id) {
      return collection.get(i);
    }
  }
  return undefined;
}

function highlightEvent({ collections, payload }: IDrawHandlerArgs): void {
  const eventId: string = payload;
  if (store.state.eventModule.detailView) return;
  const hoveredEntity = getById(collections.allEventPoints, eventId);
  if (hoveredEntity) {
    hoveredEntity.pixelSize = 15;
    hoveredEntity.color = Color.WHITE;
    hoveredEntity.outlineWidth = 0.6;
  }
};

const clearHighlightedEvent = function({ collections, payload }: IDrawHandlerArgs): void {
  const eventId: string = payload;
  const hoveredEntity = getById(collections.allEventPoints, eventId);
  const event = store.getters[EVENT_GETTERS.SINGLE_EVENT_BY_ID](eventId);
  if (hoveredEntity && event) {
    const options = createPointPrimitive(event);
    if (options) {
      hoveredEntity.pixelSize = options.pixelSize;
      hoveredEntity.color = options.color;
      hoveredEntity.outlineWidth = options.outlineWidth;
    }
  }
};

function clearViewer({ collections }: IDrawHandlerArgs): void {
  collections.allEventPoints.removeAll();
}

export default {
  [EVENT_MUTATIONS.CLEAR_HOVERED_EVENT]: clearHighlightedEvent,
  [EVENT_MUTATIONS.CLEAR_VIEWER]: clearViewer,
  [EVENT_MUTATIONS.SET_HOVERED_EVENT]: highlightEvent,
  [EVENT_MUTATIONS.SHOW_ALL_EVENTS]: drawAllEvents
};
