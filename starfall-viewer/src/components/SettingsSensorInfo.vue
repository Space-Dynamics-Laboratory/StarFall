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
<div class="content">
  <h2>Sensor Information Settings</h2>
  <div class="platform">
    <div class="platform-info">
      <div class="platform-name">
        Platform
      </div>
    </div>
    <div class="sensors">
      <div class="sensor">
        <div class="sensor-name">Sensor</div>
        <div class="sensor-fov">Field of View (&#176;)</div>
      </div>
    </div>
  </div>
  <hr>
  <div class="platforms">
    <div class="platform-container" v-for="platform in sortPlatforms(platforms)" :key="platform.id">
      <div class="platform">
        <div class="platform-info">
          <div class="platform-name">
            <input type="text" :value="platform.name" @change="setPlatformName(platform.id, $event)">
          </div>
        </div>
        <div class="sensors">
          <div v-for="sensor in sortSensors(platform.sensors)" :key="sensor.id" class="sensor">
            <div><input type="text" class="sensor-name" :value="sensor.name" @change="setSensorName(platform.id, sensor.id, $event)"></div>
            <div><input type="number" class="sensor-fov" :value="sensor.fov" @change="setSensorFov(platform.id, sensor.id, $event)"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <hr>
  <div class="buttons">
    <button class="btn-base submit button" @click="save">Save</button>
  </div>
</div>
</template>

<script lang="ts">
import * as R from 'ramda';
import { ACTIONS as MESSAGE_ACTIONS } from '@/store/modules/MessageModule';
import { MUTATIONS as POPUP_MUTATIONS } from '@/store/modules/PopupsModule';
import type { Platforms } from 'starfall-common/Types/Platforms';
import type { Sensors } from 'starfall-common/Types/Sensors';
import type { RootState } from '@/types/RootState';

const sortByName: (p: any) => any =
  R.pipe(
    Object.values,
    R.sort(R.ascend(R.prop('name')))
  );

export default {
  name: 'SettingsSensorInfo',
  data() {
    return {
      unwatch: null as (() => void) | null,
      platforms: {} as Platforms,
    }
  },
  methods: {
    sortByName,
    sortPlatforms: sortByName,
    sortSensors: sortByName,
    save(): void {
      this.$store.commit(POPUP_MUTATIONS.CREATE_CONFIRMATION_POPUP, {
        title: 'Change Sensor Information',
        message: 'This will change the names and FOVs stored in the database, do you want to continue?',
        confirmButtonText: 'Continue',
        cancelButtonText: 'Cancel',
        onConfirm: () => {
          this.$store.dispatch(MESSAGE_ACTIONS.UPDATE_PLATFORMS_IN_DATABASE, this.platforms);
          this.$parent?.$emit('toggle-modal');
        }
      });
    },
    setPlatformName(platformId: number, event: Event): void {
      const name = (event.target as HTMLInputElement).value;
      this.platforms[platformId].name = name;
    },
    setSensorName(platformId: number, sensorId: number, event: Event): void {
      const name = (event.target as HTMLInputElement).value;
      this.platforms[platformId].sensors[sensorId].name = name;
    },
    setSensorFov(platformId: number, sensorId: number, event: Event): void {
      const fov = Number.parseFloat((event.target as HTMLInputElement).value);
      this.platforms[platformId].sensors[sensorId].fov = fov;
    },
  },
  mounted(): void {
    this.unwatch = this.$store.watch(
      (state: RootState) => state.eventModule.platforms,
      (value) => {
        this.platforms = R.clone(value);
        if (this.unwatch) this.unwatch();
      }
    );
    this.$store.dispatch(MESSAGE_ACTIONS.GET_ALL_PLATFORMS);
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

.content {
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  height: 100%;
  width: 30vw;
  overflow-y: hidden;
  overflow-x: hidden;
  margin: 0px;
}
.platforms {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  overflow-y: auto;
}
.platform {
  display: flex;
  padding: 10px;
}
.platform-info {
  flex: 0.5;
  display: flex;
  flex-direction: column;
}
.platform-name {
  flex: 0.5;
  display: flex;
  align-items: flex-start;
  padding: 3px;
}
.sensors {
  flex: 1;
}
.sensor {
  display: flex;
  align-items: center;
  padding: 3px;
}
.sensor-name,
.sensor-fov {
  flex: 0.5;
}
hr {
  margin: 0;
  padding: 0;
  border: none;
  border-top: 1px solid #999;
}
.platform-container {
  border-bottom: 1px solid #999;
}
.platform-container:last-child {
  border: none;
}
.buttons {
  padding-top: 20px;
  display: flex;
  justify-content: center;
}
.button {
  margin: 0;
}
input {
  width: 80%;
}
.modal h2, .content h2 {
  margin-top: 0;
  padding-top: 0;
  margin-right: 20px;
}
</style>
