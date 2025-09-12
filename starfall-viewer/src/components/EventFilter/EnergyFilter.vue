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
  <div class="flex space-between mb1">
    <h3 class="m0">Energy Filter</h3>
    <div>
      <input class="toggle" id="filter-by-energy" ref="enabled" type="checkbox" checked="false" @input="onEnabledChanged" v-model="enabled">
      <label class="sr-only" for="filter-by-energy">Enable</label>
    </div>
  </div>
  <!-- <div class="flex mb1">
    <input class="toggle" id="above-energy-threshold-check-box" ref="above-energy-threshold" type="checkbox" v-model="onlyAboveEnergyThreshold" :disabled="!enabled">
    <label class="text-small" for="above-energy-threshold-check-box">Only Above Energy Threshold Events</label>
  </div> -->

  <div class="flex space-between mb1">
    <div>
      <label class="label" for="filter-energy-low">Low</label><br/>
      <div
        id="filter-energy-low"
        class="mt8"
      >
        {{ sliderValue[0].toExponential(precision) }}
      </div>
    </div>

    <div>
      <label for="filter-energy-high" class="label align-right w100 inline-block">High</label><br/>
      <div
        id="filter-energy-high"
        class="mt8"
      >
        {{ sliderValue[1].toExponential(precision) }}
      </div>
    </div>
  </div>

  <LogScaleSlider 
    :key="sliderKey"
    v-model="sliderValue"
    :lowerBound="lowerBound"
    :upperBound="upperBound"
    :enabled="enabled"
    @change="storeFilter"
  />
</div>
</template>

<script lang="ts">
import * as R from 'ramda';
import LogScaleSlider from '../LogScaleSlider.vue';
import { ACTIONS as EVENT_ACTIONS } from '@/store/modules/EventModule';
import type { RootState } from '@/types/RootState';
import type { PageData } from 'starfall-common/Types/Paging';

export default {
  name: 'EnergyFilter',
  components: {
    LogScaleSlider
  },
  data() {
    return {
      precision: 2,
      lowerBound: 1,
      upperBound: 1e10,
      sliderValue: [1, 1e10],
      sliderKey: 0,
      onlyAboveEnergyThreshold: false,
      enabled: false,
    }
  },
  mounted() {
    this.$store.watch(
      (state: RootState) => state.eventModule.eventList,
      (value: PageData) => this.updateBounds(value)
    );
  },
  computed: {
  },
  methods: {
    reset(): void {
      this.enabled = false;
      this.sliderValue = [this.lowerBound, this.upperBound]
      this.sliderKey += 1;
      this.onlyAboveEnergyThreshold = false;
      this.storeFilter();
    },
    storeFilter(value): void {
      const filter = R.clone(this.$store.state.eventModule.eventFilter);
      filter.approx_energy_j.enabled = this.enabled;
      filter.approx_energy_j.lte = value ? value[1] : this.sliderValue[1];
      filter.approx_energy_j.gte = value ? value[0] : this.sliderValue[0];
      this.$store.dispatch(EVENT_ACTIONS.SET_EVENT_FILTER, filter);
    },
    updateBounds(events: PageData): void {
      const floor = events.minEnergy !== undefined ? Math.floor(events.minEnergy) : this.lowerBound;
      const ceil = events.maxEnergy !== undefined ? Math.ceil(events.maxEnergy) : this.upperBound;

      if (events === undefined || floor === this.lowerBound || ceil === this.upperBound) {
        return;
      }

      this.lowerBound = floor;
      this.upperBound = ceil;
      this.sliderValue = [floor, ceil]
    },
    onEnabledChanged(e: Event): void {
      this.enabled = (e.target as HTMLInputElement).checked;
      this.storeFilter();
    }
  },
  watch: {
    // TODO: Implement only above energy threshold filter
    // onlyAboveEnergyThreshold(value) {
    //   if (value) {
    //     const threshold = this.$store.state.settingsModule.energyThreshold;
    //     if (threshold) {
    //       this.lowerBound = threshold;
    //       this.upperBound = this.upperBound > threshold ? this.upperBound : threshold;
    //       this.sliderValue = [this.lowerBound, this.upperBound]
    //       this.storeFilter();
    //     }
    //   } else {
    //     this.updateBounds(this.$store.state.eventModule.eventList);
    //   }
    // }
  }
}
</script>

<style src="@vueform/slider/themes/default.css"></style>
<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

.label {
  font-weight: 700;
  font-size: 0.8em;
  text-transform: uppercase;
}
.text-small {
  font-size: 0.8em;
}
.mt8 {
  margin-top: 4px;
}
.white {
  color: $white;
}
.flex {
  display: flex;
  align-items: center;
}
.space-between {
  justify-content: space-between;
}
.mt5 {
  margin-top: 1em;
}
.p5 {
  padding: 1em;
}
.m0 {
  margin: 0;
}
.mb1 {
  margin-bottom: 1em;
}
.align-right {
  text-align: right;
}
.w100 {
  width: 100%;
}
.inline-block {
  display: inline-block;
}
</style>
