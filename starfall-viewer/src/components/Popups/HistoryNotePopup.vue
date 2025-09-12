
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
      <h2 class="no-select">Add Note to History</h2>
      <h3 class="event-time no-select">Event Time: {{ formatDate(eventTime) }}</h3>
      <p class="no-select">Author</p>
      <input ref="author" class="input">
      <p class="no-select">Note</p>
      <textarea ref="note" rows="5" cols="20" class="textarea"></textarea>
      <div v-if="missingAuthor || missingNote" class="error-container">
        <p v-if="missingAuthor && missingNote">Empty Fields: Author/Note </p>
        <p v-else-if="missingAuthor">Empty Field: Author</p>
        <p v-else-if="missingNote">Empty Field: Note</p>
      </div>
      <div class="buttons-container">
        <button class="btn-base button submit center" @click="submit">Add</button>
        <button class="btn-base button cancel center" @click="close">Cancel</button>
      </div>
    </div>
    <div @click="close" class="popup-background"/>
  </div>
</template>

<script lang="ts">
import { ACTIONS as MESSAGE_ACTIONS } from '@/store/modules/MessageModule';
import { formatUTC } from 'starfall-common/helpers/time';

export default {
  name: 'HistoryNotePopup',
  data() {
    return {
      missingAuthor: false,
      missingNote: false,
      eventTime: undefined as number | undefined,
      eventId: undefined as string | undefined
    }
  },
  created() {
    this.eventTime = this.$store.state.eventModule.selectedEventSummary?.approx_trigger_time;
    this.eventId = this.$store.state.eventModule.selectedEventSummary?.event_id;
  },
  methods: {
    close() {
      this.$emit('close');
    },
    submit(): void {
      const authorInput = this.$refs.author.value;
      const noteInput = this.$refs.note.value;
      this.missingAuthor = authorInput === '';
      this.missingNote = noteInput === '';
      if (!this.missingAuthor && !this.missingNote) {
        this.$store.dispatch(MESSAGE_ACTIONS.PUT_EVENT_HISTORY_NOTE, {
          eventId: this.eventId,
          author: authorInput,
          entry: noteInput,
          time: Date.now()
        });
        this.close();
      }
    },
    formatDate(mssue: number | undefined): string {
      return mssue ? formatUTC('y-MM-dd HH:mm:ss', new Date(mssue)) : '';
    }
  }
}
</script>

<style lang="scss" scoped>
  @import '@/assets/scss/colors.scss';

  textarea {
    font-family: sans-serif;
    resize: none;
  }

  .buttons-container{
    padding: 0;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .button {
    max-width: 200px;
  }

  p {
    margin: 0;
  }

  .error-container {
    background-color: $error-red;
    color: $grey;
    font-size: 25px;
    text-align: center;
    font-weight: bolder;

    & p {
      margin: 0;
      padding: .25em;
    }
  }

  h2 {
    text-align: center;
    margin: .5em 0;
  }

  .event-time {
    text-align: center;
    margin: 0 0 2em 0;
  }
</style>
