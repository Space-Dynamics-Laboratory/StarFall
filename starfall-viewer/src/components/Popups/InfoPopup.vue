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
      <div>
        <h1 id="title">{{ title }}</h1>
        <p id="message">{{ message }}</p>
      </div>
      <div class="buttons-container">
        <button class="btn-base submit button center" @click="confirm">{{ confirmButtonText }}</button>
      </div>
    </div>
    <div @click="close" class="popup-background"/>
  </div>
</template>

<script lang="ts">

export default {
  name: 'ConfirmationPopup',
  props: {
    title: String,
    message: String,
    confirmButtonText: {
      type: String,
      default: 'Close'
    },
    onConfirm: {
      type: Function,
      default: () => {}
    }
  },
  methods: {
    close() {
      this.$emit('close');
    },
    confirm(): void {
      this.onConfirm();
      this.close();
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

#title {
  text-align: center;
}

#message {
  white-space: pre-wrap;
  text-align: center;
  font-size: 15pt;
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

</style>
