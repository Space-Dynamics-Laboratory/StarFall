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
/* eslint-disable @typescript-eslint/no-empty-function */

import * as R from 'ramda';
import Rainbow from 'rainbowvis.js';
// import Vue from 'vue';
import type { ActionContext, Module } from 'vuex';

import ExponentialGradient from '@/types/ExponentialGradient';
import type { EventHistoryItem } from '@/types/EventHistoryItem';
import type { Platform } from '@/types/Platform';
import type { PointSource } from '@/types/PointSource';
import type { RootState } from '@/types/RootState';
import type { Sensor } from '@/types/Sensor';
import type { PointSourceDetails } from '@/types/PointSourceDetails';
import ecef from 'starfall-common/ecef';
import { defaultFilter } from 'starfall-common/Types/EventFilter';
import type { EventFilter, SavedEventFilter } from 'starfall-common/Types/EventFilter';
import type { EventListItem } from 'starfall-common/Types/EventListItem';
import type { Platforms } from 'starfall-common/Types/Platforms';
import type { PointSourceFilterExtents } from 'starfall-common/Types/PointSourceFilterExtents';
import type { PageData } from 'starfall-common/Types/Paging';
import { ACTIONS as EVENT_ACTIONS } from './EventModule';
import { Scene, Viewer } from 'cesium';
import { Namespaces } from './Namespaces';

export type LightCurve = {
  title: string;
  sensor_id: number;
  x: number[];
  y: number[];
  y_label: string;
  y_units: string;
  type: number;
  triggerTimestamp: string;
};

export type EventDetails = {
  sightings: {
    [sightingId: string]: PointSource[];
  };
  lightCurves: {
    [sightingId: string]: LightCurve[];
  };
};

export type State = {
  event: EventDetails | null;
  selectedEventSummary: EventListItem | null;
  selectedPointSource: PointSourceDetails | null;
  eventFilter: EventFilter;
  eventList: PageData;
  savedEventFilterList: SavedEventFilter[];
  history: EventHistoryItem[];
  gradient: Rainbow;
  energyGradient: ExponentialGradient;
  hoveredId: string;
  detailView: boolean;
  lockedView: boolean;
  eventPlatforms: Platform[];
  platforms: Platforms;
  mainScene: Scene | null;
  markerSize: number;
  lineSize: number;
  pointSourceFilterExtents: PointSourceFilterExtents;
};

const state: State = {
  event: null,
  selectedEventSummary: null,
  selectedPointSource: null,
  eventFilter: defaultFilter,
  eventList: { data: [], pageNumber: -1, pageSize: -1, totalCount: -1, unviewed: -1, filteredCount: -1 },
  savedEventFilterList: [],
  gradient: new Rainbow(),
  energyGradient: new ExponentialGradient(),
  history: [],
  hoveredId: '',
  detailView: false,
  lockedView: false,
  eventPlatforms: [],
  platforms: [],
  mainScene: null,
  markerSize: 8,
  lineSize: 1,
  pointSourceFilterExtents: {
    minTime: 0,
    maxTime: Date.now(),
    minIntensity: 0,
    maxIntensity: 100,
    minClusterSize: 0,
    maxClusterSize: 99,
    tags: []
  }
};

const namespace = Namespaces.Event;

export const ACTIONS = {
  NEW_GLM_EVENT: namespace + 'NEW_GLM_EVENT',
  SHOW_ALL_EVENTS: namespace + 'SHOW_ALL_EVENTS',
  SET_EVENT_FILTER: namespace + 'SET_EVENT_FILTER',
  SELECT_EVENT: namespace + 'SELECT_EVENT',
  CLEAR_SELECTED_EVENT: namespace + 'CLEAR_SELECTED_EVENT',
  DELETE_EVENT: namespace + 'DELETE_EVENT'
};

