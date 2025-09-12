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
    <div v-for="(sensor, index) in sensors" :key="index" class="m5 flex">
      <svg class="mt2 w12 mr5" height="12" width="12">
        <circle
          v-if="sensor.shape === pointShapes.circle"
          r="4" cx="5" cy="5"
          :fill="getFill(sensor)"
          :stroke="getStroke(sensor)"
          :stroke-width="getStrokeWidth(sensor)"
        />
        <polygon
          v-else
          :points="getPoints(sensor.shape)"
          :fill="getFill(sensor)"
          :stroke="getStroke(sensor)"
          :stroke-width="getStrokeWidth(sensor)"
        />
      </svg>
      <span style="word-wrap: anywhere; line-height: 10pt; font-size: 10pt;">{{ sensor.name }}</span>
    </div>
  </div>
</template>

<script lang="ts">
import { Color } from 'cesium';
import { getSensorColor } from '@/store/Helpers/getSensorColor';
import { PointShape } from '@/store/modules/SettingsModule';
import { getSensorPointShape } from '@/store/Helpers/getSensorPointShape';
import { getSensorLine } from '@/store/Helpers/getSensorLine';

type sensorInfo = {
  id: number;
  name: string;
  color: Color;
  shape: PointShape;
  line: boolean;
};

const PointShapeMap = {
  [PointShape.square]: '1,1 9,1 9,9 1,9',
  [PointShape.diamond]: '5,1 8,5 5,9 2,5',
  [PointShape.triangle]: '5,2 9,9 1,9',
  [PointShape.down_triangle]: '1,1 9,9 1,9',
  [PointShape.left_triangle]: '2,5 9,1 5,8',
  [PointShape.right_triangle]: '1,1 8,5 1,9',
  [PointShape.plus]: '1,4 4,4 4,1 6,1 6,4 9,4 9,6 6,6 6,9, 4,9 4,6 1,6',
  [PointShape.times]: '1,3 3,1 5,3 7,1 9,3 6,5 9,7 7,9 5,7 3,9 1,7 3,5',
  [PointShape.vertical_line]: '4,1 6,1 6,9 4,9',
  [PointShape.horizontal_line]: '1,4 9,4 9,6 1,6',
  [PointShape.circle]: '' // not an svg polygon, handle as svg circle
};

export default {
  name: 'EnergyLegend',
  methods: {
    getPoints(shape: PointShape): string {
        return PointShapeMap[shape];
      },
    getFill(sensor: sensorInfo): string {
      if (sensor.line === false) {
        return '#f1f1f1';
      }
      return `rgb(${sensor.color.red * 255},${sensor.color.green * 255},${sensor.color.blue * 255})`;
    },
    getStroke(sensor: sensorInfo): string {
      if (sensor.line === false) {
        return `rgb(${sensor.color.red * 255},${sensor.color.green * 255},${sensor.color.blue * 255})`;
      }
      return '#424949';
    },
    getStrokeWidth(sensor: sensorInfo): string {
      if (sensor.line === false) {
        return '20%';
      }
      return '';
    }
  },
  computed: {
    pointShapes: () => PointShape,
    sensors(): sensorInfo[] {
      const sensorInfos: sensorInfo[] = [];
      this.$store.state.eventModule.eventPlatforms.forEach(platform => {
        platform.sensors.forEach(sensor => {
          // check if sensor has point sources
          if (this.$store.state.eventModule.event !== null
            && Object.values(this.$store.state.eventModule.event.sightings)
              .find(pointsources => pointsources[0].sensor_id === sensor.id) === undefined) {
            return;
          }
          sensorInfos.push({
            id: sensor.id,
            name: platform.name + ' ' + sensor.name,
            color: getSensorColor(sensor.id),
            shape: getSensorPointShape(sensor.id),
            line: getSensorLine(sensor.id)
          });
        });
      });
      return sensorInfos;
    }
  }
}

</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

.flex {
  display: flex;
}
.m5 {
  margin: 5px;
}
.mr5 {
  margin-right: 5px;
}
.mt2 {
  margin-top: 2px;
}
.w12 {
  width: 12px;
}
</style>
