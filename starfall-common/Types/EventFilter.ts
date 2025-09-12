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

import { ProcessingState } from './ProcessingState';
import * as R from 'ramda';

type Filter = {
  enabled: boolean;
};

export type DateFilter = Filter & {
  lte: number;
  gte: number;
};

export type EnergyFilter = Filter & {
  lte: number;
  gte: number;
};

export type StateFilter = Filter & {
  [key in ProcessingState]: boolean;
};

export type EventFilter = {
  approx_trigger_time: DateFilter;
  approx_energy_j: EnergyFilter;
  state_filter: StateFilter;
  unviewed: boolean;
};

export type SavedEventFilter = EventFilter & {
  name: string
};

export const defaultFilter: EventFilter = {
  approx_trigger_time: { enabled: false, gte: -Number.MAX_SAFE_INTEGER, lte: Number.MAX_SAFE_INTEGER },
  approx_energy_j: { enabled: false, gte: -Number.MAX_SAFE_INTEGER, lte: Number.MAX_SAFE_INTEGER },
  // @ts-ignore
  state_filter: {
    enabled: false,
    ...R.zipObj(
    // @ts-ignore
      Object.values(ProcessingState).filter(x => !isNaN(Number(x))),
      R.repeat(false, Object.values(ProcessingState).length)
    )
  },
  unviewed: false
};
