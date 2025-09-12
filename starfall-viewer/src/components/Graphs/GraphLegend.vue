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
      <svg height="12" width="12" class="mt2 w12 mr5">
        <circle r="4" cx="5" cy="5"
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
import { getSensorLine } from '@/store/Helpers/getSensorLine';
import type { PropType } from 'vue';

type sensorInfo = {
  id: number;
  name: string;
  color: Color;
  line: boolean;
};

export default {
  name: 'GraphLegend',
  props: {
    sensorIds: {
      type: Object as PropType<Set<number>>,
      required: true
    }
  },
  methods: {
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
    sensors(): sensorInfo[] {
      if (this.$store.state.eventModule.eventPlatforms.length === 0) return [];
      const sensorInfos: sensorInfo[] = [];
      this.$store.state.eventModule.eventPlatforms.forEach(platform => {
        platform.sensors.forEach(sensor => {
          if (this.sensorIds.has(sensor.id)) {
            sensorInfos.push({
              id: sensor.id,
              name: platform.name + ' ' + sensor.name,
              color: getSensorColor(sensor.id),
              line: getSensorLine(sensor.id)
            });
          }
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
