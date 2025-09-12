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
  <h2>Plot Settings</h2>
  <div class="platform">
    <div class="platform-info">
      <div class="platform-name">
        Platform
      </div>
    </div>
    <div class="sensors">
      <div class="sensor">
        <div class="sensor-name">Sensor</div>
        <div class="sensor-color">Color</div>
        <div class="sensor-point-shape">Point Shape</div>
      </div>
    </div>
  </div>
  <hr>
  <div class="platforms">
    <div v-for="platform in platforms" :key="platform.id">
      <div class="platform">
        <div class="platform-info">
          <div class="platform-name">
            {{ platform.name }}
          </div>
        </div>
        <div class="sensors">
          <div v-for="sensor in platform.sensors" :key="sensor.id" class="sensor">
            <div class="sensor-name">{{ sensor.name }}</div>
            <div class="sensor-color">
              <input type="color" :value="getColor(sensor.id)" @change="updateColor(sensor, $event)" class="pointer">
            </div>
            <div class="sensor-point-shape">
              <select :value="getPointShape(sensor.id)" @change="updatePointShape(sensor, $event)">
                <option :value="pointShapes.circle" class="circle">&#x25CF;</option>
                <option :value="pointShapes.square" class="square">&#x25A0;</option>
                <option :value="pointShapes.diamond" class="diamond">&#9670;</option>
                <option :value="pointShapes.triangle" class="triangle">&#x25B2;</option>
                <option :value="pointShapes.down_triangle" class="down-triangle">&#x25BC;</option>
                <option :value="pointShapes.left_triangle" class="left-triangle">&#x25C0;</option>
                <option :value="pointShapes.right_triangle" class="right-triangle">&#x25B6;</option>
                <option :value="pointShapes.plus" class="plus">&plus;</option>
                <option :value="pointShapes.times" class="times">&#x2716;</option>
                <option :value="pointShapes.vertical_line" class="vertical_line">&#x2759;</option>
                <option :value="pointShapes.horizontal_line" class="horizontal_line">&#x2015;</option>
              </select>
            </div>
          </div>
        </div>
      </div>
      <hr>
    </div>
  </div>
</div>
</template>

<script lang="ts">
import { ACTIONS as MESSAGE_ACTIONS } from '@/store/modules/MessageModule';
import { ColorGenerator } from '@/components/Cesium/CesiumDrawingHandlers/ColorGenerator';
import { MUTATIONS as SETTINGS_MUTATIONS, PointShape } from '@/store/modules/SettingsModule';
import type { Platforms } from 'starfall-common/Types/Platforms';
import { getSensorColor } from '@/store/Helpers/getSensorColor';
import { getSensorPointShape } from '@/store/Helpers/getSensorPointShape';
import type { Sensor } from 'starfall-common/Types/Sensors';

export default {
  name: 'PlotSettings',
  computed: {
    pointShapes: () => PointShape,
    platforms(): Platforms {
      return Object.values(this.$store.state.eventModule.platforms).sort(
        (a, b) =>
          a.name > b.name
            ? 1
            : a.name < b.name
              ? -1
              : 0);
    }
  },
  methods: {
    updateColor(sensor: Sensor, event: { target: HTMLInputElement }): void {
      const color = ColorGenerator.HextoRGB(event.target.value);
      if (color) {
        this.$store.commit(SETTINGS_MUTATIONS.SET_SENSOR_COLOR, { id: sensor.id, color: { red: color.r / 255, green: color.g / 255, blue: color.b / 255, alpha: 0.5 } });
      }
    },
    getColor(id: number): string {
      const color = getSensorColor(id);
      return ColorGenerator.RGBToHex(Math.round(color.red * 255), Math.round(color.green * 255), Math.round(color.blue * 255));
    },
    updatePointShape(sensor: Sensor, event: { target: HTMLInputElement }):void {
      this.$store.commit(SETTINGS_MUTATIONS.SET_SENSOR_POINT_SHAPE, { id: sensor.id, shape: event.target.value });
    },
    getPointShape(id: number): string {
      return getSensorPointShape(id);
    },
  },
  mounted() {
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
  font-size: 14px;
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
  align-items: center;
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
.sensor-name {
  flex: 0.5;
}
.sensor-color {
  flex: 0.5;
}
.sensor-point-shape {
  flex: 0.5;
  height: 27px;
}
input, select {
  height: 2em;
  width: 4em;
}
option {
  font-size: 20px;
}
hr {
  margin: 0;
  padding: 0;
  border: none;
  border-top: 1px solid #999;
}
.pointer {
  cursor: pointer;
}
.modal h2, .content h2 {
  margin-top: 0;
  padding-top: 0;
  margin-right: 20px;
}

</style>
