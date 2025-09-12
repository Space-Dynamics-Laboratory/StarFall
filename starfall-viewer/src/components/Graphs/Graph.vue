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
    <div class="graph-controls button-group">
      <button title="Redraw Graph" @click="draw()">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-refresh-cw"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>
      </button>
      <save-button :elementId="elid" tooltip="Save Graph"/>
    </div>
    <div ref="graph" :id="elid" class="graph">
      <div class="legend-container">
        <GraphLegend class="legend" :sensorIds="sensorIds"/>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { scaleLinear } from 'd3-scale';
import type { NumberValue, ScaleLinear, ScaleLogarithmic } from 'd3-scale';
import { axisBottom, axisLeft } from 'd3-axis';
import type { Axis, AxisDomain } from 'd3-axis';
import { brush } from 'd3-brush';
import type { BrushBehavior } from 'd3-brush';
import { format } from 'd3-format';
import { line } from 'd3-shape';
import { select } from 'd3-selection';
import { transition } from 'd3-transition';

import GraphLegend from './GraphLegend.vue';
import SaveButton from './SaveButton.vue';
import type { Point, Curve } from './types';
import { getSensorColor } from '@/store/Helpers/getSensorColor';
import type { SensorColor, SensorLine } from '@/store/modules/SettingsModule';
import { getSensorLine } from '@/store/Helpers/getSensorLine';
import { formatUTC } from '../../../../starfall-common/helpers/time';
import type { PropType } from 'vue';

