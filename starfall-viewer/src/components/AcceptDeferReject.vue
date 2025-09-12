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
    <ul>
      <li>
        <input type="radio" id="accept" name="choices" :value="StateEnum.Accepted" v-model="processingState" />
        <label for="accept" class="accept">Accept</label>
      </li>
      <li>
        <input type="radio" id="defer" name="choices" :value="StateEnum.Deferred" v-model="processingState" />
        <label for="defer" class="defer">Defer</label>
      </li>
      <li>
        <input type="radio" id="reject" name="choices" :value="StateEnum.Rejected" v-model="processingState" />
        <label for="reject" class="reject">Reject</label>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { ProcessingState as StateEnum } from 'starfall-common/Types/ProcessingState';

export default {
  name: 'AcceptDeferReject',
  emits: ['change'],
  data() {
    return {
      processingState: undefined,
      StateEnum: StateEnum,
    }
  },
  mounted() {
    const currentState = this.$store.state.eventModule.selectedEventSummary?.processing_state;
    if (currentState) {
      this.processingState = currentState;
    }
  },
  watch: {
    processingState() {
      this.$emit('change', this.processingState)
    }
  },
}
</script>

<style lang="scss" scoped>
@use "sass:color";
@import '@/assets/scss/colors.scss';

ul {
  list-style-type: none;
  display: inline-block;
  margin: 0;
  padding: 0;
}

li {
  text-align: center;
  display: inline-block;
  padding: 0;
  position: relative;
  margin: 0 5px 0 5px;
  width: 100px;
  height: 30px;
}

label, input {
  display: block;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

label {
  color: $black;
  padding: 5px;
  border: 1px solid $off-white;
  border-radius: 4px;
  z-index: 90;
  cursor: pointer;
}

input[type=radio] {
  opacity: 0.011;
}

label.accept {
  background: color.adjust($accepted, $lightness: 30%)
}

label.defer {
  background: color.adjust($deferred, $lightness: 30%)
}

label.reject {
  background: color.adjust($rejected, $lightness: 30%)
}

input[type=radio]:checked + label.accept, label.accept:hover {
  background: $accepted;
  border-color: $black;
  border-width: 1px;
}
input[type=radio]:checked + label.defer, label.defer:hover {
  background: $deferred;
  border-color: $black;
  border-width: 1px;
}
input[type=radio]:checked + label.reject, label.reject:hover {
  background: $rejected;
  border-color: $black;
  border-width: 1px;
}
</style>
