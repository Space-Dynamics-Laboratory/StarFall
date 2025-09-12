<!-- 
# ------------------------------------------------------------------------
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# ------------------------------------------------------------------------
-->
<template>
<div
  class="microservice-details"
  :style="`right: 200px; width: 700px;`"
>
  <h1 class="title">{{ microservice.name }}</h1>
  <div class="status">
    <p :class="getMicroserviceActiveClass(microservice.receivedLastResponse)">
      <fa-icon
        size="lg"
        icon="circle" />
      <span class="black"> last updated: {{ formatDate(microservice.lastUpdateTimeStamp) }} </span>
    </p>
    <ul>
      <li v-for="(message, index) of microservice.status" :key="index">
        {{ message }}
      </li>
    </ul>
  </div>

  <div class="flex">
    <h2 class="label">Recent Logs</h2>
    <LogFilterButtons
      :microserviceIndex="microserviceIndex"
      @toggle="onToggleFilter"
    />
  </div>

  <div class="logs" name="logs">
    <div class="logs-content">
      <p v-for="(log, index) in logs"
        :key="index"
        :class="log.class"
      >
        <fa-icon
          v-if="parseLogDate(log.logMsg) > viewedTimeStamp"
          size="xs"
          icon="circle"
        />
        {{ log.logMsg }}
      </p>
    </div>

    <div v-if="microservice.logs.length === 0">
      <p class="info-text"> no logs reported </p>
    </div>
  </div>
  <div id="footer">
    <button @click="markAsViewed()" class="btn-base-dark btn right">Mark As Viewed</button>
    <button @click="exportLogs()" class="btn-base-dark btn left">Export</button>
    <input type="checkbox" name="exportAll" class="export-all" v-model="exportAll">
    <label for="export-all">All Microservices</label>
  </div>
</div>
</template>

<script lang="ts">
import LogFilterButtons from '@/components/LogFilterButtons.vue';
import { formatUTC, parseTimestamp as parseTimestamp_f } from 'starfall-common/helpers/time';
import { ACTIONS as STATUS_ACTIONS } from '@/store/modules/MicroserviceStatusModule';
import { LogState } from '@/types/LogState';
import { MUTATIONS as SETTINGS_MUTATIONS } from '@/store/modules/SettingsModule';
import type { MicroserviceStatus } from 'starfall-common/Types/MicroserviceStatus';
import type { MicroserviceDetailsLogFilter } from '@/types/MicroserviceDetailsLogFilter';

const DEFAULT_FILTERS = {
  debug: true,
  info: true,
  warning: true,
  error: true
}

export default {
  name: 'StatusDetails',
  components: {
    LogFilterButtons
  },
  props: {
    microserviceIndex: Number
  },
  data() {
    return {
      exportAll: true,
      filter: DEFAULT_FILTERS as MicroserviceDetailsLogFilter | null
    }
  },
  mounted() {
    this.filter = this.$store.state.settingsModule.microserviceDetailsLogFilter;
  },
  methods: {
    parseLogDate: parseTimestamp_f,
    getMicroserviceActiveClass(receivedLastUpdate: boolean): string {
      if (receivedLastUpdate) return 'service-active';
      return 'service-inactive';
    },
    onToggleFilter(filter: string): void {
      if (filter === 'debug') this.filter.debug = !this.filter.debug;
      if (filter === 'info') this.filter.info = !this.filter.info;
      if (filter === 'warning') this.filter.warning = !this.filter.warning;
      if (filter === 'error') this.filter.error = !this.filter.error;
      this.$store.commit(SETTINGS_MUTATIONS.SET_MICROSERVICE_DETAILS_LOG_FILTER, this.filter);
    },
    markAsViewed(): void {
      this.$store.dispatch(STATUS_ACTIONS.MARK_LOGS_AS_VIEWED, this.microserviceIndex);
    },
    exportLogs(): void {
      if (this.exportAll) {
        this.$store.dispatch(STATUS_ACTIONS.EXPORT_ALL_SERVICES);
      } else {
        this.$store.dispatch(STATUS_ACTIONS.EXPORT_SINGLE_SERVICE, this.microserviceIndex);
      }
    },
    formatDate(mssue: number): string {
      return mssue === 0 ? 'never' : formatUTC('y-MM-dd HH:mm:ss', new Date(mssue));
    }
  },
  computed: {
    microservice(): MicroserviceStatus {
      return this.$store.state.microserviceStatusModule.microserviceStatusList[this.microserviceIndex];
    },
    logs(): { logMsg: string, class: any }[] {
      let lastLogClass = 'info-text';
      return this.microservice.logs
        .filter(log => {
          if (log.includes('(debug)')) return this.filter.debug;
          if (log.includes('(info)')) return this.filter.info;
          if (log.includes('(warning)')) return this.filter.warning;
          if (log.includes('(error)')) return this.filter.error;
          return this.filter.error;
        })
        .map((logMsg: string) => {
          if (logMsg.includes('(debug)')) {
            lastLogClass = 'debug-text';
            return { logMsg, class: { 'debug-text': true } };
          }
          if (logMsg.includes('(info)')) {
            lastLogClass = 'info-text';
            return { logMsg, class: { 'info-text': true } };
          }
          if (logMsg.includes('(warning)')) {
            lastLogClass = 'warning-text';
            return { logMsg, class: { 'warning-text': true } };
          }
          if (logMsg.includes('(error)')) {
            lastLogClass = 'error-text';
            return { logMsg, class: { 'error-text': true } };
          }
          return { logMsg, class: { [lastLogClass]: true } };
        });
    },
    LogState(): typeof LogState {
      return LogState;
    },
    viewedTimeStamp(): number {
      if (this.microserviceIndex !== null) {
        return this.$store.state.microserviceStatusModule.microserviceStatusList[this.microserviceIndex].viewedTimeStamp;
      }
      return 0;
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

.flex {
  display: flex;
  justify-content: space-between;
}
.title {
  text-align: center;
  color: $black;
  word-break: break-all;
  white-space: normal;
}
.logs {
  background-color: $gl-grey;
  border-radius: 5px;
  overflow-y: auto;
  overflow-x: auto;
  display: flex;
  padding: 1em;
}
.logs-content {
  font: 13px "Consolas", monospace;
  background-color: $gl-grey;
  text-align: left;
  overflow-wrap: break-word;
  white-space: nowrap;
  max-height: 200px;
  border-radius: 5px;
}
.logs-content > p {
  white-space: pre;
}
p {
  margin: 2px 2px 2px 10px;
  word-break: break-all;
  white-space: normal;
}
.status {
  text-align: left;
  font: 13px "Consolas", monospace;
}
.status li {
  text-wrap: auto;
}
.warning-text {
  color: $warning;
}
.debug-text {
  color: $debug;
}
.info-text {
  color: $white;
}
.error-text {
  color: $error;
}
.service-inactive {
  color: $service-inactive;
}
.service-active {
  color: $service-active;
}
.label {
  display: inline-block;
  text-align: left;
  margin-bottom: auto;
  margin-top: auto;
}
.microservice-details {
  padding: 0 1em;
  padding-bottom: 1em;
  position: absolute;
  top: 0;
  background-color: $white;
  white-space: nowrap;
  overflow: hidden;
  box-shadow: 0 2px 5px 0 $shadow, 0 2px 10px 0 $shadow-light;
  z-index: 99;
}
.export-all {
  margin-top: 25px;
}
.btn {
  margin-top: 10px;
}
.right {
  float: right;
}
.left {
  float: left;
}
.black { color: $black }
</style>
