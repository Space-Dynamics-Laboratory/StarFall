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
<div class="relative h100">
  <div v-if="detailView" class="h100 flex flex-column space-between">
  <div class="filter-card-container">
    <button class="mb5 w100 fixed top reset-btn z-index" @click="resetFilters">
      <svg class="mr" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2v6h-6"></path><path d="M21 13a9 9 0 1 1-3-7.7L21 8"></path></svg>
      Reset Filters
    </button>
    <div> <!-- tags -->
      <div class="flex space-between">
        <h3 class="m0">Tag Filter</h3>
        <input class="toggle" type="checkbox" name="tags" id="tags" :disabled="!detailView" v-model="filter.tags.enabled">
        <label class="sr-only" for="tags">Enable</label>
      </div>
      <ul>
        <li class="flex align-center" v-for="(tag, i) in sortTags(allTags)" :key="`tag-${i}`">
          <input
            type="checkbox"
            :name="tag"
            :id="tag"
            :value="tag"
            :disabled="!detailView || !filter.tags.enabled"
            v-model="filter.tags.tags"
          >
          <label :title="tag" class="overflow-ellipsis" :for="tag"> {{ tag }} </label>
        </li>
      </ul>
    </div>
    <div> <!-- time -->
      <div class="flex space-between">
        <h3 class="m0">Time Filter</h3>
        <input class="toggle" type="checkbox" name="time" id="time" :disabled="!detailView" v-model="filter.time.enabled">
        <label class="sr-only" for="time">Enable</label>
      </div>
      <div class="flex-row mt10 white nowrap">
        <div class="overflow-ellipsis" :title="formatDate(filter.time.extents[0])" >{{ formatDate(filter.time.extents[0], 'HH:mm:ss') }}</div>
        <div class="overflow-ellipsis" :title="formatDate(filter.time.extents[1])" >{{ formatDate(filter.time.extents[1], 'HH:mm:ss') }}</div>
      </div>
      <div class="slider-container">
        <Slider
          class="slider"
          v-model="filter.time.extents"
          :min="minTime"
          :max="maxTime"
          :disabled="!detailView || !filter.time.enabled"
          :tooltips="false"
        />
      </div>
    </div>
    <div> <!-- intensity -->
      <div class="flex space-between">
        <h3 class="m0">Intensity Filter</h3>
        <input class="toggle" type="checkbox" name="intensity" id="intensity" :disabled="!detailView" v-model="filter.intensity.enabled">
        <label class="sr-only" for="intensity">Enable</label>
      </div>
      <div class="flex-row mt10">
        <div> {{ lowIntensity }} </div>
        <div> {{ highIntensity }} </div>
      </div>
      <div class="slider-container">
        <Slider
          class="slider"
          v-model="filter.intensity.extents"
          :min="0"
          :max="100"
          :disabled="!detailView || !filter.intensity.enabled"
          :tooltips="false"
        />
      </div>
    </div>
    <div> <!-- geo filter -->
      <div class="flex space-between">
        <h3 class="m0 mb1">Geo Filter</h3>
        <input class="toggle" type="checkbox" name="geo" id="geo" :disabled="!detailView" v-model="filter.geo.enabled">
        <label class="sr-only" for="geo">Geo Filter</label>
      </div>
      <div class="geo-flex">
        <label for="lat">Lat (&#176;)</label>
        <input type="number" name="lat" id="lat" :disabled="!detailView || !filter.geo.enabled" v-model="filter.geo.lat">
      </div>
      <div class="geo-flex">
        <label for="lon">Lon (&#176;)</label>
        <input type="number" name="lon" id="lon" :disabled="!detailView || !filter.geo.enabled" v-model="filter.geo.lon">
      </div>
      <div class="geo-flex">
        <label for="radius">Radius (km)</label>
        <input type="number" name="radius" id="radius" :disabled="!detailView || !filter.geo.enabled" v-model="filter.geo.radius">
      </div>
    </div>
    <div> <!-- cluster size -->
      <div class="flex space-between">
        <h3 class="m0">Cluster Size Filter</h3>
        <input class="toggle" type="checkbox" name="cluster-size" id="cluster-size" :disabled="!detailView" v-model="filter.clusterSize.enabled">
        <label class="sr-only" for="cluster-size">Cluster Size Filter</label>
      </div>
      <div class="flex-row mt10">
        <label> {{ filter.clusterSize.extents[0] }} </label>
        <label> {{ filter.clusterSize.extents[1] }} </label>
      </div>
      <div class="slider-container">
        <Slider
          class="slider"
          v-model="filter.clusterSize.extents"
          :min="minClusterSize"
          :max="maxClusterSize"
          :disabled="!detailView || !filter.clusterSize.enabled"
          :tooltips="false"
        />
      </div>
    </div>
    <div> <!-- horizon -->
      <div class="flex space-between">
        <h3 class="m0">Horizon Filter</h3>
        <input class="toggle" type="checkbox" name="horizon" id="horizon" :disabled="!detailView" v-model="filter.horizon.enabled">
        <label class="sr-only" for="horizon">Horizon Filter</label>
      </div>
      <ul>
        <li>
          <input
            type="checkbox"
            name="above-horizon"
            id="above-horizon"
            :disabled="!detailView || !filter.horizon.enabled"
            v-model="filter.horizon.above"
          >
          <label for="above-horizon">Above</label>
        </li>
        <li>
          <input
            type="checkbox"
            name="below-horizon"
            id="below-horizon"
            :disabled="!detailView || !filter.horizon.enabled"
            v-model="filter.horizon.below"
          >
          <label for="below-horizon">Below</label>
        </li>
      </ul>
    </div>
  </div>
  <div v-if="pointCount !== undefined" class="filter-controls fixed flex content-center white text-small z-index">
    {{ pointCount }} Points Selected
  </div>
  </div>
  <div class="white p5" v-else>
    No event selected
  </div>
</div>
</template>

<script lang="ts">
import type { RootState } from '@/types/RootState';
import Slider from '@vueform/slider';
import * as R from 'ramda';
import { ACTIONS as MESSAGE_ACTIONS } from '@/store/modules/MessageModule';
import { formatUTC } from 'starfall-common/helpers/time';
import type { PointSourceFilter } from 'starfall-common/Types/PointSourceFilter';
import type { PointSourceFilterExtents } from 'starfall-common/Types/PointSourceFilterExtents';
import type { EventListItem } from 'starfall-common/Types/EventListItem';

const toFixed5 = (value: number) => parseFloat(value.toFixed(5));

const DEFAULT_TAGS = ['Accepted', 'User Accepted', 'Group Accepted'];

// round up most significant digit: 1001 -> 2000
const roundUp = (value: number) => {
  if (!value) return 0;
  const n = Math.pow(10,
    Math.floor(Math.log10(value)) // number of digits
  );
  return Math.ceil(value / n) * n;
};

// round down most significant digit: 1999 -> 1000
const roundDown = (value: number) => {
  if (!value) return 0;
  const n = Math.pow(10,
    Math.floor(Math.log10(value)) // number of digits
  );
  return Math.floor(value / n) * n;
};

export default {
  name: 'PointSourceFilters',
  components: {
    Slider
  },
  data() {
    return {
      PSExtents: undefined as PointSourceFilterExtents | undefined,
      selectedEventSummary: undefined as EventListItem | undefined,
      filter: {
        time: {
          enabled: false,
          extents: [0, 100]
        },
        intensity: {
          enabled: false,
          extents: [0, 100]
        },
        geo: {
          enabled: false,
          lat: 0,
          lon: 0,
          alt: 0,
          radius: 250
        },
        horizon: {
          enabled: false,
          above: false,
          below: false
        },
        clusterSize: {
          enabled: false,
          extents: [0,100]
        },
        tags: {
          enabled: true,
          // check all tags and make sure at least one is checked
          tags: []
        }
      } as PointSourceFilter,
      timer: undefined as NodeJS.Timeout | undefined
    }
  },
  mounted(): void {
    this.PSExtents = this.$store.state.eventModule.pointSourceFilterExtents;

    this.$store.watch(
      (state: RootState) => state.eventModule.pointSourceFilterExtents,
      (newExtents) => {
        this.PSExtents = newExtents;
        this.resetFilters();
      }
    );
    this.$store.watch(
      (state: RootState) => state.eventModule.selectedEventSummary,
      (selectedEventSummary: EventListItem) => {
        this.selectedEventSummary = selectedEventSummary;
        this.resetFilters();
      }
    );
  },
  methods: {
    sortTags: R.sort((a: string, b: string) => a < b ? -1 : a > b ? 1 : 0),
    debounce(func, timeout = 500) {
      return (...args) => {
        clearTimeout(this.timer);
        this.timer = setTimeout(() => { func.apply(this, args); }, timeout);
      };
    },
    applyFilters(): void {
      const filter = R.clone(this.filter);
      filter.time.extents = filter.time.extents.map(value => value / 1000);
      filter.geo.radius = this.filter.geo.radius * 1000;
      filter.intensity.extents = [parseFloat(this.lowIntensity), parseFloat(this.highIntensity)];
      this.$store.dispatch(MESSAGE_ACTIONS.CHANGE_POINT_SOURCE_FILTER, filter);
    },
    formatDate(mssue: number, format = 'yy/MM/dd (DDD) HH:mm:ss'): string {
      const date = new Date(mssue);
      if (isNaN(date.getTime())) {
        return 'no time';
      } else {
        return formatUTC(format, date);
      }
    },
    resetFilters() {
      if (this.PSExtents) {
        this.filter.time.extents = [this.PSExtents.minTime, this.PSExtents.maxTime];
        // the slider needs to go between [0, 100]
        this.filter.intensity.extents = [0, 100];
        this.filter.clusterSize.extents = [this.PSExtents.minClusterSize, this.PSExtents.maxClusterSize];
      }
      if (this.selectedEventSummary) {
        if (this.selectedEventSummary.location_lat_lon_alt_m) {
          this.filter.geo.lat = toFixed5(this.selectedEventSummary.location_lat_lon_alt_m[0]);
          this.filter.geo.lon = toFixed5(this.selectedEventSummary.location_lat_lon_alt_m[1]);
          this.filter.geo.alt = this.selectedEventSummary.location_lat_lon_alt_m[2];
        } else {
          this.filter.geo.lat = 0;
          this.filter.geo.lon = 0;
          this.filter.geo.alt = 3000;
        }
        this.filter.geo.enabled = false;
        this.filter.geo.radius = 250;

        this.filter.clusterSize.enabled = false;
        this.filter.time.enabled = false;
        this.filter.intensity.enabled = false;

        this.filter.horizon.enabled = false;
        this.filter.horizon.above = false;
        this.filter.horizon.below = false;

        this.filter.tags.enabled = true;
        this.filter.tags.tags = this.defaultTags;
      }
    }
  },
  watch: {
    filter: {
      deep: true,
      handler() {
        this.debounce(this.applyFilters)();
      }
    }
  },
  computed: {
    detailView(): boolean {
      return this.$store.state.eventModule.detailView;
    },
    minTime(): number {
      return Math.floor(this.PSExtents.minTime);
    },
    maxTime(): number {
      return Math.ceil(this.PSExtents.maxTime);
    },
    minIntensity(): number {
      return roundDown(this.PSExtents.minIntensity);
    },
    maxIntensity(): number {
      return roundUp(this.PSExtents.maxIntensity);
    },
    minClusterSize(): number {
      return this.PSExtents.minClusterSize || 0;
    },
    maxClusterSize(): number {
      return this.PSExtents.maxClusterSize || 1;
    },
    allTags(): string[] {
      return this.PSExtents.tags;
    },
    defaultTags(): string[] {
      return this.allTags.filter(x => DEFAULT_TAGS.includes(x)).length > 0 ? DEFAULT_TAGS : this.allTags;
    },
    pointCount(): number | undefined {
      const sightings = this.$store.state.eventModule.event?.sightings;
      if (sightings) {
        // @ts-ignore
        return R.pipe(
          Object.values,
          // @ts-ignore
          R.map(R.prop('length')),
          R.sum
        )(sightings);
      } else {
        return undefined;
      }
    },
    lowIntensity(): string {
      return (this.filter.intensity.extents[0] / 100 * (this.maxIntensity - this.minIntensity) + this.minIntensity).toPrecision(2);
    },
    highIntensity(): string {
      return (this.filter.intensity.extents[1] / 100 * (this.maxIntensity - this.minIntensity) + this.minIntensity).toPrecision(2);
    },
    lowTime(): string {
      return this.formatDate(this.filter.time.extents[0]);
    },
    highTime(): string {
      return this.formatDate(this.filter.time.extents[1]);
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

.filter-card-container {
  color: $white;
  display: flex;
  flex-direction: column;
  user-select: none;
  position: relative;
}
.top {
  top: 0;
}
.z-index {
  z-index: 999;
}
.reset-btn {
  display: flex;
  align-items: center;
  justify-content: center;
}
.filter-card-container > div {
  padding: 0.7em;
  margin: 0.3em;
  background: #333;
  font-size: 0.85rem;
}

label {
  color: $white;
  white-space: nowrap;
}
.white {
  color: $white;
}
.nowrap {
  white-space: nowrap;
}
ul {
  margin-top: 0;
  list-style: none;
  padding-left: 1em;
  color: $white;
}
.slider {
  margin-top: 1em;
}
.slider-container {
  padding: 0 25px;
  margin-bottom: 10px;
}
.geo-flex > label {
  margin-left: 1em;
}
.geo-flex {
  display: flex;
  justify-content: space-between;
}
.geo-flex > input {
  width: 50%;
}
.w100 {
  width: 100%;
}
.p5 {
  padding: 5px;
}
.mt10 {
  margin-top: 10px;
}
.mb1 {
  margin-bottom: 1em;
}
.mb5 {
  margin-bottom: 5px;
}
.m0 {
  margin: 0;
}
.mr {
  margin-right: 4px;
}
.flex {
  display: flex;
}
.space-between {
  justify-content: space-between;
}
.flex-column {
  flex-direction: column;
}
.align-center {
  align-items: center;
}
.space-between {
  justify-content: space-between;
}
.content-center {
  justify-content: center;
}
.flex-row {
  display: flex;
  justify-content: space-between;
  flex-direction: row;
  flex-wrap: wrap;
}
.w5ch {
  width: 5ch;
}
.inline-block {
  display: inline-block;
}
.fixed {
  position: sticky;
  bottom: 0;
  right: 0;
  left: 0;
}
.h100 {
  height: 100%;
}
.relative {
  position: relative;
}
.filter-controls {
  background: #222;
  width: 100%;
  padding: 4px 0;
  border-top: 1px solid #333;
}
.text-small {
  font-size: 0.7rem;
}
.z-index {
  z-index: 10;
}
.overflow-ellipsis {
  text-overflow: ellipsis;
  overflow: hidden;
}
</style>
