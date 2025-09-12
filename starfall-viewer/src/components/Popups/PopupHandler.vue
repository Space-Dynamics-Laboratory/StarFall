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
    <AboutPopup            
      v-if="popup === MUTATIONS.CREATE_ABOUT_POPUP"
      @close="close"
    />
    <AttributionsPopup     
      v-if="popup === MUTATIONS.CREATE_ATTRIBUTIONS_POPUP"
      @close="close"
    />
    <ChangeEventStatePopup 
      v-if="popup === MUTATIONS.CREATE_EVENT_STATUS_POPUP"
      @close="close"
    />
    <ConfirmationPopup     
      v-if="popup === MUTATIONS.CREATE_CONFIRMATION_POPUP"
      :title="payloadProps.title"
      :message="payloadProps.message"
      :confirmButtonText="payloadProps.confirmButtonText || 'Yes'"
      :cancelButtonText="payloadProps.cancelButtonText || 'No'"
      :onConfirm="payloadProps.onConfirm || (() => {})"
      @close="close"
    />
    <EventAlertPopup       
      v-if="popup === MUTATIONS.CREATE_EVENT_ALERT_POPUP"
      :eventSummary="payloadProps.eventSummary || {}"
      @close="close"
    />
    <HistoryNotePopup      
      v-if="popup === MUTATIONS.CREATE_HISTORY_NOTE_POPUP"
      @close="close"
    />
    <InfoPopup             
      v-if="popup === MUTATIONS.CREATE_INFO_POPUP"
      :title="payloadProps.title"
      :message="payloadProps.message"
      :confirmButtonText="payloadProps.confirmButtonText || 'Close'"
      :onConfirm="payloadProps.onConfirm || (() => {})"
      @close="close"
    />
    <SaveFilterPopup       
      v-if="popup === MUTATIONS.CREATE_SAVE_FILTER_POPUP"
      @close="close"
    />
</template>

<script lang="ts">
import AboutPopup from '@/components/Popups/AboutPopup.vue';
import AttributionsPopup from '@/components/Popups/AttributionsPopup.vue';
import ChangeEventStatePopup from '@/components/Popups/ChangeEventStatePopup.vue';
import ConfirmationPopup from '@/components/Popups/ConfirmationPopup.vue';
import EventAlertPopup from '@/components/Popups/EventAlertPopup.vue';
import HistoryNotePopup from '@/components/Popups/HistoryNotePopup.vue';
import InfoPopup from '@/components/Popups/InfoPopup.vue';
import SaveFilterPopup from '@/components/Popups/SaveFilterPopup.vue';
import { MUTATIONS } from '@/store/modules/PopupsModule';
import { useToast } from 'vue-toastification'
import { TYPE } from "vue-toastification";

const toast = useToast()

const popups = {
  [MUTATIONS.CREATE_ABOUT_POPUP]: true,
  [MUTATIONS.CREATE_ATTRIBUTIONS_POPUP]: true,
  [MUTATIONS.CREATE_CONFIRMATION_POPUP]: true,
  [MUTATIONS.CREATE_EVENT_ALERT_POPUP]: true,
  [MUTATIONS.CREATE_EVENT_STATUS_POPUP]: true,
  [MUTATIONS.CREATE_HISTORY_NOTE_POPUP]: true,
  [MUTATIONS.CREATE_INFO_POPUP]: true,
  [MUTATIONS.CREATE_SAVE_FILTER_POPUP]: true,
  [MUTATIONS.CREATE_TOAST_POPUP]: true
};

export default {
  name: 'PopupHandler',
  components: {
    AboutPopup,
    AttributionsPopup,
    ChangeEventStatePopup,
    ConfirmationPopup,
    EventAlertPopup,
    HistoryNotePopup,
    InfoPopup,
    SaveFilterPopup
  },
  data() {
    return {
      popup: undefined as undefined | string,
      payloadProps: undefined as Object | undefined
    }
  },
  methods: {
    close() {
      this.popup = undefined
      this.payloadProps = undefined
    }
  },
  mounted() {
    this.$store.subscribe((mutation) => {
      if (popups[mutation.type]) {
        this.popup = mutation.type
        this.payloadProps = mutation.payload

        if (this.popup === MUTATIONS.CREATE_TOAST_POPUP) {
          const toastTypes = {
            [TYPE.INFO]: toast.info,
            [TYPE.SUCCESS]: toast.success,
            [TYPE.ERROR]: toast.error,
            [TYPE.WARNING]: toast.warning,
          }
          toastTypes[this.payloadProps.icon](this.payloadProps.title)
        }
      }
    });
  },
  computed: {
    MUTATIONS: () => MUTATIONS
  }
}
</script>

<style lang="scss" scoped>

</style>
