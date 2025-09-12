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

import type { Module, ActionContext } from 'vuex';
import type { RootState } from '@/types/RootState';
import { Namespaces } from './Namespaces';
import { Color } from 'cesium';
import type { MicroserviceDetailsLogFilter } from '@/types/MicroserviceDetailsLogFilter';
import { getSensorColor } from '@/store/Helpers/getSensorColor';

export type SensorColor = {
  id: number,
  color: Color
};

export enum PointShape {
  circle = 'circle',
  square = 'square',
  diamond = 'diamond',
  triangle = 'triangle',
  down_triangle = 'down_triangle',
  left_triangle = 'left_triangle',
  right_triangle = 'right_triangle',
  plus = 'plus',
  times = 'times',
  vertical_line = 'vertical_line',
  horizontal_line = 'horizontal_line'
}

export type SensorPointShape = {
  id: number,
  shape: PointShape
};

export type SensorLine = {
  id: number,
  line: boolean
};

export type State = {
  zoomToEvent: boolean;
  flashingScreen: boolean;
  voiceAlertSetting: boolean;
  sensorColorList: SensorColor[];
  sensorPointShapeList: SensorPointShape[];
  sensorLineList: SensorLine[];
  microserviceDetailsLogFilter: MicroserviceDetailsLogFilter;
  eventAlertInterval: number;
  alertOnlyIfAboveEnergyThreshold: boolean;
  nEventsPerPage: number;
  maxLogsPerService: number;
  energyThreshold: number;
};

const defaultState: State = {
  zoomToEvent: true,
  flashingScreen: true,
  voiceAlertSetting: true,
  alertOnlyIfAboveEnergyThreshold: true,
  sensorColorList: [],
  sensorPointShapeList: [],
  sensorLineList: [],
  microserviceDetailsLogFilter: {
    debug: true,
    info: true,
    warning: true,
    error: true
  },
  eventAlertInterval: 60,
  nEventsPerPage: 50,
  maxLogsPerService: 1000,
  energyThreshold: 0
};

const state: State = JSON.parse(JSON.stringify(defaultState));

const namespace = Namespaces.Settings;

export const ACTIONS = {
  SET_ENERGY_THRESHOLD: namespace + 'SET_ENERGY_THRESHOLD'
};

export const MUTATIONS = {
  INIT: namespace + 'INIT',
  RESET: namespace + 'RESET',
  TOGGLE_ZOOM_TO_EVENT: namespace + 'TOGGLE_ZOOM_TO_EVENT',
  TOGGLE_FLASHING_SCREEN: namespace + 'TOGGLE_FLASHING_SCREEN',
  TOGGLE_VOICE_ALERT: namespace + 'TOGGLE_VOICE_ALERT',
  TOGGLE_ALERT_ONLY_IF_ABOVE_ENERGY_THRESHOLD: namespace + 'TOGGLE_ALERT_ONLY_IF_ABOVE_ENERGY_THRESHOLD',
  PUSH_SENSOR_COLOR_LIST: namespace + 'PUSH_SENSOR_COLOR_LIST',
  SET_SENSOR_COLOR: namespace + 'SET_SENSOR_COLOR',
  PUSH_SENSOR_POINT_SHAPE_LIST: namespace + 'PUSH_SENSOR_POINT_SHAPE_LIST',
  SET_SENSOR_POINT_SHAPE: namespace + 'SET_SENSOR_POINT_SHAPE',
  PUSH_SENSOR_LINE_LIST: namespace + 'PUSH_SENSOR_LINE_LIST',
  SET_SENSOR_LINE: namespace + 'SET_SENSOR_LINE',
  RESET_SENSOR_LINE: namespace + 'RESET_SENSOR_LINE',
  SET_MICROSERVICE_DETAILS_LOG_FILTER: namespace + 'SET_MICROSERVICE_DETAILS_LOG_FILTER',
  SET_ALERT_INTERVAL: namespace + 'SET_ALERT_INTERVAL',
  SET_N_EVENTS_PER_PAGE: namespace + 'SET_N_EVENTS_PER_PAGE',
  SET_MAX_LOGS_PER_SERVICE: namespace + 'SET_MAX_LOGS_PER_SERVICE',
  SET_ENERGY_THRESHOLD: namespace + 'SET_ENERGY_THRESHOLD'
};

export const GETTERS = {
  GET_SENSOR_COLOR: namespace + 'GET_SENSOR_COLOR',
  GET_SENSOR_POINT_SHAPE: namespace + 'GET_POINT_SHAPE',
  GET_SENSOR_LINE: namespace + 'GET_SENSOR_LINE'
};

type Context = ActionContext<State, RootState>;

const actions = {
  [ACTIONS.SET_ENERGY_THRESHOLD](context: Context, threshold: number): void {
    context.commit(MUTATIONS.SET_ENERGY_THRESHOLD, threshold);
  }
};

