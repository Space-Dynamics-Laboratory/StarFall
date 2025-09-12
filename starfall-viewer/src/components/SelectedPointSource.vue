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
<div id="selected-point-source" class="dark" v-if="ps">
  <div>
    <p class="mt0"><span class="label">Point Source ID:</span> <span v-if="ps">{{ ps.point_source_id }}</span><span v-else>No Point Source Selected</span></p>
    <p v-if="ps"><span class="label">Platform:</span> {{ ps.platform_name }} - {{ ps.sensor_name }}</p>
    <p v-for="[key, value] in psEntries" :key="key" >
      <span class="label">{{ psMap[key].label }}:</span> {{ psMap[key].format ? psMap[key].format(value) : value }}
    </p>
    <div v-if="location">
      <p><span class="label">Ground Intersection Location:</span></p>
      <ul>
        <li><span class="label">Lat (°N):</span> {{ location[0].toFixed(2) }}</li>
        <li><span class="label">Lon (°E):</span> {{ location[1].toFixed(2) }}</li>
        <li><span class="label">Alt (km):</span> {{ format(location[2]) }}</li>
      </ul>
    </div>
    <template v-if="ps && ps.tags">
      <p class="mb0 label">Tags: </p>
      <ul>
        <li v-for="(tag, idx) in sortTags(ps.tags)" :key="idx">
          {{ tag }}
          <button
            class="btn"
            v-if="tag === USER_TAG.USER_ACCEPTED || tag === USER_TAG.USER_REJECTED"
            @click="removeTag(ps.point_source_id, tag)"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"></path><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
          </button>
        </li>
      </ul>
    </template>
  </div>
  <div
    class="flex justify-center sticky text-small height-1"
    :class="ps.tags.includes(USER_TAG.USER_ACCEPTED) ? 'green' : ps.tags.includes(USER_TAG.USER_REJECTED) ? 'red' : ''"
  >
    <svg v-if="loading" class="loader" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg>
    <div v-else>
      <div
          v-if="!(ps.tags.includes(USER_TAG.USER_ACCEPTED) || ps.tags.includes(USER_TAG.USER_REJECTED))"
        >
          <button
            :title="`add ${USER_TAG.USER_ACCEPTED} tag`"
            class="btn text-small"
            v-if="!ps.tags.includes(TAG.ACCEPTED)"
            @click="addTag(ps.point_source_id, USER_TAG.USER_ACCEPTED)"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="pr6" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 10v12"></path><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z"></path></svg>
            Accept Point
          </button>
          <button
            :title="`add ${USER_TAG.USER_REJECTED} tag`"
            class="btn text-small"
            v-if="ps.tags.includes(TAG.ACCEPTED)"
            @click="addTag(ps.point_source_id, USER_TAG.USER_REJECTED)"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="pr6" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 14V2"></path><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"></path></svg>
            Reject Point
          </button>
      </div>
      <div class="flex green text-small" v-if="ps.tags.includes(USER_TAG.USER_ACCEPTED)">
        {{ USER_TAG.USER_ACCEPTED }}
      </div>
      <div class="flex red text-small" v-if="ps.tags.includes(USER_TAG.USER_REJECTED)">
        {{ USER_TAG.USER_REJECTED }}
      </div>
    </div>
  </div>
</div>
</template>

<script lang="ts">
import type { PointSourceDetails as PointSourceDetails_t } from '@/types/PointSourceDetails';
import pointSourceDetailsMap from '@/helpers/pointSourceDetailsMap';
import type { EventListItem } from 'starfall-common/Types/EventListItem';
import ecef from 'starfall-common/ecef';
import { ACTIONS as MESSAGE_ACTIONS } from '@/store/modules/MessageModule';
import * as R from 'ramda';

const USER_TAG = {
  USER_ACCEPTED: 'User Accepted',
  USER_REJECTED: 'User Rejected'
};

const TAG = {
  ACCEPTED: 'Accepted'
};