export const MUTATIONS = {
  INIT: namespace + 'INIT',
  SET_EVENT_LIST: namespace + 'SET_EVENT_LIST',
  SET_EVENT_DETAILS: namespace + 'SET_EVENT_DETAILS',
  SET_POINT_SOURCE_DETAILS: namespace + 'SET_POINT_SOURCE_DETAILS',
  SHOW_ALL_EVENTS: namespace + 'SHOW_ALL_EVENTS',
  SET_HOVERED_EVENT: namespace + 'SET_HOVERED_EVENT',
  CLEAR_HOVERED_EVENT: namespace + 'CLEAR_HOVERED_EVENT',
  SET_EVENT_FILTER: namespace + 'SET_EVENT_FILTER',
  SET_EVENT_HISTORY: namespace + 'SET_EVENT_HISTORY',
  SET_SELECTED_EVENT: namespace + 'SET_SELECTED_EVENT',
  ADD_UPDATE_EVENT_SUMMARY: namespace + 'ADD_UPDATE_EVENT_SUMMARY',
  SAVE_EVENT_FILTER: namespace + 'SAVE_EVENT_FILTER',
  LOAD_EVENT_FILTER: namespace + 'LOAD_EVENT_FILTER',
  SET_EVENT_PLATFORMS: namespace + 'SET_EVENT_PLATFORMS',
  CLEAR_EVENT_PLATFORMS: namespace + 'CLEAR_EVENT_PLATFORMS',
  SET_PLATFORMS: namespace + 'SET_PLATFORMS',
  FLY_TO_PLATFORM: namespace + 'FLY_TO_PLATFORM',
  SHOW_HIDE_PLATFORM: namespace + 'SHOW_HIDE_PLATFORM',
  SHOW_HIDE_FOV: namespace + 'SHOW_HIDE_FOV',
  STORE_SCENE: namespace + 'STORE_SCENE',
  CLEAR_SELECTED_EVENT: namespace + 'CLEAR_SELECTED_EVENT',
  SET_LOCKED_VIEW: namespace + 'SET_LOCKED_VIEW',
  CLEAR_VIEWER: namespace + 'CLEAR_VIEWER',
  LOCK_VIEW: namespace + 'LOCK_VIEW',
  UNLOCK_VIEW: namespace + 'UNLOCK_VIEW',
  FLY_HOME: namespace + 'FLY_HOME',
  UPDATE_SIGHTINGS: namespace + 'UPDATE_SIGHTINGS',
  SET_POINT_SOURCE_FILTER_EXTENTS: namespace + 'SET_POINT_SOURCE_FILTER_EXTENTS'
};

export const GETTERS = {
  FULL_EVENT_LIST: namespace + 'FULL_EVENT_LIST',
  SINGLE_EVENT_BY_ID: namespace + 'SINGLE_EVENT_BY_ID',
  MICROSERVICE_CHAIN_STATUS: namespace + 'MICROSERVICE_CHAIN_STATUS',
  MICROSERVICE_STATUS: namespace + 'MICROSERVICE_STATUS',
  MICROSERVICE_STATUS_HELPER: namespace + 'MICROSERVICE_STATUS_HELPER',
  LOG_STATUS: namespace + 'LOG_STATUS',
  LOG_STATUS_HELPER: namespace + 'LOG_STATUS_HELPER',
  UNVIEWED_COUNT: namespace + 'UNVIEWED_COUNT',
  EVENT_FILTER: namespace + 'EVENT_FILTER'
};

type Context = ActionContext<State, RootState>;

