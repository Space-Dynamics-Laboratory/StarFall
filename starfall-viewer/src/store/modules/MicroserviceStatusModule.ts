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

import JSZip from 'jszip';
import type { ActionContext, GetterTree, Module } from 'vuex';

import { formatUTC, parseTimestamp, msToTimestamp } from 'starfall-common/helpers/time';
import version from 'starfall-common/config/version';
import { ACTIONS as MESSAGE_ACTIONS } from './MessageModule';
import type { Heartbeat } from 'starfall-common/Types/Heartbeat';
import { LogState } from '@/types/LogState';
import type { MicroserviceStatus } from 'starfall-common/Types/MicroserviceStatus';
import { Namespaces } from './Namespaces';
import type { RootState } from '@/types/RootState';

const namespace = Namespaces.MicroserviceStatus;

export type State = {
  latestVersion: boolean;
  microserviceStatusList: MicroserviceStatus[];
};

const VIEWER = 0;
const SERVER = 1;

const state: State = {
  latestVersion: true,
  microserviceStatusList: [
    {
      name: 'StarFall Viewer',
      status: [],
      logs: [],
      lastUpdateTimeStamp: Date.now(),
      receivedLastResponse: true,
      viewedTimeStamp: 0
    },
    {
      name: 'StarFall Server',
      status: ['No heartbeat received'],
      logs: [],
      lastUpdateTimeStamp: 0,
      receivedLastResponse: false,
      viewedTimeStamp: 0
    }
  ]
};

export const ACTIONS = {
  INIT: namespace + 'INIT',
  SAVE_VIEWER_LOG: namespace + 'SAVE_VIEWER_LOG',
  MARK_LOGS_AS_VIEWED: namespace + 'MARK_LOGS_AS_VIEWED',
  EXPORT_SINGLE_SERVICE: namespace + 'EXPORT_SINGLE_SERVICE',
  EXPORT_ALL_SERVICES: namespace + 'EXPORT_ALL_SERVICES'
};

export const MUTATIONS = {
  PUSH_VIEWER_LOG: namespace + 'PUSH_VIEWER_LOG',
  SET_VIEWED_TIMESTAMP: namespace + 'SET_VIEWED_TIMESTAMP',
  UPDATE_STATUS: namespace + 'UPDATE_STATUS',
  HEARTBEAT: namespace + 'HEARTBEAT',
  CHECK_HEARTBEAT: namespace + 'CHECK_HEARTBEAT'
};

export const GETTERS = {
  MICROSERVICE_CHAIN_STATUS: namespace + 'MICROSERVICE_CHAIN_STATUS',
  MICROSERVICE_STATUS: namespace + 'MICROSERVICE_STATUS',
  LOG_STATUS: namespace + 'LOG_STATUS',
  LOG_COUNTS_FOR_SERVICE: namespace + 'LOG_COUNTS_FOR_SERVICE'
};

type Context = ActionContext<State, RootState>;

// curried function, takes a Date object
const timestamp = formatUTC('MM/dd/y HH:mm:ss');

const actions = {
  [ACTIONS.INIT]: (context: Context) => {
    setInterval(() => {
      context.commit(MUTATIONS.CHECK_HEARTBEAT);
    }, 30 * 1000);
  },
  [ACTIONS.SAVE_VIEWER_LOG]: (context: Context, log: string) => {
    context.commit(MUTATIONS.PUSH_VIEWER_LOG, {
      log: log,
      maxLogs: context.rootState.settingsModule.maxLogsPerService
    });
    if (log.includes('(warning)') || log.includes('error')) {
      context.dispatch(MESSAGE_ACTIONS.SAVE_VIEWER_LOG, log);
    }
  },
  [ACTIONS.MARK_LOGS_AS_VIEWED]: (context: Context, index: number): void => {
    context.commit(MUTATIONS.SET_VIEWED_TIMESTAMP, {
      time: (new Date(timestamp(new Date()))).getTime(),
      index: index
    });
  },
  [ACTIONS.EXPORT_SINGLE_SERVICE]: ({ state }: Context, index: number): void => {
    const datestr = formatUTC('MM-dd-y_HH-mm-ss', new Date());
    const filename = `StarFall_LOGS_${state.microserviceStatusList[index].name}_${datestr}`.replace(/\s/g, '_');
    const text
      = 'STATUS\n'
      + state.microserviceStatusList[index].status.reduce(
        (prev, curr) => `${prev}\n* ${curr}`, ''
      )
      + '\n\nLOGS\n'
      + state.microserviceStatusList[index].logs.reduce(
        (prev, curr) => `${prev}\n${curr}`, ''
      );

    const link = document.createElement('a');
    link.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    link.download = filename;
    link.style.display = 'none';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },
  [ACTIONS.EXPORT_ALL_SERVICES]: ({ state }: Context): void => {
    const zip = new JSZip();
    const datestr = formatUTC('MM-dd-y_HH-mm-ss', new Date());
    const zipfilename = `StarFall_LOGS_${datestr}.zip`;
    for (const index in state.microserviceStatusList) {
      const filename = `StarFall_LOGS_${state.microserviceStatusList[index].name}_${datestr}.txt`.replace(/\s/g, '_');
      const text
        = 'STATUS\n'
        + state.microserviceStatusList[index].status.reduce(
          (prev: string, curr: string) => `${prev}\n* ${curr}`, ''
        )
        + '\n\nLOGS\n'
        + state.microserviceStatusList[index].logs.reduce(
          (prev: string, curr: string) => `${prev}\n${curr}`, ''
        );
      zip.file(filename, text);
    }

    zip.generateAsync({ type: 'blob', compression: 'DEFLATE' })
      .then((blob: Blob) => {
        const blobUrl = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = zipfilename;
        link.style.display = 'none';

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      });
  }
};

