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

import type { ActionContext, Module } from 'vuex';

import { ACTIONS as EVENT_ACTIONS, MUTATIONS as EVENT_MUTATIONS, GETTERS as GLM_GETTERS } from './EventModule';
import { ACTIONS as MESSAGE_ACTIONS, MUTATIONS as MESSAGE_MUTATIONS } from './MessageModule';
import { ACTIONS as STATUS_ACTIONS } from './MicroserviceStatusModule';
import type { EventListItem } from 'starfall-common/Types/EventListItem';
import { MUTATIONS as POPUP_MUTATIONS } from './PopupsModule';
import { MUTATIONS as SETTINGS_MUTATIONS } from './SettingsModule';
import { Namespaces } from './Namespaces';
import type { RootState } from '@/types/RootState';

export type State = Record<string, unknown>;

const state: State = { };

const namespace = Namespaces.Global;

export const ACTIONS = {
  INIT: namespace + 'INIT',
  SELECT_EVENT: namespace + 'SELECT_EVENT'
};

type Context = ActionContext<State, RootState>;

const actions = {
  [ACTIONS.INIT](context: Context): void {
    context.commit(SETTINGS_MUTATIONS.INIT);
    context.commit(EVENT_MUTATIONS.INIT);
    context.commit(MESSAGE_MUTATIONS.INIT);
    context.commit(POPUP_MUTATIONS.INIT);
    context.dispatch(STATUS_ACTIONS.INIT);
  },
  [ACTIONS.SELECT_EVENT](context: Context, id: string): void {
    context.commit(EVENT_MUTATIONS.CLEAR_VIEWER);
    context.commit(EVENT_MUTATIONS.SET_POINT_SOURCE_DETAILS, null);

    context.commit(EVENT_MUTATIONS.FLY_HOME);
    const event: EventListItem | undefined = context.rootGetters[GLM_GETTERS.SINGLE_EVENT_BY_ID](id);
    if (event === undefined) {
      console.warn(`global select event: no event ${id}`);
    } else if (!event.user_viewed) {
      context.dispatch(MESSAGE_ACTIONS.TOGGLE_EVENT_USER_VIEWED, id);
    }
    context.commit(EVENT_MUTATIONS.SET_LOCKED_VIEW, context.rootState.settingsModule.zoomToEvent);

    context.dispatch(MESSAGE_ACTIONS.GET_EVENT_DETAILS, id);
    context.dispatch(MESSAGE_ACTIONS.GET_EVENT_HISTORY, id);
    context.dispatch(MESSAGE_ACTIONS.GET_EVENT_SATELLITES, id);
    context.dispatch(MESSAGE_ACTIONS.GET_POINT_SOURCE_FILTER_EXTENTS, id);

    context.dispatch(EVENT_ACTIONS.CLEAR_SELECTED_EVENT);

    context.commit(EVENT_MUTATIONS.CLEAR_HOVERED_EVENT);
    context.commit(EVENT_MUTATIONS.SET_SELECTED_EVENT, id);
  }
};

export default {
  state,
  actions
} as Module<State, RootState>;
