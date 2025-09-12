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
      <h1 class="title">StarFall Viewer</h1>
      <h2 class="mt-0">Version {{ version }}</h2>
      <p>Built on {{ build_time }} at branch/commit {{ commit_branch }}/{{ commit_ref }}</p>

      <table v-if="config !== ''">
        <tbody>
          <tr>
            <th>Config</th>
            <th>Log File</th>
            <th>Viewer Log</th>
          </tr>
          <tr>
            <td>{{ config.configFilepath }}</td>
            <td>{{ config.logFile }}</td>
            <td>{{ config.viewerLogDir }}</td>
          </tr>
        </tbody>
      </table>

      <!-- APACHE 2.0 LICENSE -->
      <p>This software was built for NASA’s <a href="https://www.nasa.gov/planetarydefense/">Planetary Defense Coordination Office (PDCO)</a>. Licensed under the <a href="/LICENSE">Apache License 2.0</a>.</p>
      <img src="/public/sdl-logo.png" alt="SDL Logo" width="40%">
      <div class="buttons-container">
        <button class="btn-base button submit center" @click="close">OK</button>
      </div>
    </div>
    <div @click="close" class="popup-background"/>
  </div>
</template>

<script lang="ts">
import version from 'starfall-common/config/version';
import { formatUTC } from 'starfall-common/helpers/time';

export default {
  name: 'AboutPopup',
  data() {
    return {
      config: ''
    }
  },
  mounted() {
    fetch('/api/config')
      .then(res => res.json())
      .then(res => {
        this.config = res;
      })
      .catch(console.error);
  },
  methods: {
    close() {
      this.$emit('close')
    }
  },
  computed: {
    build_time(): string {
      return import.meta.env.VITE_BUILD_TIME ? formatUTC('yyy-MM-dd', new Date(import.meta.env.VITE_BUILD_TIME)) : '';
    },
    commit_ref(): string {
      return import.meta.env.VITE_COMMIT_REF || '';
    },
    commit_branch(): string {
      return import.meta.env.VITE_COMMIT_BRANCH?.trim() || '';
    },
    version(): string {
      return version;
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

.flex {
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.title {
  text-align: center;
}

.mt-0 {
  margin-top: 0;
}
.buttons-container{
  padding: 10px 0 10px 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.button {
  max-width: 200px;
}

.blue {
  background-color: $submit-button;
}

.blue:hover {
  background-color: $submit-button-hover;
}
table {
  border-collapse: collapse;
}
td, th {
  border: 1px solid #ddd;
  padding: 8px;
}
</style>