const mutations = {
  [MUTATIONS.PUSH_VIEWER_LOG]: (state: State, { log, maxLogs }: { log: string, maxLogs: number }) => {
    state.microserviceStatusList[VIEWER].logs.unshift(log);
    if (state.microserviceStatusList[VIEWER].logs.length > maxLogs) {
      state.microserviceStatusList[VIEWER].logs.length = maxLogs;
    }
    state.microserviceStatusList[VIEWER].lastUpdateTimeStamp = Date.now();
  },
  [MUTATIONS.SET_VIEWED_TIMESTAMP]: (state: State, { time, index }: { time: number, index: number }): void => {
    state.microserviceStatusList[index].viewedTimeStamp = time;
  },
  [MUTATIONS.UPDATE_STATUS]: (state: State, statuses: MicroserviceStatus[]): void => {
    for (const status of statuses) {
      const i = state.microserviceStatusList.findIndex(s => s.name === status.name);
      if (i < 0) {
        state.microserviceStatusList.push(status);
      } else {
        status.viewedTimeStamp = state.microserviceStatusList[i].viewedTimeStamp;
        state.microserviceStatusList[i] = status;
      }
    }
  },
  [MUTATIONS.HEARTBEAT]: (state: State, payload: Heartbeat): void => {
    state.latestVersion = payload.version === version;
    state.microserviceStatusList[SERVER].lastUpdateTimeStamp = Date.now();
    state.microserviceStatusList[SERVER].receivedLastResponse = true;
    state.microserviceStatusList[SERVER].status[0] = 'Heart beat received';
  },
  [MUTATIONS.CHECK_HEARTBEAT]: (state: State): void => {
    const timeSinceLastHeartbeat = Date.now() - state.microserviceStatusList[SERVER].lastUpdateTimeStamp;
    state.microserviceStatusList[SERVER].receivedLastResponse = timeSinceLastHeartbeat < 30 * 1000;
    if (!state.microserviceStatusList[SERVER].receivedLastResponse) {
      state.microserviceStatusList[SERVER].status[0] = `Server might be down, last heartbeat ${msToTimestamp(timeSinceLastHeartbeat)} seconds ago`;
    }
  }
};

const getters: GetterTree<State, RootState> = {
  [GETTERS.MICROSERVICE_CHAIN_STATUS]: (state: State, getters): LogState => {
    let status = LogState.OK;
    for (let index = 0; index < state.microserviceStatusList.length; ++index) {
      if (getters[GETTERS.MICROSERVICE_STATUS](index) === LogState.Warning) status = LogState.Warning;
      if (getters[GETTERS.MICROSERVICE_STATUS](index) === LogState.Error) return LogState.Error;
    }
    return status;
  },
  [GETTERS.MICROSERVICE_STATUS]: (state: State, getters): (index: number) => LogState => {
    return (index: number) => {
      if (state.microserviceStatusList[index].receivedLastResponse === false) return LogState.Error;
      let status = LogState.OK;
      for (let log = 0; log < state.microserviceStatusList[index].logs.length; ++log) {
        if (getters[GETTERS.LOG_STATUS](index, log) === LogState.Warning) status = LogState.Warning;
        if (getters[GETTERS.LOG_STATUS](index, log) === LogState.Error) return LogState.Error;
      }
      return status;
    };
  },
  [GETTERS.LOG_STATUS]: (state: State): (componentIndex: number, logIndex: number) => LogState => {
    return (componentIndex: number, logIndex: number) => {
      const logMsg = state.microserviceStatusList[componentIndex].logs[logIndex];
      if (logMsg.includes('(debug)') || logMsg.includes('(info)')) {
        return LogState.OK;
      }
      if (logMsg.includes('(warning)')
        && parseTimestamp(logMsg) > state.microserviceStatusList[componentIndex].viewedTimeStamp) {
        return LogState.Warning;
      }
      if (logMsg.includes('(error)')
        && parseTimestamp(logMsg) > state.microserviceStatusList[componentIndex].viewedTimeStamp) {
        return LogState.Error;
      }
      return LogState.OK;
    };
  },
  [GETTERS.LOG_COUNTS_FOR_SERVICE]: (state: State) => {
    return (componentIndex: number) => {
      const count = {
        [LogState.Debug]: 0,
        [LogState.Info]: 0,
        [LogState.Warning]: 0,
        [LogState.Error]: 0,
        [LogState.OK]: 0
      };
      for (let logIndex = 0; logIndex < state.microserviceStatusList[componentIndex].logs.length; ++logIndex) {
        const logMsg = state.microserviceStatusList[componentIndex].logs[logIndex];
        if (logMsg.includes('(degug)')) {
          ++count[LogState.Debug];
        } else if (logMsg.includes('(info)')) {
          ++count[LogState.Info];
        } else if (logMsg.includes('(warning)')
          && parseTimestamp(logMsg) > state.microserviceStatusList[componentIndex].viewedTimeStamp) {
          ++count[LogState.Warning];
        } else if (logMsg.includes('(error)')
          && parseTimestamp(logMsg) > state.microserviceStatusList[componentIndex].viewedTimeStamp) {
          ++count[LogState.Error];
        } else {
          ++count[LogState.Info];
        }
      }
      return count;
    };
  }
};

export default {
  state,
  actions,
  mutations,
  getters
} as Module<State, RootState>;