const actions = {
  [ACTIONS.SHOW_ALL_EVENTS](context: Context): void {
    context.dispatch(ACTIONS.CLEAR_SELECTED_EVENT);
    context.commit(MUTATIONS.SET_POINT_SOURCE_DETAILS, null);
    context.commit(MUTATIONS.CLEAR_HOVERED_EVENT);
    context.commit(MUTATIONS.SHOW_ALL_EVENTS, { events: context.getters[GETTERS.FULL_EVENT_LIST] });
  },
  [ACTIONS.SET_EVENT_FILTER](context: Context, filter: EventFilter): void {
    context.commit(MUTATIONS.SET_EVENT_FILTER, filter);
    if (!state.detailView) {
      context.commit(MUTATIONS.SHOW_ALL_EVENTS, {
        events: context.getters[GETTERS.FULL_EVENT_LIST],
        flyHome: false
      });
    }
  },
  [ACTIONS.SELECT_EVENT](context: Context, eventId: string): void {
    context.dispatch(ACTIONS.CLEAR_SELECTED_EVENT);
    context.commit(MUTATIONS.SET_SELECTED_EVENT, eventId);
  },
  [ACTIONS.CLEAR_SELECTED_EVENT](context: Context): void {
    context.commit(MUTATIONS.CLEAR_SELECTED_EVENT);
    context.commit(MUTATIONS.CLEAR_EVENT_PLATFORMS);
  },
  [ACTIONS.DELETE_EVENT](context: Context, eventId: string): void {
    const idx = context.getters[GETTERS.FULL_EVENT_LIST].data.findIndex((event) => event.event_id === eventId);
    if (idx === undefined) {
      console.warn(`delete event: event does not exist ${eventId}`);
      return;
    }
    state.eventList.data.splice(idx, 1);
    context.dispatch(EVENT_ACTIONS.SHOW_ALL_EVENTS);
  }
};

