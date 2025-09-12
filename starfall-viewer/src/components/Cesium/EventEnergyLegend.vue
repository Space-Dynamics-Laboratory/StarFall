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
  <div id="container" v-if="show">
    <div id="gradient"/>
    <div id="ytick-container">
      <p class="ytick" v-for="(tick, index) in yticks()" :key="index">{{tick}}</p>
    </div>
  </div>
</template>

<script lang="ts">

export default {
  name: 'EventEnergyLegend',
  methods: {
    show(): boolean {
      return !this.$store.state.eventModule.detailView;
    },
    yticks(): string[] {
      const min = this.$store.state.eventModule.energyGradient.minPos;
      const max = this.$store.state.eventModule.energyGradient.maxPos;
      const n = 5;
      const step = (max - min) / n;
      const ticks = [];
      for (let i = 0; i <= n; ++i) {
        const pos = min + step * i;
        const val = this.$store.state.eventModule.energyGradient.value(pos);
        ticks.push((val).toExponential(1));
      }
      return ticks.reverse();
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

#container {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  width: 70px;
  height: 40%;
  margin: 3px;
  background: #303336;
  border: 1px solid #444;
  border-radius: 4px;
}
#gradient {
  position: absolute;
  right: 2px;
  top: 50%;
  transform: translateY(-50%);
  height: 90%;
  width: 33%;
  background: linear-gradient(
    $energy-gradient-8, $energy-gradient-7,
    $energy-gradient-6, $energy-gradient-5,
    $energy-gradient-4, $energy-gradient-3,
    $energy-gradient-2, $energy-gradient-1);
}
#ytick-container {
  color: white;
  position: absolute;
  left: 2px;
  top: 50%;
  transform: translateY(-50%);
  height: 90%;
  text-align: right;
  display: flex;
  flex-flow: column nowrap;
  justify-content: space-between;
  font-size: 8pt;
}
.ytick {
  margin: 0;
  padding: 0;
}

</style>
