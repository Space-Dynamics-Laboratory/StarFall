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
<div class="scroll">
  <div class="flex space-between">
    <h3 class="m0">State Filter</h3>
    <div>
      <input
        class="toggle"
        type="checkbox"
        name="enabled"
        id="filter-by-state"
        :checked="filter.state_filter.enabled"
        @change="onEnableChanged"
      >
      <label class="sr-only" for="filter-by-state">Enable</label>
    </div>
  </div>
  <div class="height text-small" ><span v-if="filter.state_filter.enabled && filterCount > 0">{{ filterCount }} Selected</span></div>
  <ul class="checkbox-list">
    <li v-for="(state, i) in states" :key="state">
      <input
        type="checkbox"
        :name="state"
        :id="state"
        :disabled="!filter.state_filter.enabled || stateCount === undefined || !stateCount[state]"
        :checked="filter.state_filter[state]"
        @change="update($event, state)"
      >
      <label :for="state">
        {{ stateStr[state] }} <span v-if="stateCount">({{ stateCount[state] }})</span>
      </label>
    </li>
  </ul>
</div>
</template>

<script lang="ts">
import * as R from 'ramda';
import { ACTIONS as EVENT_ACTIONS, MUTATIONS as EVENT_MUTATIONS } from '@/store/modules/EventModule';
import { ProcessingState, stateStr } from 'starfall-common/Types/ProcessingState';
import type { StateCount } from 'starfall-common/Types/Paging';

type StateCountMap = {
  [key in ProcessingState]: number
};

export default {
  name: 'StateFilter',
  methods: {
    onEnableChanged(event: Event): void {
      const enabled = (event.target as HTMLInputElement).checked;
      const filter = R.clone(this.$store.state.eventModule.eventFilter);
      filter.state_filter.enabled = enabled;
      this.$store.dispatch(EVENT_ACTIONS.SET_EVENT_FILTER, filter);
    },
    update(event: Event, state: number): void {
      const checked = (event.target as HTMLInputElement).checked;

      const filter = R.clone(this.filter);
      filter.state_filter[state] = checked;

      // Automatically set `enabled` to true if any checkbox is checked
      filter.state_filter.enabled = Object.values(filter.state_filter)
        .filter(value => typeof value === 'boolean') // just in case other keys are present
        .some(value => value);

      this.$store.dispatch(EVENT_ACTIONS.SET_EVENT_FILTER, filter);
    },
    reset(): void {
      const filter = R.clone(this.filter);

      filter.state_filter = {};
      for (const state of Object.values(ProcessingState)) {
        if (typeof state === 'number') {
          filter.state_filter[state] = false;
        }
      }

      filter.state_filter.enabled = false;

      this.$store.dispatch(EVENT_ACTIONS.SET_EVENT_FILTER, filter);
    },
  },
  computed: {
    stateStr: () => stateStr,
    states(): number[] {
      return Object.values(ProcessingState)
        .filter((value) => typeof value === 'number')
        .filter(value => this.stateCount ? this.stateCount[value] > 0 : false)
    },
    filterCount(): number {
      return Object.values(this.$store.state.eventModule.eventFilter.state_filter).filter(R.identity).length - 1;
    },
    stateCount(): StateCountMap | undefined {
      const stateCount: StateCount[] = this.$store.state.eventModule.eventList.stateCount;
      if (stateCount) {
        // @ts-ignore
        return R.pipe(
          R.map((x: StateCount) => { return { [x.processing_state]: x.count }; }),
          R.mergeAll
        )(stateCount);
      }
      return undefined;
    },
    filter() {
      return this.$store.state.eventModule.eventFilter;
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

.height {
  height: 1.4em;
}
.text-small {
  font-size: 0.8em;
}
.checkbox-list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.mt8 {
  margin-top: 8px;
}
.white {
  color: $white;
}
.flex {
  display: flex;
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
.inline-block {
  display: inline-block;
}
.scroll {
  // height: 9em;
  overflow: auto;
}
</style>
