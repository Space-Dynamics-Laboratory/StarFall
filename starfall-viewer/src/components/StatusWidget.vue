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
  <div class="no-select">

    <button
      @click="toggleDetails"
      :class="getStatusIconClasses()"
      class="dropbtn text-size"
    >
      Status
    </button>

    <div class="dropdown-content" :class="{ show }" style="width: 200px;">
      <div
        v-for="(microservice, index) in microserviceChainComponents"
        :key="microservice.name"
        @click="showMicroserviceDetails(index)"
      >
        <a :class="microserviceClasses(index)" class="ellipsis">
          {{ microservice.name }}
        </a>
        </div>
    </div>
    <StatusDetails
      v-for="(microservice, index) in microserviceChainComponents"
      :microserviceIndex="index"
      :microservice="getMicroserviceByIndex(index)"
      :key="microservice.name + '_details'"
      :class="microserviceIndexSelection === index ? 'show-status' : 'hide-status'"
      class="dropdown-content"
    />
  </div>
</template>

<script lang="ts">
import StatusDetails from '@/components/StatusDetails.vue';
import { GETTERS as STATUS_GETTERS } from '@/store/modules/MicroserviceStatusModule';
import { LogState } from '@/types/LogState';
import type { MicroserviceStatus } from 'starfall-common/Types/MicroserviceStatus';
import * as R from 'ramda';

export default {
  name: 'StatusWidget',
  components: {
    StatusDetails
  },
  data() {
    return {
      show: false,
      microserviceIndexSelection: null as number | null
    }
  },
  computed: {
    microserviceChainStatus(): LogState {
      return this.$store.getters[STATUS_GETTERS.MICROSERVICE_CHAIN_STATUS];
    },
    microserviceChainComponents(): MicroserviceStatus[] {
      return this.$store.state.microserviceStatusModule.microserviceStatusList;
    },
    LogState(): typeof LogState {
      return LogState;
    }
  },
  methods: {
    getStatusIconClasses() {
      const status = this.microserviceChainStatus;
      return {
        OK: status === LogState.OK,
        warning: status === LogState.Warning,
        error: status === LogState.Error
      };
    },
    microserviceClasses(index: number) {
      const status = this.$store.getters[STATUS_GETTERS.MICROSERVICE_STATUS](index);
      return {
        OK: status === LogState.OK,
        warning: status === LogState.Warning,
        error: status === LogState.Error
      };
    },
    microserviceStatus(index: number): LogState {
      return this.$store.getters[STATUS_GETTERS.MICROSERVICE_STATUS](index);
    },
    toggleDetails(): void {
      if (this.show) {
        this.microserviceIndexSelection = null
      }
      this.show = !this.show;
    },
    getMicroserviceByIndex(index: number) {
      this.$store.state.microserviceStatusModule.microserviceStatusList[index]
    },
    showMicroserviceDetails(index: number): void {
      this.microserviceIndexSelection = index;
    }
  }
}
</script>

<style lang="scss" scoped>
@use 'sass:color';
@import '@/assets/scss/colors.scss';
@import '@/assets/scss/variables.scss';

$perc: 25%;

.text-size {
  font-size: 1em;
}
.OK {
  background-color: $OK;
  border-color: color.scale($OK, $lightness: -$perc);
}
.warning {
  background-color: $warning;
  border-color: color.scale($warning, $lightness: -$perc)
}
.error {
  background-color: $error;
  border-color: color.scale($error, $lightness: -$perc)
}
.error:hover, .error:focus {
  background-color: color.scale($error, $lightness: -5%);
}
.dropbtn {
  color: $black;
  font-family: 'Arial', sans-serif;
  font-weight: 700;
}
.dropdown-content {
  display: absolute;
  right: 0;
  top: $menu-height;
}
.show-status {
  display: block;
}
.hide-status {
  display: none;
}
.ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
