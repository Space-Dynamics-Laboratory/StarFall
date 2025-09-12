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

import type { Module } from 'vuex';
import { Namespaces } from './Namespaces';
import type { RootState } from '@/types/RootState';

const namespace = Namespaces.Popups;

export const MUTATIONS = {
  INIT: namespace + 'INIT',
  CREATE_ABOUT_POPUP: namespace + 'CREATE_ABOUT_POPUP',
  CREATE_ATTRIBUTIONS_POPUP: namespace + 'CREATE_ATTRIBUTIONS_POPUP',
  CREATE_CONFIRMATION_POPUP: namespace + 'CREATE_CONFIRMATION_POPUP',
  CREATE_EVENT_ALERT_POPUP: namespace + 'CREATE_NEW_EVENT_POPUP',
  CREATE_EVENT_STATUS_POPUP: namespace + 'CREATE_EVENT_STATUS_POPUP',
  CREATE_HISTORY_NOTE_POPUP: namespace + 'CREATE_HISTORY_NOTE_POPUP',
  CREATE_INFO_POPUP: namespace + 'CREATE_INFO_POPUP',
  CREATE_SAVE_FILTER_POPUP: namespace + 'CREATE_SAVE_FILTER_POPUP',
  CREATE_TOAST_POPUP: namespace + 'CREATE_TOAST_POPUP'
};

export type State = {
};

const mutations = {
  [MUTATIONS.INIT](): void {},
  [MUTATIONS.CREATE_ABOUT_POPUP](): void {},
  [MUTATIONS.CREATE_ATTRIBUTIONS_POPUP](): void {},
  [MUTATIONS.CREATE_CONFIRMATION_POPUP](): void {},
  [MUTATIONS.CREATE_EVENT_ALERT_POPUP](): void {},
  [MUTATIONS.CREATE_EVENT_STATUS_POPUP](): void {},
  [MUTATIONS.CREATE_HISTORY_NOTE_POPUP](): void {},
  [MUTATIONS.CREATE_INFO_POPUP](): void {},
  [MUTATIONS.CREATE_SAVE_FILTER_POPUP](): void {},
  [MUTATIONS.CREATE_TOAST_POPUP](): void {}
};

export default {
  mutations
} as Module<State, RootState>;
