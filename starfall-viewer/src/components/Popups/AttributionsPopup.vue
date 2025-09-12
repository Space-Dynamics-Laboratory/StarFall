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
      <div class="flex">
        <h1 id="title">ATTRIBUTION</h1>
      </div>
      <div class="attributions-container">
        <div class="attribution" v-for="(attribution, index) in attributions" :key="index">
          <h1 id="version">{{ attribution.name }}</h1>
          <h3>License: {{ attribution.license }}</h3>
          <div v-for="link in attribution.links" :key="link">
            <a :href="link" target="_blank" rel="noopener noreferrer">{{ link }}</a>
          </div>
          <p v-if="attribution.credit">Credit: {{ attribution.credit }}</p>
          <p>{{ attribution.information }}</p>
      </div>
      </div>
      <div class="buttons-container">
        <button class="btn-base button submit center" @click="close">OK</button>
      </div>
    </div>
    <div @click="close" class="popup-background"/>
  </div >
</template>

<script lang="ts">
import type { Attribution } from '@/types/Attribution';

export default {
  name: 'AttributionsPopup',
  methods: {
    close() {
      this.$emit('close')
    }
  },
  computed: {
    attributions: (): Attribution[] => [
      {
        name: 'Satellite Model',
        links: ['https://nasa3d.arc.nasa.gov/detail/cloudsat', 'https://www.nasa.gov/multimedia/guidelines/index.html'],
        credit: 'Kevin Lane. NASA/JPL-Caltech'
      },
      {
        name: 'Cesium',
        license: 'Apache License Version 2.0, January 2004',
        links: ['http://www.apache.org/licenses/LICENSE-2.0', 'https://github.com/CesiumGS/cesium/blob/master/LICENSE.md']
      }
    ]
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

.attributions-container {
  align-content: center;
  overflow: auto;
  text-align: left;
  max-height: 400px;
  // box-shadow: 0px 0px 5px rgba($black, .25);
  display: inline-block;
  padding: 0 .5em;
  margin-bottom: .5em;
}

.attribution {
  border-radius: 5px;
  background: rgba($black, .03);
  border: 1px solid rgba($black, .25);
  margin-bottom: .5em;
  padding: .25em;
}

.flex {
  display: flex;
  justify-content: space-around;
  align-items: center;
}

#title {
  display: inline-block;
}

#version {
  margin-top: 0;
}

a {
  text-decoration: none;
}

.buttons-container {
  padding: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.button {
  max-width: 200px;
}

</style>
