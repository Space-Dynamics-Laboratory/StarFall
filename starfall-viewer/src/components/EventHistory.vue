
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
  <div class="event-history-table relative">
    <p class="mt0 event-id" v-if="eventHistory[0]"><span class="label">Event ID:</span> {{ eventHistory[0].event_id }}</p>
    <table>
      <tbody>
      <tr>
        <th> Author </th>
        <th> Note </th>
        <th> Time </th>
      </tr>
      <tr
        v-for="note in eventHistory"
        :key="note.id"
      >
        <td>{{ note.author }}</td>
        <td>{{ note.entry }}</td>
        <td>{{ format(new Date(note.time)) }}</td>
      </tr>
      </tbody>
    </table>
    <button v-if="detailView" class="write-button fixed" @click="onClick()" title="Add event note">
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-edit"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
    </button>
  </div>
</template>

<script lang="ts">
import type { EventHistoryItem } from '@/types/EventHistoryItem';
import { MUTATIONS as POPUP_MUTATIONS } from '@/store/modules/PopupsModule';
import { formatUTC } from 'starfall-common/helpers/time';

export default {
  name: 'EventHistory',
  methods: {
    onClick() {
      this.$store.commit(POPUP_MUTATIONS.CREATE_HISTORY_NOTE_POPUP);
    },
    format(date: Date): string {
      if (date) {
        return formatUTC('y-MM-dd HH:mm:ss', date);
      } else {
        return '';
      }
    }
  },
  computed: {
    detailView(): boolean {
      return this.$store.state.eventModule.detailView;
    },
    eventHistory(): EventHistoryItem[] {
      return this.$store.state.eventModule.history;
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';
@import '@/assets/scss/table.scss';

.event-id {
  font-size: 13px;
  margin-left: 0.5em;
}
.event-history-table {
  // background-color: #f1f1f1;
  font: 13px "Consolas", monospace;
}
.relative {
  position: relative;
}
.fixed {
  position: sticky;
  bottom: 0.5em;
  right: 0.5em;
}
.write-button {
  display: flex;
  align-items: center;
  padding: 3px;
  margin-left: auto;
  margin-top: 0.5em;
  margin-right: 0.5em;
}
.mt0 {
  margin-top: 0;
}
.label {
  font-weight: bold;
}
</style>
