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
    <div class="flex text-size">

      <div v-if="processingState === State.New"                      class="box new item">                  New</div>
      <div v-else-if="processingState === State.Waiting"             class="box waiting item">              Waiting</div>
      <div v-else-if="processingState === State.Processing"          class="box processing item">           Processing</div>
      <div v-else-if="processingState === State.Failed"              class="box failed item">               Failed</div>
      <div v-else-if="processingState === State.ParameterEstimation" class="box parameter-estimation item"> Parameter Estimation</div>
      <div v-else-if="processingState === State.UserAnalysis"        class="box user-analysis item">        User Analysis</div>
      <div v-else-if="processingState === State.Accepted"            class="box accepted item">             Accepted</div>
      <div v-else-if="processingState === State.Deferred"            class="box deferred item">             Deferred</div>
      <div v-else-if="processingState === State.Rejected"            class="box rejected item">             Rejected</div>
      <div v-else-if="processingState === State.NoSolution"          class="box no-solution item">          No Solution</div>
      <div v-else-if="processingState === State.NoData"              class="box no-data item">              No Data</div>
      <div v-else class="box no-event item">No Event</div>

      <button
        v-if="processingState === State.UserAnalysis
        || processingState === State.Accepted
        || processingState === State.Deferred
        || processingState === State.Rejected"
        class="item btn-base btn-box"
        @click="onChange"
        >
          Change Event State
        </button>
    </div>
  </div>
</template>

<script lang="ts">
import type { EventListItem } from 'starfall-common/Types/EventListItem';
import { ProcessingState as State, stateStr } from 'starfall-common/Types/ProcessingState';
import { MUTATIONS as POPUP_MUTATIONS } from '@/store/modules/PopupsModule';

export default {
  name: 'ProcessingStatus',
  methods: {
    onChange(): void {
      this.$store.commit(POPUP_MUTATIONS.CREATE_EVENT_STATUS_POPUP);
    }
  },
  computed: {
    State: () => State,
    eventSummary(): EventListItem | null {
      return this.$store.state.eventModule.selectedEventSummary;
    },
    processingState(): State | null {
      if (this.eventSummary !== null) {
        return this.eventSummary.processing_state;
      }
      return null;
    },
    processingStateStr(): string | null {
      if (this.eventSummary !== null) {
        return stateStr[this.eventSummary.processing_state];
      }
      return null;
    }
  }
}
</script>

<style lang="scss" scoped>
@use "sass:color";
@import '@/assets/scss/colors.scss';
@import '@/assets/scss/variables.scss';
$perc: 25%;

.text-size * + * {
  font-size: 1em;
}
.new {
  background-color: $new;
  border-color: color.scale($new, $lightness: -$perc);
}
.waiting {
  background-color: $waiting;
  border-color: color.scale($waiting, $lightness: -$perc);
}
.processing {
  background-color: $processing;
  border-color: color.scale($processing, $lightness: -$perc);
}
.failed {
  background-color: $failed;
  border-color: color.scale($failed, $lightness: -$perc);
}
.parameter-estimation {
  background-color: $parameter-estimation;
  border-color: color.scale($parameter-estimation, $lightness: -$perc);
}
.user-analysis {
  background-color: $user-analysis;
  border-color: color.scale($user-analysis, $lightness: -$perc);
}
.accepted {
  background-color: $accepted;
  border-color: color.scale($accepted, $lightness: -$perc);
}
.deferred {
  background-color: $deferred;
  border-color: color.scale($deferred, $lightness: -$perc);
}
.rejected {
  background-color: $rejected;
  border-color: color.scale($rejected, $lightness: -$perc);
}
.no-solution {
  background-color: $no-solution;
  border-color: color.scale($no-solution, $lightness: -$perc);
}
.no-data {
  background-color: $no-data;
  border-color: color.scale($no-data, $lightness: -$perc);
}
.no-event {
  background-color: $white;
  border-color: color.scale($white, $lightness: -$perc);
}
.btn-box {
  margin: 0;
  text-align: center;
  height: $menu-height;
  font-weight: 700;
  font-family: 'Arial', sans-serif;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}
.box {
  text-align: center;
  border-style: solid;
  border: none;
  height: $menu-height;
  font-weight: 700;
  font-family: 'Arial', sans-serif;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1em;
}
.flex {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: center;
}
.item {
  flex-grow: 1;
}
</style>
