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
<div v-show="open" @click.self="toggle" class="popup-background">
  <div class="modal">
    <span @click="toggle" class="close">&times;</span>
    <slot name="content"></slot>
  </div>
</div>
</template>

<script lang="ts">

export default {
  name: 'Modal',
  props: {
    open: Boolean
  },
  methods: {
    toggle() {
      this.$emit('toggle-modal', this.open);
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

.popup-background {
  display: flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  // z-index: 100;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow-y: hidden;
  background-color: rgba(0,0,0,0.3);
}

.modal {
  position: relative;
  z-index: 101;
  background-color: white;
  margin: auto;
  padding: 20px;
  border: 1px solid #888;
  width: fit-content;
  overflow-y: hidden;
  border-radius: 5px;
}

.close {
  position: absolute;
  top: 0px;
  right: 6px;
  color: #aaaaaa;
  font-size: 28px;
  font-weight: bold;
  cursor: pointer;
}
.modal h2, .content h2 {
  margin-top: 0;
  padding-top: 0;
  margin-right: 20px;
}

</style>
