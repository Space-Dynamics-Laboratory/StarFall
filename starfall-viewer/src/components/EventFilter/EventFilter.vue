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
  <div class="filter-container">
    <div class="filter-stats">
      <p class="count-width">{{ filteredCount }}/{{ eventCount }} events</p>
      <div title="filter by unviewed" class="flex align-center" v-if="unviewedCount > 0">
        <input class="toggle m0" type="checkbox" name="unviewed" id="filter-by-unviewed" v-model="unviewedFilter">
        <label for="filter-by-unviewed">{{ unviewedCount }} unviewed</label>
      </div>
      <button id="reset" class="ml2 mr2 reset-btn" @click="reset">
        <svg class="mr" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2v6h-6"></path><path d="M21 13a9 9 0 1 1-3-7.7L21 8"></path></svg>
        Reset Filters
      </button>
    </div>
    <div class="filter-card-container">
      <DateFilter
        class="filter-card"
        ref="dateFilter"
      />
      <EnergyFilter
        class="filter-card"
        ref="energyFilter"
      />
      <StateFilter
        class="filter-card"
        ref="stateFilter"
      />
    </div>
  </div>
</template>

<script lang="ts">
import DateFilter from '@/components/EventFilter/DateFilter.vue';
import EnergyFilter from '@/components/EventFilter/EnergyFilter.vue';
import StateFilter from '@/components/EventFilter/StateFilter.vue';
import type { EventFilter as EventFilter_t } from 'starfall-common/Types/EventFilter';
import { ACTIONS as EVENT_ACTIONS } from '@/store/modules/EventModule';
import * as R from 'ramda';

export default {
  name: 'EventFilter',
  components: {
    DateFilter,
    EnergyFilter,
    StateFilter
  },
  data() {
    return {
      unviewedFilter: false
    }
  },
  methods: {
    reset(): void {
      this.$refs.dateFilter.reset();
      this.$refs.energyFilter.reset();
      this.$refs.stateFilter.reset();
      this.unviewedFilter = false;
    }
  },
  watch: {
    unviewedFilter(val: boolean): void {
      const filter = R.clone(this.$store.state.eventModule.eventFilter);
      filter.unviewed = val;
      this.$store.dispatch(EVENT_ACTIONS.SET_EVENT_FILTER, filter);
    }
  },
  computed: {
    savedEventFilterList(): EventFilter_t[] {
      return this.$store.state.eventModule.savedEventFilterList;
    },
    filteredCount(): number {
      return this.$store.state.eventModule.eventList.filteredCount;
    },
    eventCount(): number {
      return this.$store.state.eventModule.eventList.totalCount;
    },
    unviewedCount(): number {
      return this.$store.state.eventModule.eventList.unviewed;
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

.btn {
  display: flex;
  align-items: center;
}
.flex {
  display: flex;
}
.align-center {
  align-items: center;
}
.count-width {
  min-width: 10em;
}
.white {
  color: $off-white;
}
.m0 {
  margin: 0;
}
.p0 {
  padding: 0;
}
.mr {
  margin-right: 4px;
}
.ml2 {
  margin-left: 2em;
}
.mr2 {
  margin-right: 2em;
}
.reset-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-right: 1em;
  padding-left: 1em;
}
.filter-container {
  color: $white;
}
.filter-stats {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
}
.filter-stats p, .filter-stats label {
  padding: 0;
  margin: 0;
  margin-right: 0.7em;
  margin-left: 0.3em;
  font-size: 0.8em;
}
.filter-card {
  padding: 0.7em;
  margin: 0.3em;
  background: #333;
  min-width: 14em;
}
.filter-card-container {
  display: flex;
  flex-wrap: wrap;
  align-content: stretch;
  align-items: flex-start;
}
.ml1 {
  margin-left: 1em;
}
.m0 {
  margin: 0;
}
</style>