const mutations = {
  [MUTATIONS.INIT]: (state: State) => {
    const settings = localStorage.getItem('settings');
    if (settings) {
      Object.assign(state, JSON.parse(settings) as State);
    }
    for (const item of state.sensorColorList) {
      item.color = Color.fromBytes(item.color.red * 255, item.color.green * 255, item.color.blue * 255, item.color.alpha * 255);
    }
  },
  [MUTATIONS.RESET]: (state: State): void => {
    const newColorsList: SensorColor[] = state.sensorColorList.slice();
    Object.assign(state, defaultState);
    localStorage.setItem('settings', JSON.stringify(state));
    newColorsList.forEach(sensor => {
      getSensorColor(sensor.id);
    });
  },
  [MUTATIONS.TOGGLE_ZOOM_TO_EVENT]: (state: State): void => {
    state.zoomToEvent = !state.zoomToEvent;
    localStorage.setItem('settings', JSON.stringify(state));
  },
  [MUTATIONS.TOGGLE_FLASHING_SCREEN]: (state: State): void => {
    state.flashingScreen = !state.flashingScreen;
    localStorage.setItem('settings', JSON.stringify(state));
  },
  [MUTATIONS.TOGGLE_VOICE_ALERT]: (state: State): void => {
    state.voiceAlertSetting = !state.voiceAlertSetting;
    localStorage.setItem('settings', JSON.stringify(state));
  },
  [MUTATIONS.TOGGLE_ALERT_ONLY_IF_ABOVE_ENERGY_THRESHOLD]: (state: State): void => {
    state.alertOnlyIfAboveEnergyThreshold = !state.alertOnlyIfAboveEnergyThreshold;
    localStorage.setItem('settings', JSON.stringify(state));
  },
  [MUTATIONS.PUSH_SENSOR_COLOR_LIST]: (state: State, payload: SensorColor): void => {
    state.sensorColorList.push(payload);
  },
  [MUTATIONS.SET_SENSOR_COLOR]: (state: State, payload: SensorColor): void => {
    state.sensorColorList = state.sensorColorList.map(function(item) { return item.id === payload.id ? payload : item; });
    localStorage.setItem('settings', JSON.stringify(state));
  },
  [MUTATIONS.PUSH_SENSOR_POINT_SHAPE_LIST]: (state: State, payload: SensorPointShape): void => {
    state.sensorPointShapeList.push(payload);
  },
  [MUTATIONS.SET_SENSOR_POINT_SHAPE]: (state: State, payload: SensorPointShape): void => {
    state.sensorPointShapeList = state.sensorPointShapeList.map(function(item) { return item.id === payload.id ? payload : item; });
    localStorage.setItem('settings', JSON.stringify(state));
  },
  [MUTATIONS.PUSH_SENSOR_LINE_LIST]: (state: State, payload: SensorLine): void => {
    state.sensorLineList.push(payload);
  },
  [MUTATIONS.SET_SENSOR_LINE]: (state: State, payload: SensorLine): void => {
    state.sensorLineList = state.sensorLineList.map(function(item) { return item.id === payload.id ? payload : item; });
    localStorage.setItem('settings', JSON.stringify(state));
  },
  [MUTATIONS.RESET_SENSOR_LINE]: (state: State): void => {
    state.sensorLineList = state.sensorLineList.map(item => { return { id: item.id, line: true }; });
    localStorage.setItem('settings', JSON.stringify(state));
  },
  [MUTATIONS.SET_MICROSERVICE_DETAILS_LOG_FILTER]: (state: State, filter: MicroserviceDetailsLogFilter): void => {
    state.microserviceDetailsLogFilter = filter;
    localStorage.setItem('settings', JSON.stringify(state));
  },
  [MUTATIONS.SET_ALERT_INTERVAL]: (state: State, interval: number): void => {
    state.eventAlertInterval = interval;
    localStorage.setItem('settings', JSON.stringify(state));
  },
  [MUTATIONS.SET_N_EVENTS_PER_PAGE]: (state: State, nEventsPerPage: number): void => {
    state.nEventsPerPage = nEventsPerPage;
    localStorage.setItem('settings', JSON.stringify(state));
  },
  [MUTATIONS.SET_MAX_LOGS_PER_SERVICE]: (state: State, max: number): void => {
    state.maxLogsPerService = max;
    localStorage.setItem('settings', JSON.stringify(state));
  },
  [MUTATIONS.SET_ENERGY_THRESHOLD]: (state: State, threshold: number): void => {
    state.energyThreshold = threshold;
  }
};

const getters = {
  [GETTERS.GET_SENSOR_COLOR]: (state: State): (id: number) => Color | undefined => {
    return (id: number) => state.sensorColorList.find(color => color.id === id)?.color;
  },
  [GETTERS.GET_SENSOR_POINT_SHAPE]: (state: State): (id: number) => PointShape | undefined => {
    return (id: number) => state.sensorPointShapeList.find(shape => shape.id === id)?.shape;
  },
  [GETTERS.GET_SENSOR_LINE]: (state: State): (id: number) => boolean | undefined => {
    return (id: number) => state.sensorLineList.find(line => line.id === id)?.line;
  }
};

export default {
  state,
  actions,
  mutations,
  getters
} as Module<State, RootState>;
