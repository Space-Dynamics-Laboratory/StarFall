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
    <div class="container">
      <audio ref="popupSound">
        <source src="@/assets/sounds/alert-female.wav" type="audio/mpeg">
      </audio>
      <div class="popup-base popup">
        <div class="icon-container">
          <fa-icon icon="exclamation-circle" size="5x"  :style="{ color: '#f8961e' }"/>
          <h1>New Event</h1>
          <p class="bold center text-medium">received: {{ timeNow() }}</p>
        </div>
        <div class="buttons-container">
          <button class="btn-base button submit center" @click="seeEvent">See Event</button>
          <button class="btn-base button cancel center" @click="close">Dismiss</button>
        </div>

      </div>
    </div>
    <div
      @click="close"
      class="popup-background"
      :class="$store.state.settingsModule.flashingScreen ? 'flashing-background' : ''"
    />
  </div>
</template>

<script lang="ts">
import type { EventListItem } from 'starfall-common/Types/EventListItem';
import { ACTIONS as GLOBAL_ACTIONS } from '@/store/modules/GlobalModule';
import { formatUTC } from 'starfall-common/helpers/time';
import type { PropType } from 'vue';

export default {
  name: 'EventAlertPopup',
  props: {
    eventSummary: Object as PropType<EventListItem>
  },
  data() {
    return {
      alertIntervalId: null as null | number
    }
  },
  mounted() {
    if (this.$store.state.settingsModule.voiceAlertSetting) {
      const audio = this.$refs.popupSound;
      this.alertIntervalId = window.setInterval(function () { audio.play(); }, this.$store.state.settingsModule.eventAlertInterval * 1000);
      audio.play();
    }
  },
  methods: {
    timeNow(): string {
      return formatUTC('y-MM-dd HH:mm:ss', new Date());
    },
    seeEvent(): void {
      this.$store.dispatch(GLOBAL_ACTIONS.SELECT_EVENT, this.$props.eventSummary.event_id);
      this.close();
    },
    close() {
      if (this.alertIntervalId) {
        clearInterval(this.alertIntervalId)
      }
      this.$emit('close');
    }
  }
}
</script>

<style lang="scss" scoped>
  @import '@/assets/scss/colors.scss';

  .icon-container {
    display: block;
    text-align: center;
  }

  .buttons-container {
    margin: 0;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .button {
    max-width: 200px;
  }
  .flashing-background {
    background: red;
    animation: flashing 1s infinite;
    z-index: 1000;
  }
  @keyframes flashing {
    from {
      opacity: 100%;
    }
    to {
      opacity: 0%;
    }
  }
  .center {
    text-align: center;
  }
  .bold {
    font-weight: 700;
  }
  .text-medium {
    font-size: 1.2em;
  }
</style>
