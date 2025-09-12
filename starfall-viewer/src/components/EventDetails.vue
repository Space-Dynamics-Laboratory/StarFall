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
  <div class="event-details" :class="dark ? 'dark' : ''">
    <div v-if="eventSummary" class="content">
    <p><span class="label">Event ID:</span> {{ eventSummary.event_id }}</p>

    <!-- Date -->
    <p><span class="label">Date:</span> {{ date_str }}</p>

    <!-- Location -->
    <p class="mb0"><span class="label">Location</span></p>
    <ul>
      <li>Lat (&#176;N): {{ eventLat_str }}</li>
      <li>Lon (&#176;E): {{ eventLon_str }}</li>
    </ul>

    <!-- Altitude -->
    <p><span class="label">Altitude (km):</span> {{ eventAlt_km_str }}</p>
    <ul>
      <li>Escape Vel (km/s): {{ escapeVelocity_str }}</li>
      <li>Circular Vel (km/s): {{ circularVelocity_str }}</li>
    </ul>

    <!-- Energy -->
    <p><span class="label">Energy (J):</span> {{ energy_str }}</p>

    <!-- Velocity -->
    <p class="mb0"><span class="label">Velocity (km/s):</span> {{ speed_km_s_str }}
      <button
        v-if="speed_km_s_str != UNKNOWN"
        class="btn ml-10 inline-flex"
        @click="deleteVelocityEstimate"
        title="delete velocity estimate"
      >
        <fa-icon icon="trash" />
      </button>
    </p>
    <ul class="mb-0">
      <li>X: {{ vel_x_km_s_str }}</li>
      <li>Y: {{ vel_y_km_s_str }}</li>
      <li>Z: {{ vel_z_km_s_str }}</li>
    </ul>
    </div>
    <div class="white p5" v-else> No Event Selected </div>

    <button v-if="eventSummary && saveButton" @click="saveSixLineMessage" class="btn fixed flex" title="Download six line message">
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-file-down"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><path d="M12 18v-6"/><path d="m9 15 3 3 3-3"/></svg>
    </button>
  </div>
</template>

<script lang="ts">
import { ACTIONS as MESSAGE_ACTIONS } from '@/store/modules/MessageModule';
import { MUTATIONS as POPUP_MUTATIONS } from '@/store/modules/PopupsModule';
import type { EventListItem } from 'starfall-common/Types/EventListItem';
import { formatUTC } from 'starfall-common/helpers/time';
import type { PropType } from 'vue';

const UNKNOWN = '--';

export default {
  name: 'EventDetails',
  props: {
    eventSummary: Object as PropType<EventListItem> | null,
    saveButton: Boolean,
    dark: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {

    }
  },
  methods: {
    deleteVelocityEstimate(): void {
      if (this.eventSummary) {
        const id = this.eventSummary.event_id;
        this.$store.commit(POPUP_MUTATIONS.CREATE_CONFIRMATION_POPUP, {
          title: 'Delete Velocity Estimate',
          message: 'Do you want to permanently delete the velocity estimate?',
          confirmButtonText: 'Delete',
          onConfirm: () => { this.$store.dispatch(MESSAGE_ACTIONS.DELETE_VELOCITY, id); }
        });
      }
    },
    download(filename: string, text: string): void {
      const element = document.createElement('a');
      element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
      element.setAttribute('download', filename);

      element.style.display = 'none';
      document.body.appendChild(element);

      element.click();

      document.body.removeChild(element);
    },
    saveSixLineMessage(): void {
      if (!this.eventSummary) {
        console.warn('no event loaded');
        return;
      }
      const dateStr = formatUTC('y-MM-dd_hh-mm-ss', new Date(this.eventSummary.approx_trigger_time));
      this.download(`StarFall-${dateStr}.txt`, this.messageSummary);
    }
  },
  computed: {
    UNKNOWN: () => UNKNOWN,
    messageSummary(): string {
      if (!this.eventSummary) {
        return 'no event selected';
      }

      const date = new Date(this.eventSummary.approx_trigger_time);

      return `On ${formatUTC('dd MMM y', date)}, GLM sensors detected the following indications of a meteoroid entry into Earth's atmosphere.
a. Date/time of peak brightness: ${formatUTC('dd MM yy/HH:mm:ss z', date)}
b. Location of peak brightness: ${this.eventLat_str} degrees N latitude, ${this.eventLon_str} degrees E longitude
c. Altitude of peak brightness: ${this.eventAlt_km_str} km
d. Velocity of peak brightness: ${this.speed_km_s_str} km/sec
e. Approximate total radiated energy: ${this.energy_str} joules
f. Pre-entry velocity vector (ECF): VELX ${this.vel_x_km_s_str} km/sec; VELY ${this.vel_y_km_s_str} km/sec; VELZ ${this.vel_z_km_s_str} km/sec
`;
    },
    escapeVelocity_str(): string {
      if (this.eventSummary !== null && this.eventSummary.location_ecef_m !== null) {
        const [x, y, z] = this.eventSummary.location_ecef_m;
        const r = Math.sqrt(x ** 2 + y ** 2 + z ** 2) / 1000; // km
        const alt = r - 6371; // km
        const r_earth = 6378; // km
        const G = 6.674e-20; // km^3 * kg^-1  * s^-2
        const M = 5.972e24; // kg
        return (Math.sqrt(2 * G * M / (r_earth + alt))).toFixed(2);
      }
      return UNKNOWN;
    },
    circularVelocity_str(): string {
      if (this.eventSummary !== null && this.eventSummary.location_ecef_m !== null) {
        const [x, y, z] = this.eventSummary.location_ecef_m;
        const r = Math.sqrt(x ** 2 + y ** 2 + z ** 2) / 1000; // km
        const alt = r - 6371; // km
        const r_earth = 6378; // km
        const G = 6.674e-20; // km^3 * kg^-1  * s^-2
        const M = 5.972e24; // kg
        return (Math.sqrt(G * M / (r_earth + alt))).toFixed(2);
      }
      return UNKNOWN;
    },
    vel_x_km_s_str(): string {
      if (this.eventSummary !== null && this.eventSummary.velocity_ecef_m_sec !== null) {
        return (this.eventSummary.velocity_ecef_m_sec[0] / 1000).toFixed(1);
      }
      return UNKNOWN;
    },
    vel_y_km_s_str(): string {
      if (this.eventSummary !== null && this.eventSummary.velocity_ecef_m_sec !== null) {
        return (this.eventSummary.velocity_ecef_m_sec[1] / 1000).toFixed(1);
      }
      return UNKNOWN;
    },
    vel_z_km_s_str(): string {
      if (this.eventSummary !== null && this.eventSummary.velocity_ecef_m_sec !== null) {
        return (this.eventSummary.velocity_ecef_m_sec[2] / 1000).toFixed(1);
      }
      return UNKNOWN;
    },
    speed_km_s_str(): string {
      if (this.eventSummary !== null && this.eventSummary.velocity_ecef_m_sec !== null) {
        const [vel_x, vel_y, vel_z] = this.eventSummary.velocity_ecef_m_sec;
        const speed = Math.sqrt(vel_x ** 2 + vel_y ** 2 + vel_z ** 2) / 1000;
        return speed.toFixed(1);
      }
      return UNKNOWN;
    },
    eventLat_str(): string {
      if (this.eventSummary !== null && this.eventSummary.location_lat_lon_alt_m !== null) {
        return this.eventSummary.location_lat_lon_alt_m[0].toFixed(1);
      }
      return UNKNOWN;
    },
    eventLon_str(): string {
      if (this.eventSummary !== null && this.eventSummary.location_lat_lon_alt_m !== null) {
        return this.eventSummary.location_lat_lon_alt_m[1].toFixed(1);
      }
      return UNKNOWN;
    },
    eventAlt_km_str(): string {
      if (this.eventSummary !== null && this.eventSummary.location_lat_lon_alt_m !== null) {
        return (this.eventSummary.location_lat_lon_alt_m[2] / 1000).toFixed(1);
      }
      return UNKNOWN;
    },
    date_str(): string {
      if (this.eventSummary !== null && this.eventSummary.location_lat_lon_alt_m !== null) {
        const triggerTime = this.eventSummary?.approx_trigger_time;
        if (triggerTime) {
          return formatUTC('yyyy-MM-dd (DDD) HH:mm:ss', new Date(triggerTime));
        }
      }
      return UNKNOWN;
    },
    energy_str(): string {
      if (this.eventSummary !== null && this.eventSummary.approx_energy_j !== null) {
        return this.eventSummary.approx_energy_j.toExponential(1).replace('+', '');
      }
      return UNKNOWN;
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

.event-details {
  padding: 0;
  margin: 0;
  position: relative;
  background-color: #f1f1f1;
  display: default;
  width: default;
}
.event-details.dark {
  background-color: #222;
}
.event-details.dark * {
  color: $white;
}
.event-details.dark .btn * {
  color: black;
}
.content {
  margin-left: 0.5em;
}
* {
  font: 13px "Consolas", monospace;
  color: $black;
}
p {
  margin-top: 0;
}
ul {
  margin-top: 0;
  padding-left: 2em;
}
.mb0 {
  margin-bottom: 0;
}
.flex {
  display: flex;
}
.inline-flex {
  display: inline-flex;
}
.btn {
  cursor: pointer;
  align-items: center;
  padding: 3px;
  font-weight: 700;
  font-family: 'Arial', sans-serif;
}
.fixed {
  position: sticky;
  bottom: 0.5em;
  right: 0.5em;
  margin-left: auto;
  margin-right: 0.5em;
}
.ml-10 {
  margin-left: 10px;
}
.colored {
  color: $black;
  font-weight: bold;
}
.label {
  font-weight: bold;
}
.white {
  color: $white;
}
.p5 {
  padding: 5px;
}
.mb-0 {
  margin-bottom: 0;
}
</style>
