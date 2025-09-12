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
  <div class="graph-container">
    <div class="graph-controls">
      <div class="button-group">
        <button title="Redraw Graph" @click="draw()">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-refresh-cw"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>
        </button>
        <save-button elementId="groundTrackGraph" tooltip="Save Graph"/>
        <button :class="lines ? 'active' : ''" class="btn" @click="lines = !lines" :title="lines ? 'hide lines' : 'show lines'">
          <svg width="12" height="12">
            <line x1="0" y1="12" x2="12" y2="0" stroke="black" stroke-width="2"/>
          </svg>
        </button>
      </div>
    </div>
    <div ref="graph" class="graph" id="groundTrackGraph">
        <GroundTrackLegend class="legend" :timeMin="timeMin" :timeMax="timeMax"/>
    </div>
  </div>
</template>

<script lang="ts">
import { scaleLinear } from 'd3-scale';
import type { ScaleLinear, ScaleLogarithmic } from 'd3-scale';
import { axisBottom, axisLeft } from 'd3-axis';
import { brush } from 'd3-brush';
import { select } from 'd3-selection';
import { line } from 'd3-shape';
import { transition } from 'd3-transition';

import GroundTrackLegend from '@/components/Graphs/GroundTrackLegend.vue';
import SaveButton from './SaveButton.vue';
import ecef from 'starfall-common/ecef';
import type { PointSource } from '@/types/PointSource';
import { getSensorColor } from '@/store/Helpers/getSensorColor';
import type { SensorColor, SensorLine } from '@/store/modules/SettingsModule';
import { getSensorLine } from '@/store/Helpers/getSensorLine';
import tinycolor from 'tinycolor2';

