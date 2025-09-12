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
  <div class="no-select inner">
    <ul>
      <li class="debug" title="debug">
        <input :checked="filter.debug" type="checkbox" id="debug" name="debug" @click="toggle('debug')" />
        <label for="debug" class="debug">
          <fa-icon icon="bug"/>
        </label>
      </li>
      <li class="info" title="info">
        <input :checked="filter.info" type="checkbox" id="info" name="info" @click="toggle('info')" />
        <label for="info" class="info">
          <fa-icon icon="info-circle"/>
        </label>
      </li>
      <li class="warn" title="warn">
        <input :checked="filter.warning" type="checkbox" id="warning" name="warning" @click="toggle('warning')" />
        <label for="warning" class="warning">
          <fa-icon icon="exclamation-triangle"/> ({{count_warn}})
        </label>
      </li>
      <li class="error" title="error">
        <input :checked="filter.error" type="checkbox" id="error" name="error" @click="toggle('error')" />
        <label for="error" class="error">
         <fa-icon icon="exclamation-circle"/> ({{count_error}})
        </label>
      </li>
    </ul>
  </div>
</div>
</template>

<script lang="ts">
import type { MicroserviceDetailsLogFilter } from '@/types/MicroserviceDetailsLogFilter';
import { GETTERS as STATUS_GETTERS } from '@/store/modules/MicroserviceStatusModule';
import { LogState } from '@/types/LogState';
import type { PropType } from 'vue';

export default {
  name: 'LogFilterButtons',
  props: {
    microserviceIndex: Number,
  },
  methods: {
    toggle(filter: string): void {
      this.$emit('toggle', filter);
    }
  },
  computed: {
    count_warn(): number {
      return this.$store.getters[STATUS_GETTERS.LOG_COUNTS_FOR_SERVICE](this.microserviceIndex)[LogState.Warning];
    },
    count_error(): number {
      return this.$store.getters[STATUS_GETTERS.LOG_COUNTS_FOR_SERVICE](this.microserviceIndex)[LogState.Error];
    },
    filter(): MicroserviceDetailsLogFilter {
      return this.$store.state.settingsModule.microserviceDetailsLogFilter;
    }
  }
}
</script>

<style lang="scss" scoped>
@use 'sass:color';
@import '@/assets/scss/colors.scss';
$dur: 100ms;

.inner {
  display: inline-block;
  margin-bottom: 2px;
  margin-right: 3px;
}
ul {
  list-style-type: none;
  float: right;
  padding: 0;
  margin: 0;
  text-align: right;
}
ul li {
  position: relative;
  float: left;
  margin: 0 0 0 5px;
  height: 30px;
}
ul li.error, ul li.warn {
  width: 75px;
}
ul li.debug, ul li.info {
  width: 50px;
}
ul label, ul input {
  display: block;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}
label {
  background: color.scale($gl-grey, $lightness: 60%);
  font-weight: 700;
  text-align: center;
  color: $black;
  box-shadow: 3px 3px $light-grey;
  transition-duration: $dur;
}
ul input[type=checkbox] + label {
  border-radius: 3px;
}
ul input[type=checkbox]:checked + label {
  box-shadow: 2px 2px $gl-grey;
  transform: translateY(2px);
  transition-duration: $dur;
}
ul input[type=checkbox]:checked + label.debug {
  background: $debug;
  border-color: $debug;
}
ul input[type=checkbox]:checked + label.info {
  background: $info;
  border-color: $info;
}
ul input[type=checkbox]:checked + label.warning {
  background: $warning;
  border-color: $warning;
}
ul input[type=checkbox]:checked + label.error {
  background: $error;
  border-color: $error;
}
ul label {
  color: $black;
  padding: 5px;
  border: 1px solid $off-white;
  z-index: 90;
  cursor: pointer;
}
</style>
