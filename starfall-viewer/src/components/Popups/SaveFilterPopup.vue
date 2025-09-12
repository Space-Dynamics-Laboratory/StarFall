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
    <div class="popup-base">
      <h2>Filter Name</h2>
      <input class="input" type="text" :value="'Setting ' + nextFilterNumber" ref="name" @keypress="onKeypress"/>
      <div class="buttons-container">
        <button class="btn-base button submit center" @click="submit" type="submit">Save</button>
        <button class="btn-base button cancel center" @click="close">Cancel</button>
      </div>
    </div>
  <div @click="close" class="popup-background"></div>
  </div>
</template>

<script lang="ts">
import { MUTATIONS as EVENT_MUTATIONS } from '@/store/modules/EventModule';

export default {
  name: 'SaveFilterPopup',
  methods: {
    submit(): void {
      let filterName = this.$refs.name.value;
      if (this.$refs.name.value === '') {
        filterName = `Setting ${this.nextFilterNumber}`;
      }
      this.$store.commit(EVENT_MUTATIONS.SAVE_EVENT_FILTER, filterName);
    },
    onKeypress(event: KeyboardEvent): void {
      if (event.key === 'Enter') {
        this.submit();
      }
    },
    close() {
      this.$emit('close');
    }
  },
  computed: {
    nextFilterNumber(): number {
      return this.$store.state.eventModule.savedEventFilterList.length + 1;
    }
  }
}
</script>

<style lang="scss" scoped>
  @import '@/assets/scss/colors.scss';

  input {
    font-family: sans-serif;
    width: 100%;
  }

  h2 {
    text-align: center;
    margin: 0;
  }

  .buttons-container{
    display: flex;
    justify-content: center;
  }

  .button {
    max-width: 200px;
  }

  .accept-defer-reject {
    width: 80%
  }

</style>
