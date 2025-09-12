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
  <div class="menu no-select">
    <Modal
      :open="popupState === PopupEnum.PlotSettings"
      @toggle-modal="toggleModal(PopupEnum.PlotSettings);"
    >
      <template v-slot:content>
        <PlotSettings v-if="popupState === PopupEnum.PlotSettings"/>
      </template>
    </Modal>
    <Modal
      :open="popupState === PopupEnum.SensorInfoSettings"
      @toggle-modal="toggleModal(PopupEnum.SensorInfoSettings);"
    >
      <template v-slot:content>
        <SettingsSensorInfo v-if="popupState === PopupEnum.SensorInfoSettings"/>
      </template>
    </Modal>
    <Modal
      :open="popupState === PopupEnum.ReprocessSettings"
      @toggle-modal="toggleModal(PopupEnum.ReprocessSettings);"
    >
      <template v-slot:content>
        <h2>Set time for trigger</h2>
        <div class="flex">
          <div class="reprocess-input">
            <label for="reprocess-date">Date:</label>
            <input type="date" id="reprocess-date" v-model="reprocessDate"/>
          </div>
          <div class="reprocess-input">
            <label class="ml-1" for="reprocess-time">Time:</label>
            <input type="time" min="00:00" max="23:59" step="1" id="reprocess-time" v-model="reprocessTime"/>
          </div>
        </div>
        <p v-if="validDatestringISO(isoDatestring)">Time to submit: {{ formatDate(new Date(isoDatestring))}}</p>
        <button :disabled="!validDatestringISO(isoDatestring)" class="btn-base submit button" @click="submitReprocessTime">Create Trigger</button>
      </template>
    </Modal>

    <div class="dropdown title">StarFall</div>
    <!-- Settings -->
    <div class="dropdown">
      <button
        @click="clickMenu(MenuStateEnum.SettingsMenu)"
        class="dropbtn"
        :class="menuState === MenuStateEnum.SettingsMenu ? 'active' : ''"
      >
        Settings
      </button>
      <!-- ref setting -->
      <div :class="menuState === MenuStateEnum.SettingsMenu ? 'show' : ''" class="dropdown-content">
        <div>
          <label for="toggle-zoom-setting">Zoom to Event</label>
          <input class="toggle m0" type="checkbox" name="toggle-zoom-setting" id="toggle-zoom-setting" v-model="zoomSetting">
        </div>
        <div>
          <label for="toggle-flashing-screen">Flash Screen on New Event</label>
          <input class="toggle m0" type="checkbox" name="toggle-flashing-screen" id="toggle-flashing-screen" v-model="flashSetting">
        </div>
        <div>
          <label for="toggle-voice-alert">Voice Alert</label>
          <input class="toggle m0" type="checkbox" name="toggle-voice-alert" id="toggle-voice-alert" v-model="voiceAlertSetting">
        </div>
        <!-- <a @click="showGlobeSettings">Globe</a> -->
        <div>
          <label for="toggle-alert-above-threshold">Alert if Above Threshold</label>
          <input class="toggle m0" type="checkbox" name="toggle-alert-above-threshold" id="toggle-alert-above-threshold" v-model="alertSetting">
        </div>
        <hr/>
        <div>
          <label for="replay-interval" class="inline-block" title="Number of seconds before replaying event alert audio">Alert Interval (s)</label>
          <input id="replay-interval" type="number" class="input" v-model.lazy="interval" number min="0">
        </div>
        <div>
          <label for="n-events-per-page" class="inline-block" title="Number of events displayed in the event table">Events Per Page</label>
          <input id="n-events-per-page" type="number" class="input" v-model.lazy="nEventsPerPage" number min="0">
        </div>
        <div>
          <label for="max-logs-per-service" class="inline-block" title="Number of logs to keep in memory">Logs Stored</label>
          <input id="max-logs-per-service" type="number" class="input" v-model.lazy="maxLogsPerService" number min="1">
        </div>
        <hr/>
        <button @click="toggleModal(PopupEnum.PlotSettings)">Plot Settings</button>
        <button @click="toggleModal(PopupEnum.SensorInfoSettings)">Sensor Info Settings</button>
        <!-- <button @click="toggleModal(PopupEnum.ReprocessSettings)" title="Reprocess event by selected time stamp">Create New Time Trigger</button> -->
      </div>
    </div>

    <!-- About -->
    <div class="dropdown">
      <button
        @click="clickMenu(MenuStateEnum.AboutMenu)"
        :class="menuState === MenuStateEnum.AboutMenu ? 'active' : ''"
        class="dropbtn"
      >About</button>
      <div :class="menuState === MenuStateEnum.AboutMenu ? 'show' : ''" class="dropdown-content">
        <button @click="showAboutStarFall">StarFall</button>
        <button @click="showAttribution">Attribution</button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { ACTIONS as EVENT_ACTIONS } from '@/store/modules/EventModule';
