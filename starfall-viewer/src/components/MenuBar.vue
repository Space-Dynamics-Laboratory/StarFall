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
  <div class="nav no-select">
    <MainMenu />
    <ProcessingStatus class="processing-status" />
    <StatusWidget />
  </div>
</template>

<script lang="ts">
import ProcessingStatus from '@/components/ProcessingStatus.vue';
import MainMenu from '@/components/MainMenu.vue';
import StatusWidget from '@/components/StatusWidget.vue';

export default {
  name: 'MenuBar',
  components: {
    ProcessingStatus,
    MainMenu,
    StatusWidget
  },
  computed: {
    interval: {
      get() {
        return this.$store.state.settingsModule.eventAlertInterval;
      },
      set(newVal: number) {
        this.$store.state.settingsModule.eventAlertInterval = newVal;
      }
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

.nav {
  width: 100%;
  margin: 0;
  padding: 0;
  background-color: $black;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.processing-status {
  width: 30em;
}
</style>
