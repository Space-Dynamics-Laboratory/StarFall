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
  <div class="flex space-between">
    <h3 class="m0 mb1">Date Filter</h3>
    <div>
      <input class="toggle" id="filter-by-date" name="filter-by-date" type="checkbox" checked="false" @input="onEnabledChanged" v-model="enabled">
      <label class="sr-only" for="filter-by-date">Enable</label>
    </div>
  </div>

  <div class="flex space-between align-center mb1">
    <div>
      <div class="label">Start Date</div>
      <div
        class="mt8"
      >
      {{ dateLow }}
      </div>
    </div>

    <div>
      <div class="label align-right w100 inline-block">End Date</div>
      <div
        class="mt8"
      >
        {{ dateHigh }}
      </div>
    </div>
  </div>

  <Slider 
    v-model="sliderValue"
    :disabled="!enabled"
    :min="lowerBound"
    :max="upperBound"
    :tooltips="false"
    @change="storeFilter"
  />
</div>
</template>

<script lang="ts">
import * as R from 'ramda';
import Slider from '@vueform/slider';
import { ACTIONS as EVENT_ACTIONS } from '@/store/modules/EventModule';
import type { DateFilter as DateFilter_t } from 'starfall-common/Types/EventFilter';
import type { PageData } from 'starfall-common/Types/Paging';
import type { RootState } from '@/types/RootState';
import { formatUTC } from 'starfall-common/helpers/time';

const SEC_IN_DAY = 86400;

export default {
  name: 'DateFilter',
  components: {
    Slider
  },
  data() {
    return {
      lowerBound: Date.now() / 1000,
      upperBound: Date.now() / 1000,
      sliderValue: [Date.now() / 1000, Date.now() / 1000],
      enabled: false,
    }
  },
  mounted() {
    this.reset();
    this.$store.watch(
      (state: RootState) => state.eventModule.eventList,
      (value: PageData) => this.updateBounds(value)
    );
  },
  methods: {
    onEnabledChanged(e: Event): void {
      this.enabled = (e.target as HTMLInputElement).checked;
      this.storeFilter();
    },
    reset(): void {
      this.enabled = false;
      this.sliderValue = [this.lowerBound, this.upperBound]
      this.storeFilter();
    },
    storeFilter(value): void {
      const filter = R.clone(this.$store.state.eventModule.eventFilter);
      filter.approx_trigger_time.lte = value ? value[1] : this.sliderValue[1];
      filter.approx_trigger_time.gte = value ? value[0] : this.sliderValue[0];
      filter.approx_trigger_time.enabled = this.enabled;
      this.$store.dispatch(EVENT_ACTIONS.SET_EVENT_FILTER, filter);
    },
    updateBounds(events: PageData): void {
      if (events === undefined || !events.minDate || !events.maxDate) {
        return;
      }
      let min = events.minDate;
      let max = events.maxDate;

      // provide a day cushion on the filter
      // to catch the events the ends
      min -= SEC_IN_DAY;
      max += SEC_IN_DAY;

      if (min === this.lowerBound || max === this.upperBound) {
        return;
      }
      this.lowerBound = min;
      this.upperBound = max;
      this.sliderValue = [this.lowerBound, this.upperBound]
    },
    loadFilterSetting(filter: DateFilter_t): void {
      this.low = filter.gte;
      this.high = filter.lte;
    },
    sliderInput(values: {low: number, high: number}): void {
      this.sliderValue = [values.low, values.high]
    },
    sliderChange(values: {low: number, high: number}): void {
      this.sliderValue = [values.low, values.high]
      // move this to sliderInput() to update the globe every time
      // the slider changes value instead of when the user lets go
      this.storeFilter();
    },
    msToDateString(ms: number): string {
      const date = new Date(0);
      date.setUTCMilliseconds(ms);
      return formatUTC('y-MM-dd', date);
    }
  },
  computed: {
    low: {
      get(): number {
        return this.sliderValue[0];
      },
      set(val: number) {
        this.sliderValue[0] = val;
      }
    },
    high: {
      get(): number {
        return this.sliderValue[1];
      },
      set(val: number) {
        this.sliderValue[1] = val;
      }
    },
    dateLow: {
      get(): string {
        const date = new Date(0);
        date.setUTCSeconds(this.low);
        return formatUTC('y-MM-dd', date);
      },
      set(date: string) {
        const y = parseInt(date.substring(0, 4));
        const m = parseInt(date.substring(5, 7)) - 1;
        const d = parseInt(date.substring(8, 10));
        const val = Date.UTC(y, m, d);
        console.log(y, m, d, val);
        if (val > this.high) {
          this.high = val;
        }
        this.low = val;
      }
    },
    dateHigh: {
      get(): string {
        const date = new Date(0);
        date.setUTCSeconds(this.high);
        return formatUTC('y-MM-dd', date);
      },
      set(date: string) {
        const y = parseInt(date.substring(0, 4));
        const m = parseInt(date.substring(5, 7)) - 1;
        const d = parseInt(date.substring(8, 10));
        const val = Date.UTC(y, m, d) + 86399999;
        if (val < this.low) {
          this.low = val;
        }
        this.high = val;
      }
    }
  }
}

</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

.label {
  font-weight: 600;
  font-size: 0.8em;
  text-transform: uppercase;
}
.mt8 {
  margin-top: 4px;
}
.off-white {
  color: $off-white;
}
.flex {
  display: flex;
}
.space-between {
  justify-content: space-between;
}
.align-center {
  align-items: center;
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
