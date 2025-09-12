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
  <Slider
    v-model="sliderLinear"
    :min="0"
    :max="100"
    :disabled="!enabled"
    :tooltips="false"
    @update:modelValue="handleChange"
    v-bind="$attrs"
  />
</template>

<script>
import Slider from '@vueform/slider'

export default {
  name: 'LogScaleSlider',
  components: { Slider },
  props: {
    modelValue: {
      type: Array, // [logMin, logMax]
      required: true
    },
    lowerBound: {
      type: Number,
      required: true // e.g. 1e7
    },
    upperBound: {
      type: Number,
      required: true // e.g. 1e12
    },
    enabled: {
      type: Boolean,
      default: true
    }
  },
  emits: ['update:modelValue', 'change'],
  data() {
    return {
      sliderLinear: [0, 100]
    }
  },
  watch: {
    lowerBound: 'syncFromModel',
    upperBound: 'syncFromModel'
  },
  methods: {
    mapSliderToLog(sliderVal, min, max) {
      const logMin = Math.log10(min)
      const logMax = Math.log10(max)
      const scale = sliderVal / 100 // normalized [0, 1]
      const logValue = logMin + scale * (logMax - logMin)
      return Math.pow(10, logValue)
    },
    mapLogToSlider(logVal, min, max) {
      const logMin = Math.log10(min)
      const logMax = Math.log10(max)
      const logCurrent = Math.log10(logVal)
      const scale = (logCurrent - logMin) / (logMax - logMin)
      return Math.round(scale * 100)
    },
    handleChange() {
      const [lowRaw, highRaw] = this.sliderLinear.map(val =>
        this.mapSliderToLog(val, this.lowerBound, this.upperBound)
      )

      // Fix floating point error: floor low, ceil high
      const low = Math.floor(lowRaw)
      const high = Math.ceil(highRaw)

      this.$emit('update:modelValue', [low, high])
      this.$emit('change', [low, high])
    },
    syncFromModel() {
      if (!Array.isArray(this.modelValue) || this.modelValue.length !== 2) return

      this.sliderLinear = this.modelValue.map(val =>
          this.mapLogToSlider(val, this.lowerBound, this.upperBound)
      )
    }
  }
}
</script>