export default {
  name: 'SelectedPointSource',
  data() {
    return {
      pointSourceColumnNames: {},
      loading: false,
    }
  },
  methods: {
    sortTags: R.sort((a: string, b: string) => a < b ? -1 : a > b ? 1 : 0),
    format(num: number): string {
      const result = num / 1000;
      if (result > -0.0049 && result < 0) {
        return '0.00';
      } else {
        return result.toFixed(2);
      }
    },
    removeTag(pointSourceId, tag) {
      this.loading = true;
      fetch(`/api/point-source-tag/${this.event?.event_id}/${pointSourceId}/${encodeURI(tag)}`, {
        method: 'DELETE'
      })
        .then(res => res.json())
        .then(res => {
          this.loading = false;
          if (res.error) {
            console.error(res.error);
          } else {
            this.$store.dispatch(MESSAGE_ACTIONS.GET_POINT_SOURCE_DETAILS, this.ps?.point_source_id);
          }
        })
        .catch(err => {
          console.error('fetch error', err);
        });
    },
    addTag(pointSourceId, tag) {
      this.loading = true;
      fetch(`/api/point-source-tag/${this.event?.event_id}/${pointSourceId}/${encodeURI(tag)}`, {
        method: 'PUT'
      })
        .then(res => res.json())
        .then(res => {
          this.loading = false;
          if (res.error) {
            console.error(res.error);
          } else {
            this.$store.dispatch(MESSAGE_ACTIONS.GET_POINT_SOURCE_DETAILS, this.ps?.point_source_id);
          }
        })
        .catch(err => {
          console.error('fetch error', err);
        });
    }
  },
  mounted() {
    fetch('/api/point-source-column-names')
      .then(res => res.json())
      .then(res => {
        this.pointSourceColumnNames = res;
      })
      .catch(err => {
        console.error('fetch error', err);
      });
  },
  computed: {
    USER_TAG() {
      return USER_TAG;
    },
    TAG() {
      return TAG;
    },
    ps(): PointSourceDetails_t | null {
      return this.$store.state.eventModule.selectedPointSource;
    },
    event(): EventListItem | null {
      return this.$store.state.eventModule.selectedEventSummary;
    },
    location() {
      return this.ps?.meas_far_point_ecef_m ? ecef.unproject(this.ps.meas_far_point_ecef_m) : null;
    },
    psEntries(): [string, unknown][] {
      const result = this.ps ? Object.entries(this.ps) : [];
      return result.filter(([key, val]) => Object.prototype.hasOwnProperty.call(this.psMap, key) && val !== null);
    },
    psMap(): any {
      return { ...pointSourceDetailsMap, ...this.pointSourceColumnNames };
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

* {
  font: 13px "Consolas", monospace;
}
#selected-point-source {
  position: relative;
  min-height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
p {
  padding-left: 4px;
  margin: 6px 0;
}
ul {
  margin-top: 0;
}
.label {
  font-weight: bold;
}
.btn {
  font-size: 0.7rem;
  display: inline-flex;
  align-items: center;
  padding: 1px 3px;
  margin: 0;
}
.text-small {
  font-size: 0.7rem;
}
.flex {
  display: flex;
  align-items: center;
}
.justify-center {
  justify-content: center;
}
.mt0 {
  margin-top: 0;
}
.mb0 {
  margin-bottom: 0;
}
.pb1 {
  padding-bottom: 6px;
}
.pr6 {
  padding-right: 6px;
}
.sticky {
  position: sticky;
  bottom: 0;
  right: 0;
  left: 0;
  background: #222;
  padding: 2px 0;
  border-top: 1px solid #333;
}
.green {
  background: rgb(186, 229, 186);
}
.red {
  background: rgb(244, 216, 216);
}
.h100 {
  height: 100%;
}
.height-1 {
  height: 1.5em;
}
.loader {
  animation-name: spinner;
  animation-duration: 1s;
  animation-iteration-count: infinite;
}
@keyframes spinner {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.dark {
  background-color: #222;
  color: $white;
}
</style>
