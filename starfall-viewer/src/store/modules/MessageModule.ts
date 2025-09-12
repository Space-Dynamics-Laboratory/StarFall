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

import SocketIOManager from '@/SocketIO/SockerIOManager';
import topics from 'starfall-common/topics';
import type { ActionContext, Module } from 'vuex';
import { Namespaces } from './Namespaces';
import type { PointSourceFilter } from 'starfall-common/Types/PointSourceFilter';
import type { RootState } from '@/types/RootState';
import type { Platforms } from 'starfall-common/Types/Platforms';
import type { Page } from 'starfall-common/Types/Paging';

const namespace = Namespaces.Message;

export const ACTIONS = {
  GET_EVENT_LIST: namespace + 'GET_EVENT_LIST',
  GET_EVENT_DETAILS: namespace + 'GET_EVENT_DETAILS',
  GET_POINT_SOURCE_DETAILS: namespace + 'GET_POINT_SOURCE_DETAILS',
  GET_EVENT_HISTORY: namespace + 'GET_EVENT_HISTORY',
  PUT_EVENT_HISTORY_NOTE: namespace + 'PUT_EVENT_HISTORY_NOTE',
  CHANGE_EVENT_PROCESSING_STATE: namespace + 'CHANGE_EVENT_PROCESSING_STATE',
  GET_EVENT_SATELLITES: namespace + 'GET_EVENT_SATELLITES',
  TOGGLE_EVENT_USER_VIEWED: namespace + 'TOGGLE_EVENT_USER_VIEWED',
  DELETE_EVENT: namespace + 'DELETE_EVENT',
  DUPLICATE_EVENT: namespace + 'DUPLICATE_EVENT',
  DELETE_VELOCITY: namespace + 'DELETE_VELOCITY',
  SAVE_VIEWER_LOG: namespace + 'SAVE_VIEWER_LOG',
  GET_ALL_PLATFORMS: namespace + 'GET_ALL_PLATFORMS',
  GET_POINT_SOURCE_FILTER_EXTENTS: namespace + 'GET_POINT_SOURCE_FILTER_EXTENTS',
  CHANGE_POINT_SOURCE_FILTER: namespace + 'CHANGE_POINT_SOURCE_FILTER',
  UPDATE_PLATFORMS_IN_DATABASE: namespace + 'UPDATE_PLATFORMS_IN_DATABASE'
};

export const MUTATIONS = {
  INIT: namespace + 'INIT'
};

export const GETTERS = {
};

export type State = {
  socket: SocketIOManager | null;
};

const state: State = {
  socket: null
};

const emit = (state: State, topic: string, ...args: unknown[]) => {
  state.socket?.emit(topic, ...args);
};

type Context = ActionContext<State, RootState>;

const actions = {
  [ACTIONS.GET_EVENT_LIST]({ state }: Context, page: Page): void {
    emit(state, topics.GetEventList, page);
  },
  [ACTIONS.GET_EVENT_DETAILS]({ state }: Context, eventId: string): void {
    emit(state, topics.GetEventDetails, eventId);
  },
  [ACTIONS.GET_POINT_SOURCE_DETAILS]({ state }: Context, psId: string): void {
    emit(state, topics.GetPointSourceDetails, psId);
  },
  [ACTIONS.GET_EVENT_HISTORY]({ state }: Context, eventId: string): void {
    emit(state, topics.GetEventHistory, eventId);
  },
  [ACTIONS.PUT_EVENT_HISTORY_NOTE]({ state }: Context, payload: any): void {
    emit(state, topics.PutEventHistoryNote, payload);
  },
  [ACTIONS.CHANGE_EVENT_PROCESSING_STATE]({ state }: Context, payload: any): void {
    emit(state, topics.ChangeEventProcessingState, payload);
  },
  [ACTIONS.GET_EVENT_SATELLITES]({ state }: Context, eventId: string): void {
    emit(state, topics.GetSensorsForEvent, eventId);
  },
  [ACTIONS.TOGGLE_EVENT_USER_VIEWED]({ state }: Context, eventId: string): void {
    emit(state, topics.ToggleEventUserViewed, eventId);
  },
  [ACTIONS.DELETE_EVENT]({ state }: Context, eventId: string): void {
    emit(state, topics.DeleteEvent, eventId);
  },
  [ACTIONS.DUPLICATE_EVENT]({ state }: Context, eventId: string): void {
    emit(state, topics.DuplicateEvent, eventId);
  },
  [ACTIONS.DELETE_VELOCITY]({ state }: Context, eventId: string): void {
    emit(state, topics.DeleteVelocity, eventId);
  },
  [ACTIONS.SAVE_VIEWER_LOG]({ state }: Context, log: string): void {
    emit(state, topics.SaveViewerLog, log);
  },
  [ACTIONS.GET_ALL_PLATFORMS]({ state }: Context, log: string): void {
    emit(state, topics.GetAllPlatforms, log);
  },
  [ACTIONS.GET_POINT_SOURCE_FILTER_EXTENTS]({ state }: Context, eventId: string): void {
    emit(state, topics.GetPointSourceFilterExtents, eventId);
  },
  [ACTIONS.CHANGE_POINT_SOURCE_FILTER]({ state, rootState }: Context, filter: PointSourceFilter): void {
    const eventId = rootState.eventModule.selectedEventSummary?.event_id;
    if (eventId) {
      emit(state, topics.ChangePointSourceFilter, { filter, eventId });
    }
  },
  [ACTIONS.UPDATE_PLATFORMS_IN_DATABASE]({ state }: Context, platforms: Platforms): void {
    emit(state, topics.UpdatePlatformsInDatabase, platforms);
  }
};

const mutations = {
  [MUTATIONS.INIT](state: State): void {
    state.socket = new SocketIOManager();
  }
};

const getters = {
};

export default {
  state,
  actions,
  mutations,
  getters
} as Module<State, RootState>;
