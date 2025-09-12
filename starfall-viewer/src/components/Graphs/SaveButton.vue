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
  <button class="btn" @click="saveElement" :title="tooltip" :disabled="!$store.state.eventModule.selectedEventSummary">
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-image-down"><path d="M10.3 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10l-3.1-3.1a2 2 0 0 0-2.814.014L6 21"/><path d="m14 19 3 3v-5.5"/><path d="m17 22 3-3"/><circle cx="9" cy="9" r="2"/></svg>
  </button>
</template>

<script lang="ts">
import html2canvas from 'html2canvas';
import { MUTATIONS as POPUP_MUTATIONS } from '@/store/modules/PopupsModule';
import { formatUTC } from 'starfall-common/helpers/time';

export default {
  name: 'SaveButton',
  props: {
    tooltip: {
      default: '',
      type: String
    },
    elementId: {
      type: String,
      required: true
    }
  },
  computed: {
    detailView() {
      return this.$store.state.eventModule.detailView;
    }
  },
  methods: {
    saveElement(): void {
      document.body.classList.add('waiting');
      setTimeout(() => {
        const element = document.getElementById(this.elementId);
        const date = new Date(this.$store.state.eventModule.selectedEventSummary?.approx_trigger_time || '');
        const dateStr = formatUTC('y-MM-dd_HH-mm-ss', date);

        if (!element) { alert('failed to save graph'); return; }

        html2canvas(element, { scale: 2 })
          .then((canvas) => {
            this.saveAs(canvas, `starfall_${dateStr}_${this.elementId}.png`);
            document.body.classList.remove('waiting');
          });
      }, 0);
    },
    saveAs(canvas: HTMLCanvasElement, filename: string): void {
      const element = document.createElement('a');
      element.download = filename;
      element.style.display = 'none';
      element.href = canvas.toDataURL('image/png')
        .replace(/^data:image\/[^;]/, 'data:application/octet-stream');

      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    }
  }
}
</script>