export default {
  name: 'Graph',
  components: {
    SaveButton,
    GraphLegend,
  },
  props: {
    curves: {
      type: Object as PropType<Curve[]>,
      required: true
    },
    graphSize: {
      type: Number,
      default: 35,
      required: true
    },
    elid: {
      type: String,
      required: true
    },
    yLabel: {
      type: String,
      required: true
    },
    type: {
      type: Number,
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
      shapes: undefined as any,
      svg: undefined as any,
      xAxis: undefined as  Axis<NumberValue> | undefined,
      yAxis: undefined as Axis<number> | undefined,
      y2Axis: undefined as Axis<number> | undefined,
      brush: undefined as BrushBehavior<unknown> | undefined,
      margin: {
        top: 5,
        right: 20,
        left: 180,
        bottom: 40
      },
      idleTimeout: null as any | null,
      idleDelay: 350,
    }
  },
  computed: {
    svgid(): string { return 'svg' + this.elid; },
    clipid(): string { return 'clip' + this.elid; },
    sensorIds(): Set<number> {
      const ids = new Set<number>();
      for (const curve of this.curves) {
        ids.add(curve.sensorId);
      }
      return ids;
    },
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
    }
  },
  methods: {
    draw(): void {
      if (!this.$refs.graph) return;
      if (!this.$store.state.eventModule.event) {
        this.drawAxes();
        return;
      }
      select(`#${this.svgid}`).remove();

      const parentWidth = this.$refs.graph.offsetWidth;
      const parentHeight = this.$refs.graph.offsetHeight;
      const graphWidth = parentWidth - this.margin.right - this.margin.left;
      const graphHeight = parentHeight - this.margin.top - this.margin.bottom;
      if (graphWidth < 0 || graphHeight < 0) {
        return;
      }

      this.xMin = Number.MAX_VALUE;
      this.xMax = -Number.MAX_VALUE;
      this.yMin = Number.MAX_VALUE;
      this.yMax = -Number.MAX_VALUE;
      this.curves.forEach(curve => {
        curve.points.forEach(point => {
          this.xMin = Math.min(this.xMin, Math.min(point.x));
          this.xMax = Math.max(this.xMax, Math.max(point.x));
          this.yMin = Math.min(this.yMin, Math.min(point.y));
          this.yMax = Math.max(this.yMax, Math.max(point.y));
        });
      });

      this.y = scaleLinear()
        .domain([this.yMin, this.yMax]).nice()
        .range([graphHeight, 0]);

      this.x = scaleLinear()
        .domain([this.xMin, this.xMax]).nice()
        .range([0, graphWidth]);

      const tickFormatter = (mssue: AxisDomain): string =>
        typeof mssue !== 'number' ? `${mssue}` : formatUTC('HH:mm:ss.SS', new Date(mssue));

      this.xAxis = axisBottom(this.x)
        .ticks(12)
        .tickFormat(tickFormatter)
        .tickSizeInner(-graphHeight);
      this.yAxis = axisLeft<number>(this.y)
        .tickSizeInner(-graphWidth)
        .ticks(12 * graphHeight / graphWidth + 1)
        .tickFormat(format('.1e'));

      this.brush = brush().extent([[0, 0], [graphWidth, graphHeight]])
        .on('end', this.brushEnded);

      // define graph container
      this.svg = select(`#${this.elid}`)
        .append('svg')
        .attr('id', this.svgid)
        .attr('width', graphWidth + this.margin.right + this.margin.left)
        .attr('height', graphHeight + this.margin.top + this.margin.bottom)
        .style('background-color', '#f1f1f1')
        .append('g')
        .attr('transform', `translate(${this.margin.left}, ${this.margin.top})`);

      this.svg
        .append('rect')
        .attr('id', `${this.elid}Background`)
        .attr('fill', '#ffffff')
        .attr('width', graphWidth)
        .attr('height', graphHeight)
        .attr('x', 0)
        .attr('y', 0);

      this.svg.append('defs')
        .append('svg:clipPath')
        .attr('id', this.clipid)
        .append('svg:rect')
        .attr('width', graphWidth)
        .attr('height', graphHeight)
        .attr('x', 0)
        .attr('y', 0);

      this.shapes = this.svg.append('g')
        .attr('id', 'shapes')
        .attr('clip-path', `url(#${this.clipid})`);

      this.curves.forEach(curve => {
        if (curve.points.length === 0) {
          return;
        }
        const color = getSensorColor(curve.sensorId);
        const rgb = `rgb(${color.red * 255},${color.green * 255},${color.blue * 255})`;
        const lines = getSensorLine(curve.sensorId);

        // create line
        if (lines) {
          this.shapes.append('path')
            .datum(curve.points)
            .attr('id', 'pathLC')
            .attr('fill', 'none')
            .attr('stroke', rgb)
            .attr('stroke-width', 2)
            .attr('d', line<Point>()
              .x((p: Point) => this.x(p.x))
              .y((p: Point) => this.y(p.y))
            );
        }
      });

      // x-axis
      this.svg.append('g')
        .attr('class', 'x-axis')
        .attr('id', 'axis-x')
        .attr('transform', 'translate(0,' + graphHeight + ')')
        .call(this.xAxis);

      const reference_time = this.$store.state.eventModule.selectedEventSummary?.approx_trigger_time || 0;
      this.svg.append('text')
        .style('text-anchor', 'middle')
        .attr('x', graphWidth / 2)
        .attr('y', graphHeight + 30)
        .style('font-size', '10pt')
        .text(formatUTC('y-MM-dd (DDD)', new Date(reference_time)) + ' HH:mm:ss.SS');

      // y-axis
      this.svg.append('g')
        .attr('class', 'y-axis')
        .attr('id', 'axis-y')
        .call(this.yAxis);

      this.svg.append('text')
        .attr('transform', 'rotate(-90)')
        .style('text-anchor', 'middle')
        .attr('y', -50)
        .attr('x', -graphHeight / 2)
        .style('font-size', '11pt')
        .text(this.yLabel);

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
      this.svg.select('#axis-x').transition(t).call(this.xAxis);
      this.svg.select('#axis-y').transition(t).call(this.yAxis);

      this.shapes.selectAll('#pathLC').transition(t)
        .attr('d', line<Point>()
          .x((p: Point) => this.x(p.x))
          .y((p: Point) => this.y(p.y))
        );
    },
    drawAxes() {
      select(`#${this.svgid}`).remove();

      const parentWidth = this.$refs.graph.offsetWidth;
      const parentHeight = this.$refs.graph.offsetHeight;
      const graphWidth = parentWidth - this.margin.right - this.margin.left;
      const graphHeight = parentHeight - this.margin.top - this.margin.bottom;
      if (graphHeight < 0 || graphWidth < 0) {
        return;
      }

      this.svg = select(`#${this.elid}`)
        .append('svg')
        .attr('id', this.svgid)
        .attr('width', graphWidth + this.margin.right + this.margin.left)
        .attr('height', graphHeight + this.margin.top + this.margin.bottom)
        .style('background-color', '#f1f1f1')
        .append('g')
        .attr('transform', `translate(${this.margin.left}, ${this.margin.top})`);

      this.svg
        .append('rect')
        .attr('id', `${this.elid}Background`)
        .attr('fill', '#ffffff')
        .attr('width', graphWidth)
        .attr('height', graphHeight)
        .attr('x', 0)
        .attr('y', 0);

      // x-axis
      this.svg.append('g')
        .attr('class', 'x-axis')
        .attr('id', 'axis-x')
        .attr('transform', 'translate(0,' + graphHeight + ')')
        .call(this.xAxis);

      this.svg.append('text')
        .style('text-anchor', 'middle')
        .attr('x', graphWidth / 2)
        .attr('y', graphHeight + 30)
        .style('font-size', '11pt')
        .text('YYYY (DOY) HH:mm:ss.zzz [ duration __ seconds ]');

      // y-axis
      this.svg.append('g')
        .attr('class', 'y-axis')
        .attr('id', 'axis-y')
        .call(this.yAxis);

      this.svg.append('text')
        .attr('transform', 'rotate(-90)')
        .style('text-anchor', 'middle')
        .attr('y', -50)
        .attr('x', -graphHeight / 2)
        .style('font-size', '11pt')
        .text(this.yLabel);
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
.legend-container {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  max-width: 110px;
  display: flex;
  flex-direction: column;
  justify-content: center;
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
</style>