export default {
  name: 'GroundTrackGraph',
  components: {
    GroundTrackLegend,
    SaveButton
  },
  props: {
    graphSize: {
      type: Number,
      default: 35,
      required: true
    }
  },
  data() {
    return {
      x: (() => {}) as ScaleLinear<number, number, never> | (() => void),
      y: (() => {}) as ScaleLinear<number, number, never> | ScaleLogarithmic<number, number, never> | (() => void),
      xMin: 0,
      xMax: 0,
      yMin: 0,
      yMax: 0,
      timeMin: 0,
      timeMax: 0,
      shapes: undefined,
      svg: undefined,
      xAxis: undefined,
      yAxis: undefined,
      brush: undefined,
      lines: true,
      margin: {
        top: 5,
        right: 150,
        left: 65,
        bottom: 40
      },
      squareSize: 6,
      circleSize: 3,
      idleTimeout: null as any | null,
      idleDelay: 350
    }
  },
  mounted() {
    this.$store.watch((state) => state.eventModule.event, this.draw);
  },
  methods: {
    draw(): void {
      if (!this.$refs.graph) return;
      if (!this.$store.state.eventModule.event) {
        this.drawAxes();
        return;
      }
      select('#svgGroundGraph').remove();

      const parentWidth = this.$refs.graph.offsetWidth;
      const parentHeight = this.$refs.graph.offsetHeight;
      const graphWidth = parentWidth - this.margin.right - this.margin.left;
      const graphHeight = parentHeight - this.margin.top - this.margin.bottom;
      if (graphWidth < 0 || graphHeight < 0) {
        return;
      }

      this.yMin = Number.MAX_VALUE;
      this.yMax = -Number.MAX_VALUE;
      this.xMin = Number.MAX_VALUE;
      this.xMax = -Number.MAX_VALUE;
      this.timeMin = Number.MAX_VALUE;
      this.timeMax = -Number.MAX_VALUE;
      Object.values(this.$store.state.eventModule.event.sightings).forEach(sighting => {
        sighting.forEach(ps => {
          this.timeMin = Math.min(this.timeMin, ps.time);
          this.timeMax = Math.max(this.timeMax, ps.time);
          const latLonAltFar = ecef.unproject(ps.meas_far_point_ecef_m);
          this.yMin = Math.min(this.yMin, latLonAltFar[0]);
          this.yMax = Math.max(this.yMax, latLonAltFar[0]);
          this.xMin = Math.min(this.xMin, latLonAltFar[1]);
          this.xMax = Math.max(this.xMax, latLonAltFar[1]);
        });
      });

      // Add 10% buffer to the graph 
      const factor = 0.1;
      const yBuffer = Math.abs(this.yMax - this.yMin) * factor;
      const xBuffer = Math.abs(this.xMax - this.xMin) * factor;
      this.yMax += yBuffer;
      this.yMin -= yBuffer;
      this.xMax += xBuffer;
      this.xMin -= xBuffer;

      // define x and y domain and ranges
      this.y = scaleLinear()
        .domain([this.yMin, this.yMax]).nice()
        .range([graphHeight, 0]);

      this.x = scaleLinear()
        .domain([this.xMin, this.xMax]).nice()
        .range([0, graphWidth]);

      this.xAxis = axisBottom(this.x)
        .ticks(12)
        .tickSizeInner(-graphHeight);
      this.yAxis = axisLeft(this.y)
        .tickSizeInner(-graphWidth)
        .ticks(12 * graphHeight / graphWidth + 1);

      this.brush = brush()
        .extent([[0, 0], [graphWidth, graphHeight]])
        .on('end', this.brushEnded);

      // define graph container
      this.svg = select('#groundTrackGraph')
        .append('svg')
        .attr('id', 'svgGroundGraph')
        .attr('width', graphWidth + this.margin.right + this.margin.left)
        .attr('height', graphHeight + this.margin.top + this.margin.bottom)
        .style('background-color', '#f1f1f1')
        .append('g')
        .attr('transform', `translate(${this.margin.left}, ${this.margin.top})`);

      this.svg
        .append('rect')
        .attr('id', 'groundTrackGraphBackground')
        .attr('fill', '#ffffff')
        .attr('width', graphWidth)
        .attr('height', graphHeight)
        .attr('x', 0)
        .attr('y', 0);

      this.svg.append('defs')
        .append('svg:clipPath')
        .attr('id', 'clip-ground')
        .append('svg:rect')
        .attr('width', graphWidth)
        .attr('height', graphHeight)
        .attr('x', 0)
        .attr('y', 0);

      this.shapes = this.svg.append('g')
        .attr('id', 'shapes-ground')
        .attr('clip-path', 'url(#clip-ground)');

      // create a line for each point source
      Object.values(this.$store.state.eventModule.event.sightings).forEach((sighting, sindx) => {
        if (sighting.length === 0) return;
        const color = getSensorColor(sighting[0].sensor_id);
        const lines = getSensorLine(sighting[0].sensor_id);

        if (lines) {
          const fillColor = (ps: PointSource) => tinycolor.fromRatio({ r: color.red, g: color.green, b: color.blue }).lighten(((this.timeMax - ps.time) / (this.timeMax - this.timeMin)) * 25).toRgbString();
          const strokeColor = (ps: PointSource) => tinycolor.fromRatio({ r: color.red, g: color.green, b: color.blue }).lighten(((this.timeMax - ps.time) / (this.timeMax - this.timeMin) - 0.1) * 25).toRgbString();

          // create line
          this.shapes.append('path')
            .datum(sighting)
            .attr('id', 'pathPS')
            .attr('fill', 'none')
            .attr('stroke', fillColor)
            .attr('stroke-width', 2)
            .style('display', this.lines ? 'inherit' : 'none')
            .attr('d', line<PointSource>()
              .x((ps: PointSource) => this.x(ecef.unproject(ps.meas_far_point_ecef_m)[1]) - this.squareSize / 2)
              .y((ps: PointSource) => this.y(ecef.unproject(ps.meas_far_point_ecef_m)[0]) - this.squareSize / 2));

          this.shapes.selectAll('#far-dot')
            .data(sighting)
            .enter()
            .append('circle')
            .attr('id', 'far-dot' + sindx)
            .attr('r', this.circleSize)
            .attr('cx', (ps: PointSource) => this.x(ecef.unproject(ps.meas_far_point_ecef_m)[1]) - this.squareSize / 2)
            .attr('cy', (ps: PointSource) => this.y(ecef.unproject(ps.meas_far_point_ecef_m)[0]) - this.squareSize / 2)
            .attr('lon', (ps: PointSource) => ecef.unproject(ps.meas_far_point_ecef_m)[1])
            .attr('lat', (ps: PointSource) => ecef.unproject(ps.meas_far_point_ecef_m)[0])
            .attr('fill', fillColor)
            .attr('stroke', strokeColor);
        }
      });

      // x-axis
      this.svg.append('g')
        .attr('class', 'x-axis')
        .attr('id', 'axis-ground-x')
        .attr('transform', 'translate(0,' + graphHeight + ')')
        .call(this.xAxis);

      this.svg.append('text')
        .style('text-anchor', 'middle')
        .attr('x', graphWidth / 2)
        .attr('y', graphHeight + 30)
        .style('font-size', '11pt')
        .text('Longitude (\xB0)');

      // y-axis
      this.svg.append('g')
        .attr('class', 'y-axis')
        .attr('id', 'axis-ground-y')
        .call(this.yAxis);

      this.svg.append('text')
        .attr('transform', 'rotate(-90)')
        .style('text-anchor', 'middle')
        .attr('y', -50)
        .attr('x', -graphHeight / 2)
        .style('font-size', '11pt')
        .text('Latitude (\xB0)');

      this.shapes.append('g')
        .attr('class', 'brush')
        .call(this.brush);
    },
    brushEnded(e: any) {
      const s = e.selection;
      if (!s) {
        if (!this.idleTimeout) {
          this.idleTimeout = setTimeout(this.idled, this.idleDelay);
          return this.idleTimeout;
        }
        this.x.domain([this.xMin, this.xMax]).nice();
        this.y.domain([this.yMin, this.yMax]).nice();
      } else {
        this.x.domain([s[0][0], s[1][0]].map(this.x.invert, this.x));
        this.y.domain([s[1][1], s[0][1]].map(this.y.invert, this.y));
        this.shapes.select('.brush').call(this.brush.move, null);
      }
      this.zoom();
    },
    idled() {
      this.idleTimeout = null;
    },
    zoom() {
      const t = transition().duration(750);
      this.svg.select('#axis-ground-x').transition(t).call(this.xAxis);
      this.svg.select('#axis-ground-y').transition(t).call(this.yAxis);

      if (this.$store.state.eventModule.event) {
        this.shapes.selectAll('#pathPS').transition(t)
          .attr('d', line<PointSource>()
            .x((ps: PointSource) => this.x(ecef.unproject(ps.meas_far_point_ecef_m)[1]) - this.squareSize / 2)
            .y((ps: PointSource) => this.y(ecef.unproject(ps.meas_far_point_ecef_m)[0]) - this.squareSize / 2)
          );

        Object.values(this.$store.state.eventModule.event.sightings).forEach((sighting, sindx) => {
          if (sighting.length === 0) return;
          this.shapes.selectAll('#far-dot' + sindx).transition(t)
            .attr('cx', (ps: PointSource) => this.x(ecef.unproject(ps.meas_far_point_ecef_m)[1]) - this.squareSize / 2)
            .attr('cy', (ps: PointSource) => this.y(ecef.unproject(ps.meas_far_point_ecef_m)[0]) - this.squareSize / 2);
        });
      }
    },
    drawAxes() {
      select('#svgGroundGraph').remove();
      const parentWidth = this.$refs.graph.offsetWidth;
      const parentHeight = this.$refs.graph.offsetHeight;
      const graphWidth = parentWidth - this.margin.right - this.margin.left;
      const graphHeight = parentHeight - this.margin.top - this.margin.bottom;
      if (graphWidth < 0 || graphHeight < 0) {
        return;
      }

      this.y = scaleLinear()
        .domain([0, 10]).nice()
        .range([graphHeight, 0]);

      this.x = scaleLinear()
        .domain([0, 10]).nice()
        .range([0, graphWidth]);

      this.xAxis = axisBottom(this.x).ticks(12);
      this.yAxis = axisLeft(this.y).ticks(12 * graphHeight / graphWidth + 1);

      // define graph container
      this.svg = select('#groundTrackGraph')
        .append('svg')
        .attr('id', 'svgGroundGraph')
        .attr('width', graphWidth + this.margin.right + this.margin.left)
        .attr('height', graphHeight + this.margin.top + this.margin.bottom)
        .style('background-color', '#f1f1f1')
        .append('g')
        .attr('transform', `translate(${this.margin.left}, ${this.margin.top})`);

      this.svg
        .append('rect')
        .attr('id', 'groundTrackGraphBackground')
        .attr('fill', '#ffffff')
        .attr('width', graphWidth)
        .attr('height', graphHeight)
        .attr('x', 0)
        .attr('y', 0);

      this.svg.append('defs')
        .append('svg:clipPath')
        .attr('id', 'clip-ground')
        .append('svg:rect')
        .attr('width', graphWidth)
        .attr('height', graphHeight)
        .attr('x', 0)
        .attr('y', 0);

      this.shapes = this.svg.append('g')
        .attr('id', 'shapes-ground')
        .attr('clip-path', 'url(#clip-ground)');

      // x-axis
      this.svg.append('g')
        .attr('class', 'x-axis')
        .attr('id', 'axis-ground-x')
        .attr('transform', 'translate(0,' + graphHeight + ')')
        .call(this.xAxis);

      this.svg.append('text')
        .style('text-anchor', 'middle')
        .attr('x', graphWidth / 2)
        .attr('y', graphHeight + 30)
        .style('font-size', '11pt')
        .text('Longitude (\xB0)');

      // y-axis
      this.svg.append('g')
        .attr('class', 'y-axis')
        .attr('id', 'axis-ground-y')
        .call(this.yAxis);

      this.svg.append('text')
        .attr('transform', 'rotate(-90)')
        .style('text-anchor', 'middle')
        .attr('y', -50)
        .attr('x', -graphHeight / 2)
        .style('font-size', '11pt')
        .text('Latitude (\xB0)');
    }
  },
  computed: {
    sensorColors(): SensorColor[] {
      return this.$store.state.settingsModule.sensorColorList;
    },
    sensorLines(): SensorLine[] {
      return this.$store.state.settingsModule.sensorLineList;
    }
  },
  watch: {
    graphSize() {
      setTimeout(this.draw, 1);
    },
    sensorColors(): void {
      this.draw();
    },
    sensorLines(): void {
      this.draw();
    },
    lines(): void {
      if (this.lines && this.shapes) {
        this.shapes
          .selectAll('#pathPS')
          .style('display', 'inherit');
      } else if (this.shapes) {
        this.shapes
          .selectAll('#pathPS')
          .style('display', 'none');
      }
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

.graph-container {
  height: 100%;
  background-color: $white;
  display: flex;
  flex-direction: column;
}
.graph {
  flex-grow: 1;
  display: flex;
  width: 100%;
  background-color: $white;
  color: black;
  overflow: hidden;
  position: relative;
  padding-bottom: 2em;
}
.legend {
  margin-bottom: 60px;
}
.graph-controls button, .graph-controls select {
  border: 1px solid #7E8086;
  display: inline-flex;
  align-items: center;
  height: 22px;
}
.button-group {
  display: flex;
  margin-left: 2px;
  margin-top: 2px;
}
.button-group button, .button-group select {
  border-right: none;
  border-radius: 0;
}
.button-group *:first-child {
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
}
.button-group *:last-child:not(svg) {
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
  border-right: 1px solid #7E8086;
}
.btn.active {
  background: #D0D0D7;
  box-shadow: inset 1px 1px 4px 1px rgba(0,0,0,0.2);
}
</style>
