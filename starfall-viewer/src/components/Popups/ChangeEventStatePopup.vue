
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
    <div class="popup-base" >
      <h2 class="title">Change Event State</h2>
      <div class="flex">
        <div class="left">
          <EventDetails :eventSummary="eventSummary" :saveButton="false" class="mr15" style="border-radius: 4px; padding: 8px 6px;"/>
        </div>
        <div>
          <label for="change-event-state-author" class="left no-select label">Author <span class="error" v-if="author === '' && validation">missing author</span></label>
          <input id="change-event-state-author" v-model="author" class="input">

          <label for="change-event-state-note" class="left no-select label">Note <span class="error" v-if="note === '' && validation">missing note</span></label>
          <textarea id="change-event-state-note" v-model="note" rows="5" cols="20" class="textarea"></textarea>
        </div>
      </div>
      <div class="flex-center mt-1">
        <AcceptDeferReject @change="updateProcessingState" />
      </div>
      <div v-if="validation" class="error-container">
        <p v-if="!validateState(state)">Select One: Accept, Defer, Reject</p>
      </div>
      <div class="buttons-container">
        <button class="btn-base button submit" @click="submit">Submit</button>
        <button class="btn-base button cancel" @click="close">Cancel</button>
      </div>
    </div>
    <div @click="close" class="popup-background"/>
  </div>
</template>

<script lang="ts">
import AcceptDeferReject from '@/components/AcceptDeferReject.vue';
import EventDetails from '@/components/EventDetails.vue';
import { ACTIONS as MESSAGE_ACTIONS } from '@/store/modules/MessageModule';
import { ProcessingState, stateStr } from 'starfall-common/Types/ProcessingState';

export default {
  name: 'ChangeEventStatePopup',
  components: {
    AcceptDeferReject,
    EventDetails
  },
  data() {
    return {
      author: '',
      note: '',
      state: '' as ProcessingState,
      validation: false,
      ProcessingState: ProcessingState
    }
  },
  methods: {
    close() {
      this.$emit('close')
    },
    updateProcessingState(newValue) {
      this.state = newValue;
    },
    validateState(state) {
      return state === ProcessingState.Accepted || state === ProcessingState.Deferred || state === ProcessingState.Rejected;
    },
    submit(): void {
      this.validation = true;
      if (this.author && this.note && this.validateState(this.state)) {
        this.$store.dispatch(MESSAGE_ACTIONS.PUT_EVENT_HISTORY_NOTE, {
          eventId: this.eventId,
          author: this.author,
          entry: `Changed processing state to: ${stateStr[this.state]}`,
          time: Date.now()
        });

        this.$store.dispatch(MESSAGE_ACTIONS.CHANGE_EVENT_PROCESSING_STATE, {
          eventId: this.eventId,
          state: this.state
        });

        this.$store.dispatch(MESSAGE_ACTIONS.PUT_EVENT_HISTORY_NOTE, {
          eventId: this.eventId,
          author: this.author,
          entry: this.note,
          time: Date.now()
        });
        this.close();
      }
    },
  },
  computed: {
    eventSummary() {
      return this.$store.state.eventModule.selectedEventSummary;
    },
    eventId() {
     return this.$store.state.eventModule.selectedEventSummary?.event_id;
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

.title {
  text-align: center;
}
.label {
  font-weight: 600;
  font-size: 14px;
  font-variant-caps:small-caps;
}
.flex-center {
  width: 100%;
  display: flex;
  justify-content: center;
}
.mr15 {
  margin-right: 15px;
}
.mt-1 {
  margin-top: 1em;
}
.flex {
  display: flex;
  justify-content: space-between;
  padding: 10px 15px 0 15px;
}
.left {
  text-align: left;
}
p {
  margin-bottom: 0;
}
textarea {
  font-family: sans-serif;
  resize: none;
}
.buttons-container {
  padding: .25em 0;
  display: flex;
  justify-content: center;
}
.button {
  max-width: 200px;
}
.error {
  font-variant-caps: normal;
  font-size: 12px;
  background-color: $error-red;
  color: $grey;
  padding: 0 2px;
  border-radius: 2px;
}
.error-container {
  text-align: center;
  font-weight: bolder;
  margin: auto;
  width: 100%;

  & p {
    background-color: $error-red;
    color: $grey;
    font-size: 12px;
    border-radius: 2px;
    display: inline-block;
    margin: 0;
    padding: .25em;
  }
}
</style>
