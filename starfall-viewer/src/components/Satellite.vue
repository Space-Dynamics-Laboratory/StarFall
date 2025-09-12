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
  <div>
    <table>
      <tbody>
      <tr>
        <th>Platform Name</th>
        <th>Sensor Name</th>
        <th>FOV (&#176;)</th>
        <th>Lat (&#176;)</th>
        <th>Lon (&#176;)</th>
        <th>Alt (km)</th>
        <th>Color</th>
        <th>Plot</th>
        <th>Show</th>
        <th>Fly To</th>
      </tr>
      <template v-for="platform in platforms" :key="`platform${platform.id}`">
        <!-- platform -->
        <tr class="platform">
          <td>{{ platform.name }} </td>
          <td> <!-- sensor name --> </td>
          <td> <!-- fov --> </td>
          <td>{{ platform.posLatLonAlt ? platform.posLatLonAlt[0].toFixed(1) : "unknown" }}</td>
          <td>{{ platform.posLatLonAlt ? platform.posLatLonAlt[1].toFixed(1) : "unknown" }}</td>
          <td>{{ platform.posLatLonAlt ? (platform.posLatLonAlt[2] / 1000000).toFixed(1) : "unknown" }}</td>
          <td> <!-- color --> </td>
          <td> <!-- plot --> </td>
          <td> <input type="checkbox" :ref="`showPlatform${platform.id}`" @click="showHidePlatform($event, platform)" /> </td>
          <td>
            <button @click="flyToPlatform(platform)" class="fly-to-button">
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-send"><line x1="22" x2="11" y1="2" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            </button>
          </td>
        </tr>
        <!-- sensors -->
        <tr class="sensor" v-for="sensor, i in platform.sensors" :key="`sensor${sensor.id}-${platform.id}-${i}`">
          <td> <!-- platform name --> </td>
          <td> {{ sensor.name }} </td>
          <td> {{ sensor.fov }} </td>
          <td> <!-- lat --> </td>
          <td> <!-- lon --> </td>
          <td> <!-- alt --> </td>
          <td :style="backgroundColor(sensor.id)"></td>
          <td>
            <input
              type="checkbox"
              :checked="getSensorPlot(sensor.id)"
              @click="showHideSensorPlot($event, sensor)"
            />
          </td>
          <td>
            <input
              v-if="sensor.fov !== null"
              type="checkbox"
              @click="showHideFov(sensor, platform)"
            />
          </td>
          <td> <!-- fly to --> </td>
        </tr>

        <!-- sensor -->
      </template>
    </tbody>
    </table>

  </div>
</template>

<script lang="ts">
import { Color, SceneMode } from 'cesium';
import { MUTATIONS as EVENT_MUTATIONS } from '@/store/modules/EventModule';
import { MUTATIONS as SETTINGS_MUTATIONS } from '@/store/modules/SettingsModule';
import type { Platform } from '@/types/Platform';
import type { Sensor } from '@/types/Sensor';
import { getSensorColor } from '@/store/Helpers/getSensorColor';
import { getSensorLine } from '@/store/Helpers/getSensorLine';

export default {
  name: 'Satellite',
  computed: {
    platforms(): Platform[] {
      return this.$store.state.eventModule.eventPlatforms;
    }
  },
  methods: {
    isThreeDScene(): boolean {
      return this.$store.state.eventModule.mainScene?.mode === SceneMode.SCENE3D;
    },
    getSensorPlot(id: number): boolean {
      return getSensorLine(id);
    },
    flyToPlatform(platform: Platform): void {
      if (this.isThreeDScene()) {
        this.$store.commit(EVENT_MUTATIONS.UNLOCK_VIEW);
        this.$store.commit(EVENT_MUTATIONS.FLY_TO_PLATFORM, platform);
      }
    },
    backgroundColor(sensorId: number): string {
      const color: Color = getSensorColor(sensorId);
      return `background-color: rgba(${color.red * 255},${color.green * 255},${color.blue * 255},1)`;
    },
    showHidePlatform(event: Event, platform: Platform): void {
      // TODO: bind values with v-model
      const show = (event.target as HTMLInputElement).checked;
      this.$store.commit(EVENT_MUTATIONS.SHOW_HIDE_PLATFORM, { platform, show });
    },
    showHideSensorPlot(event: Event, sensor: Sensor): void {
      // TODO: bind values with v-model
      const show = (event.target as HTMLInputElement).checked;
      this.$store.commit(SETTINGS_MUTATIONS.SET_SENSOR_LINE, { id: sensor.id, line: show });
    },
    showHideFov(sensor: Sensor, platform: Platform): void {
      // TODO: don't use refs, bind values with v-model
      const showPlatform = ((this.$refs[`showPlatform${platform.id}`] as HTMLElement[])[0] as HTMLInputElement).checked;
      this.$store.commit(EVENT_MUTATIONS.SHOW_HIDE_FOV, { showPlatform, sensor, platform });
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';
@import '@/assets/scss/table.scss';

input {
  cursor: pointer;
}
.platform {
  // background: $light-grey-2 !important;
}
.sensor {
  // background: $white !important;
}
.fly-to-button {
  display: inline-flex;
  align-items: center;
  margin: 0;
  padding: 2px;
}
</style>