import { MUTATIONS as SETTINGS_MUTATIONS } from '@/store/modules/SettingsModule';
import { MUTATIONS as POPUP_MUTATIONS } from '@/store/modules/PopupsModule';
import Modal from '@/components/Modal.vue';
import PlotSettings from '@/components/PlotSettings.vue';
import SettingsSensorInfo from '@/components/SettingsSensorInfo.vue';
import { formatUTC } from 'starfall-common/helpers/time';

export enum MenuStateEnum {
  NoMenu,
  ViewMenu,
  SettingsMenu,
  AboutMenu,
}

export enum PopupEnum {
  NoPopup,
  PlotSettings,
  SensorInfoSettings,
  ReprocessSettings
}

export type MenuState = MenuStateEnum.NoMenu | MenuStateEnum.ViewMenu | MenuStateEnum.SettingsMenu | MenuStateEnum.AboutMenu;

/**
 * This component handles the menu on the left side of the menu bar and the dropdown
 * menus.
 *
 * There only needs to be one instance of the click handler to clear menus,
 * even if more menus are developed in other components (ex. the status widget)
 */
export default {
  name: 'MainMenu',
  components: {
    Modal,
    PlotSettings,
    SettingsSensorInfo
  },
  data() {
    return {
      MenuStateEnum: MenuStateEnum,
      menuState: MenuStateEnum.NoMenu as MenuState,
      PopupEnum: PopupEnum,
      popupState: PopupEnum.NoPopup,
      reprocessDate: 0,
      reprocessTime: 0,
    }
  },
  methods: {
    toggleModal(state: PopupEnum) {
      this.popupState = this.popupState === state ? PopupEnum.NoPopup : state;
    },
    clickMenu(state: MenuState) {
      if (state !== this.menuState) {
        this.menuState = state;
      } else {
        this.menuState = MenuStateEnum.NoMenu;
      }
    },
    showAllEvents(): void {
      this.$store.dispatch(EVENT_ACTIONS.SHOW_ALL_EVENTS);
    },
    submitReprocessTime(): void {
      fetch(`/api/reprocess-time/${this.isoDatestring}`, { method: 'POST' })
        .then(res => res.json())
        .then(res => {
          // reset the reprocessing time
          this.reprocessDate = 0;
          this.reprocessTime = 0;

          if (res.error) {
            console.error(res.error);
            this.$store.commit(POPUP_MUTATIONS.CREATE_TOAST_POPUP, {
              icon: 'error',
              title: res.error,
              duration: 3000
            });
          } else {
            this.$store.commit(POPUP_MUTATIONS.CREATE_TOAST_POPUP, {
              icon: 'info',
              title: res.msg,
              duration: 3000
            });
          }
        })
        .catch(err => {
          console.error('fetch error', err);
        });
      this.popupState = PopupEnum.NoPopup;
    },
    formatDate(date: Date) {
      return formatUTC('yyyy-MM-dd (DDD) HH:mm:ss', date);
    },
    formatDateISO(date, time) {
      // return formatUTC('yyyy-MM-dd\'T\'HH:mm:ss.SSSSSS\'Z\'', date);
      return date + 'T' + time + '.000000Z';
    },
    validDatestringISO(str) {
      const ISO_EXTENDED_STRING_LENGTH = 27;
      const date = new Date(str);
      // @ts-ignore
      const validDateObj = date instanceof Date && !isNaN(date);
      return str.length === ISO_EXTENDED_STRING_LENGTH && validDateObj;
    },
    showGlobeSettings(): void {
      console.trace('This feature is not implemented');
      alert('This feature is not implemented\ncheck the console for more info');
    },
    resetSettings(): void {
      this.showAllEvents();
      this.$store.commit(SETTINGS_MUTATIONS.RESET);
    },
    showAboutStarFall(): void {
      this.$store.commit(POPUP_MUTATIONS.CREATE_ABOUT_POPUP);
    },
    showAttribution(): void {
      this.$store.commit(POPUP_MUTATIONS.CREATE_ATTRIBUTIONS_POPUP);
    }
  },
  computed: {
    isoDatestring(): string {
      return this.formatDateISO(this.reprocessDate, this.reprocessTime);
    },
    detailView(): boolean {
      return this.$store.state.eventModule.detailView;
    },
    interval: {
      get(): string {
        return String(this.$store.state.settingsModule.eventAlertInterval);
      },
      set(newVal: string) {
        this.$store.commit(SETTINGS_MUTATIONS.SET_ALERT_INTERVAL, Number.parseInt(newVal));
      }
    },
    nEventsPerPage: {
      get(): string {
        return String(this.$store.state.settingsModule.nEventsPerPage);
      },
      set(newVal: string) {
        this.$store.commit(SETTINGS_MUTATIONS.SET_N_EVENTS_PER_PAGE, Number.parseInt(newVal));
      }
    },
    maxLogsPerService: {
      get(): string {
        return String(this.$store.state.settingsModule.maxLogsPerService);
      },
      set(newVal: string) {
        this.$store.commit(SETTINGS_MUTATIONS.SET_MAX_LOGS_PER_SERVICE, Number.parseInt(newVal));
      }
    },
    zoomSetting: {
      get() {
        return this.$store.state.settingsModule.zoomToEvent
      },
      set(newVal) {
        this.$store.commit(SETTINGS_MUTATIONS.TOGGLE_ZOOM_TO_EVENT, newVal);
      }
    },
    flashSetting: {
      get() {
        return this.$store.state.settingsModule.flashingScreen
      },
      set(newVal) {
        this.$store.commit(SETTINGS_MUTATIONS.TOGGLE_FLASHING_SCREEN, newVal);
      }
    },
    voiceAlertSetting: {
      get() {
        return this.$store.state.settingsModule.voiceAlertSetting
      },
      set(newVal) {
        this.$store.commit(SETTINGS_MUTATIONS.TOGGLE_VOICE_ALERT, newVal);
      }
    },
    alertSetting: {
      get() {
        return this.$store.state.settingsModule.alertOnlyIfAboveEnergyThreshold
      },
      set(newVal) {
        this.$store.commit(SETTINGS_MUTATIONS.TOGGLE_ALERT_ONLY_IF_ABOVE_ENERGY_THRESHOLD, newVal);
      }
    },
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

.flex {
  display: flex;
  flex-wrap: wrap;
}

.dropbtn:hover, .dropbtn.active {
  background-color: $accent;
}

.input {
  display: inline-block;
  width: 5em;
  height: 22px;
  background-color: $transparent
}
input {
  margin: 0;
  margin-right: 8px;
}

input[type=number] {
  -moz-appearance:textfield;
  &::-webkit-inner-spin-button,
  &::-webkit-outer-spin-button {
    -webkit-appearance: none;
  }
}
.reprocess-input {
  margin-bottom: 0.5em;
}
.reprocess-input label {
  margin-right: 1em;
  display: inline-block;
  width: 2rem;
}
.ml-1 {
  margin-left: 1em;
}
.dropdown-content button,
.dropdown-content label {
  cursor: pointer;
  margin: 0;
  padding: 3px 8px;
}
.dropdown-content button {
  border-radius: 0;
  background: #0000;
  border: none;
  display: block;
  text-align: left;
  width: 100%;
}
.dropdown-content * {
  font-size: 12px;
}
.dropdown-content div {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.dropdown-content button:hover {
  background: #dcdcdc;
}
.dropdown-content hr {
  margin: 4px 6px;
  padding: 0;
  border: none;
  border-top: 1px solid #999;
}
.submit {
  margin: 1em auto 0;
  display: block;
}
.title {
  font-weight: 700;
  margin: 0 0.7em;
  color: white;
}
</style>
