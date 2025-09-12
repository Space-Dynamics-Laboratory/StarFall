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
  <div class="inner-legend-container" v-show="hasSatellites">
    <div v-for="(sensor, index) in sensors" :key="index" class="legend-item">
      <svg height="10" width="10" class="dot">
        <circle r="4" cx="5" cy="5"
          :fill="getFill(sensor)"
          :stroke="getStroke(sensor)"
          :stroke-width="getStrokeWidth(sensor)"
        />
      </svg>
      <p>{{ sensor.name }}</p>
    </div>
    <div class="legend-item">
      <hr />
    </div>
    <div class="legend-item">
      <svg height="10" width="10" class="dot">
        <circle r="4" cx="5" cy="5"
          :fill="getFill(sensors[0])"
          fill-opacity="25%"
          :stroke="getStroke(sensors[0])"
          stroke-opacity="25%"
        />
      </svg>
      <p>{{ formatUTC(timeMin) }}</p>
    </div>
    <div class="legend-item">
      <svg height="10" width="10" class="dot">
        <circle r="4" cx="5" cy="5"
          :fill="getFill(sensors[0])"
          :stroke="getStroke(sensors[0])"
        />
      </svg>
      <p>{{ formatUTC(timeMax) }}</p>
    </div>
  </div>
</template>

<script lang="ts">
import ecef from 'starfall-common/ecef';
import { Color } from 'cesium';
import type { PointSource } from '@/types/PointSource';
import { getSensorColor } from '@/store/Helpers/getSensorColor';
import { getSensorLine } from '@/store/Helpers/getSensorLine';
import { formatUTC } from 'starfall-common/helpers/time';

function getNearAlt(ps: PointSource): number {
  return ecef.unproject(ps.meas_near_point_ecef_m)[2];
}

function getFarAlt(ps: PointSource): number {
  return ecef.unproject(ps.meas_far_point_ecef_m)[2];
}

type sensorInfo = {
  id: number;
  name: string;
  color: Color;
  line: boolean;
};

export default {
  name: 'EnergyLegend',
  props: {
    timeMin: Number,
    timeMax: Number
  },
  methods: {
    getFill(sensor: sensorInfo): string {
      if (!sensor) return '';
      if (sensor.line === false) {
        return '#f1f1f1';
      }
      return `rgb(${sensor.color.red * 255},${sensor.color.green * 255},${sensor.color.blue * 255})`;
    },
    getStroke(sensor: sensorInfo): string {
      if (!sensor) return '';
      if (sensor.line === false) {
        return `rgb(${sensor.color.red * 255},${sensor.color.green * 255},${sensor.color.blue * 255})`;
      }
      return '#424949';
    },
    getStrokeWidth(sensor: sensorInfo): string {
      if (!sensor) return '';
      if (sensor.line === false) {
        return '20%';
      }
      return '';
    },
    formatUTC(time) {
      return formatUTC('HH:mm:ss.SS', time);
    }
  },
  computed: {
    hasSatellites(): boolean {
      return this.$store.state.eventModule.eventPlatforms.length !== 0;
    },
    sensors(): sensorInfo[] {
      if (this.$store.state.eventModule.eventPlatforms.length === 0) return [];
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
            line: getSensorLine(sensor.id)
          });
        });
      });
      return sensorInfos;
    },
    nearAlt(): string | undefined {
      if (this.$store.state.eventModule.event) {
        const nearAlt = Object.values(this.$store.state.eventModule.event.sightings)
          .reduce((acc, sighting: PointSource[]) =>
            Math.max(acc, sighting.length > 0 ? getNearAlt(sighting[0]) : -Number.MAX_VALUE), -Number.MAX_VALUE);
        return nearAlt.toFixed(1) + ' m'; // ecef.unproject(Object.values(this.$store.state.eventModule.event.sightings)[0][0].meas_near_point_ecef_m)[2].toFixed(1) + ' m';
      }
      return undefined;
    },
    farAlt(): string | undefined {
      if (this.$store.state.eventModule.event) {
        const farAlt = Object.values(this.$store.state.eventModule.event.sightings)
          .reduce((acc, sighting: PointSource[]) =>
            Math.min(acc, sighting.length > 0 ? getFarAlt(sighting[0]) : Number.MAX_VALUE), Number.MAX_VALUE);
        return farAlt.toFixed(1) + ' m'; // ecef.unproject(Object.values(this.$store.state.eventModule.event.sightings)[0][0].meas_far_point_ecef_m)[2].toFixed(1) + ' m';
      }
      return undefined;
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

p {
  font-size: 10pt;
  display: inline;
}

.inner-legend-container {
  width: 100px;
  height: 100%;
  background-color: $white;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.legend-item {
  margin: 2px;
}

.dot {
  margin-right: 5px;
}
</style>
