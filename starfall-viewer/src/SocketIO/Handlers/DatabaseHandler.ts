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

import ecef from 'starfall-common/ecef';

import EventDetailsSchema from 'starfall-common/Schemas/EventDetails';
import EventHistoryListSchema from 'starfall-common/Schemas/EventHistoryList';
import EventListItemSchema from 'starfall-common/Schemas/EventListItem';
import EventListSchema from 'starfall-common/Schemas/EventList';
import JsonValidator from 'starfall-common/JsonValidator';
import PlatformsSchema from 'starfall-common/Schemas/Platforms';
import PointSourceDetailsSchema from 'starfall-common/Schemas/PointSourceDetails';
import SensorListSchema from 'starfall-common/Schemas/SensorList';
import store from '@/store/index';
import { ACTIONS as EVENT_ACTIONS, MUTATIONS as EVENT_MUTATIONS } from '@/store/modules/EventModule';
import { MUTATIONS as SETTINGS_MUTATIONS } from '@/store/modules/SettingsModule';
import type { EventDetails } from '@/store/modules/EventModule';
import type { EventHistoryItem } from '@/types/EventHistoryItem';
import type { EventListItem } from 'starfall-common/Types/EventListItem';
import type { PointSource } from '@/types/PointSource';
import type { PointSourceFilterExtents } from 'starfall-common/Types/PointSourceFilterExtents';
import type { PageData } from 'starfall-common/Types/Paging';

export default class DataBaseHandler {
  public static processEvent(event: EventListItem): void {
    event.approx_trigger_time *= 1000;
    event.created_time *= 1000;
    event.last_update_time *= 1000;
    if (event.location_ecef_m !== null
      && event.location_ecef_m[0] !== null) {
      event.location_lat_lon_alt_m = ecef.unproject(event.location_ecef_m);
    } else {
      event.location_lat_lon_alt_m = null;
      event.location_ecef_m = null;
    }

    if (event.velocity_ecef_m_sec === null
      || event.velocity_ecef_m_sec[0] === null) {
      event.velocity_ecef_m_sec = null;
    }
  }

  public static processEventDetails(eventDetails: EventDetails): void {
    for (const sighting_id in eventDetails.sightings) {
      eventDetails.sightings[sighting_id].forEach((ps: PointSource) => {
        ps.time *= 1000;
      });
    }
  }

  public static onEventList(data: PageData): void {
    data.data.forEach((event) => DataBaseHandler.processEvent(event));
    if (JsonValidator.validate(data.data, EventListSchema)) {
      console.debug('received valid Event List');
    } else {
      console.error('received invalid Event List');
      return;
    }
    store.dispatch(EVENT_ACTIONS.SHOW_ALL_EVENTS);
    store.commit(EVENT_MUTATIONS.SET_EVENT_LIST, data);
  }

  public static onEventDetails(eventDetails: EventDetails): void {
    DataBaseHandler.processEventDetails(eventDetails);

    if (JsonValidator.validate(eventDetails, EventDetailsSchema)) {
      console.debug('received valid Event Details');
    } else {
      console.error('received invalid Event Details');
      return;
    }

    store.commit(EVENT_MUTATIONS.SET_EVENT_DETAILS, {
      eventDetails: eventDetails,
      selectedEventSummary: store.state.eventModule.selectedEventSummary
    });
    store.commit(SETTINGS_MUTATIONS.RESET_SENSOR_LINE);
  }

  public static onPointSourceDetails(pointSourceDetails: unknown): void {
    if (JsonValidator.validate(pointSourceDetails, PointSourceDetailsSchema)) {
      console.debug('received valid Point Source Details');
    } else {
      console.error('received invalid Point Source Details');
      // return;
    }

    store.commit(EVENT_MUTATIONS.SET_POINT_SOURCE_DETAILS, pointSourceDetails);
  }

  public static onEventHistory(eventHistory: EventHistoryItem[]): void {
    for (const entry of eventHistory) {
      entry.time *= 1000;
    }
    if (JsonValidator.validate(eventHistory, EventHistoryListSchema)) {
      console.debug('received valid Event History');
    } else {
      console.error('received invalid Event History');
      return;
    }
    // only update history if it matches the currently selected event
    const event_id = store.state.eventModule.selectedEventSummary?.event_id;
    if (event_id && eventHistory[0]?.event_id === event_id) {
      store.commit(EVENT_MUTATIONS.SET_EVENT_HISTORY, eventHistory);
    }
  }

  public static onAddUpdateEventSummary(event: EventListItem): void {
    DataBaseHandler.processEvent(event);

    if (JsonValidator.validate(event, EventListItemSchema)) {
      console.debug('received valid Event List Item');
    } else {
      console.error('received invalid Event List Item');
      return;
    }
    store.commit(EVENT_MUTATIONS.ADD_UPDATE_EVENT_SUMMARY, event);
  }

  public static onSensorsForEvent(data: any[]): void {
    if (JsonValidator.validate(data, SensorListSchema)) {
      console.debug('received valid Satellites');
    } else {
      console.error('received invalid Satellites');
      return;
    }
    store.commit(EVENT_MUTATIONS.SET_EVENT_PLATFORMS, data);
  }

  public static onDeleteEvent(eventId: string): void {
    if (typeof eventId === 'string') {
      console.debug('received valid delete event');
    } else {
      console.error('received invalid delete event');
      return;
    }
    store.dispatch(EVENT_ACTIONS.DELETE_EVENT, eventId);
  }

  public static onAllPlatforms(platforms: any[]): void {
    if (JsonValidator.validate(platforms, PlatformsSchema)) {
      console.debug('received valid All Platforms');
    } else {
      console.error('received invalid All Platforms');
    }
    store.commit(EVENT_MUTATIONS.SET_PLATFORMS, platforms);
  }

  public static onUpdateSightings(eventDetails: EventDetails): void {
    DataBaseHandler.processEventDetails(eventDetails);

    if (JsonValidator.validate(eventDetails, EventDetailsSchema)) {
      console.debug('received valid Updated Sightings');
    } else {
      console.error('received invalid Updated Sightings');
    }
    store.commit(EVENT_MUTATIONS.UPDATE_SIGHTINGS, { eventDetails });
  }

  public static onPointSourceFilterExtents(extents: PointSourceFilterExtents): void {
    extents.maxTime *= 1000;
    extents.minTime *= 1000;
    console.debug('received valid Point Source Filter Extents');
    store.commit(EVENT_MUTATIONS.SET_POINT_SOURCE_FILTER_EXTENTS, extents);
  }
}