const mutations = {
  [MUTATIONS.INIT](state: State): void {
    state.gradient.setSpectrum('#3d26a8', '#2e81f9', '#3ed28d', '#f8ba3d', '#f9fa14');
    state.energyGradient.setSpectrum('#283c64', '#0b69a6', '#3094a5', '#adbd5f', '#f2c338', '#f2a038', '#eb6e30', '#d91e1e');
  },
  [MUTATIONS.SET_EVENT_LIST](state: State, payload: PageData): void {
    state.eventList = payload;
  },
  [MUTATIONS.SET_EVENT_DETAILS](state: State, payload: { eventDetails: EventDetails, selectedEventSummary: EventListItem }): void {
    state.detailView = true;
    state.event = payload.eventDetails;
  },
  [MUTATIONS.SET_POINT_SOURCE_DETAILS](state: State, payload: PointSourceDetails): void {
    state.selectedPointSource = payload;
  },
  [MUTATIONS.SET_EVENT_FILTER](state: State, filter: EventFilter): void {
    state.eventFilter = filter;
  },
  [MUTATIONS.SET_EVENT_HISTORY](state: State, payload: EventHistoryItem[]): void {
    state.history = payload;
  },
  [MUTATIONS.SHOW_ALL_EVENTS](): void {
    state.detailView = false;
  },
  [MUTATIONS.SET_HOVERED_EVENT](state: State, payload: string): void {
    state.hoveredId = payload;
  },
  [MUTATIONS.CLEAR_HOVERED_EVENT](state: State): void {
    state.hoveredId = '';
  },
  [MUTATIONS.SET_SELECTED_EVENT](state: State, event_id: string): void {
    const eventSummary = state.eventList.data.find((event) => event.event_id === event_id);
    if (eventSummary === undefined) {
      console.warn(`set selected event: no event ${event_id}`);
      return;
    }
    state.selectedEventSummary = eventSummary;
  },
  [MUTATIONS.ADD_UPDATE_EVENT_SUMMARY](state: State, newEvent: EventListItem): void {
    const idx = state.eventList.data.findIndex((event) => event.event_id === newEvent.event_id);
    if (idx >= 0) {
      state.eventList.data[idx] = newEvent;
    } else {
      state.eventList.data = [newEvent, ...state.eventList.data];
    }
    if (state.selectedEventSummary?.event_id === newEvent.event_id) {
      state.selectedEventSummary = newEvent;
    }
  },
  [MUTATIONS.SAVE_EVENT_FILTER](state: State, name: string): void {
    const filter = { name, ...R.clone(state.eventFilter) };
    state.savedEventFilterList.push(filter);
  },
  [MUTATIONS.LOAD_EVENT_FILTER](state: State, index: number): void {
    state.eventFilter = R.clone(state.savedEventFilterList[index]);
  },
  [MUTATIONS.SET_EVENT_PLATFORMS](state: State, data: any[]): void {
    const result: Platform[] = [];
    for (const row of data) {
      const platform = result.find((platform) => platform.id === row.platform_id)
        || (result[result.length] = {
          id: row.platform_id,
          name: row.platform_name,
          posEcef: row.pos_ecef_m,
          posLatLonAlt: row.pos_ecef_m ? ecef.unproject(row.pos_ecef_m) : null,
          sensors: [] as Sensor[]
        });

      // update platform location if it is null from creation
      if (platform.posLatLonAlt === null && row.pos_ecef_m !== null) {
        platform.posLatLonAlt = ecef.unproject(row.pos_ecef_m);
      }

      const s : Sensor = {
        id: row.sensor_id,
        name: row.sensor_name,
        type: row.sensor_type,
        fov: row.fov
      };

      // prevent duplicate sensors getting pushed to a platform
      if (!platform.sensors.some(sensor => sensor.id === s.id)) {
        platform.sensors.push(s);
      }
    }

    state.eventPlatforms = result;
  },
  [MUTATIONS.SET_PLATFORMS](state: State, data: Platforms): void {
    state.platforms = data;
  },
  [MUTATIONS.CLEAR_SELECTED_EVENT](state: State): void {
    state.event = null;
    state.selectedEventSummary = null;
    state.history = [];
  },
  [MUTATIONS.CLEAR_EVENT_PLATFORMS](state: State): void {
    state.eventPlatforms = [];
  },
  [MUTATIONS.FLY_TO_PLATFORM](): void {},
  [MUTATIONS.SHOW_HIDE_PLATFORM](): void {},
  [MUTATIONS.SHOW_HIDE_FOV](): void {},
  [MUTATIONS.STORE_SCENE](state: State, viewer: Viewer): void {
    state.mainScene = viewer.scene;
  },
  [MUTATIONS.SET_POINT_SOURCE_FILTER_EXTENTS](state: State, extents: PointSourceFilterExtents): void {
    state.pointSourceFilterExtents = extents;
  },
  [MUTATIONS.UPDATE_SIGHTINGS](state: State, payload: { eventDetails: EventDetails }): void {
    if (state.event) {
      state.event.sightings = payload.eventDetails.sightings;
    }
  },
  [MUTATIONS.SET_LOCKED_VIEW](state: State, value: boolean): void {
    state.lockedView = value;
  },
  [MUTATIONS.CLEAR_VIEWER](): void {},
  [MUTATIONS.LOCK_VIEW](): void {},
  [MUTATIONS.UNLOCK_VIEW](): void {},
  [MUTATIONS.FLY_HOME](): void {}
};

const getters = {
  [GETTERS.FULL_EVENT_LIST]: (state: State): PageData => {
    return state.eventList;
  },

  eventHistory: function(state: State): EventHistoryItem[] {
    return state.history;
  },

  [GETTERS.SINGLE_EVENT_BY_ID]: (state: State): (eventId: string) => EventListItem | undefined => {
    return (eventId: string) => state.eventList.data.find((event) => event.event_id === eventId);
  },

  [GETTERS.UNVIEWED_COUNT]: (state: State): number => {
    return state.eventList.data.reduce((acc: number, cur: EventListItem) => acc + (cur.user_viewed ? 0 : 1), 0);
  },

  [GETTERS.EVENT_FILTER]: (state: State): EventFilter => {
    return state.eventFilter;
  }
};

export default {
  state,
  actions,
  mutations,
  getters
} as Module<State, RootState>;
