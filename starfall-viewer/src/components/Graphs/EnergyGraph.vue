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
        <save-button elementId="energyGraph" tooltip="Save Graph"/>
        <button title="Download JSON" @click="downloadJSON" :disabled="!$store.state.eventModule.selectedEventSummary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-file-down"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M12 18v-6"/><path d="m9 15 3 3 3-3"/></svg>
        </button>
        <toggle-line-button @toggle-lines="energyLines = !energyLines; draw();" :lines="energyLines"/>
        <toggle-scale-type-button @toggle-scale="linearScale = !linearScale; draw();" :linearScale="linearScale"/>
        <button class="mr" title="Graph Help"><fa-icon icon="question" @click="help"/></button>
      </div><!-- button-group -->
      <div v-if="overlayGraphs.length > 1">
        <label class="label sr-only" for="graph-overlay">Overlay</label>
        <div class="button-group">
        <select name="graph-overlay" id="graph-overlay" v-model="selectedOverlayId" title="select overlay graph">
          <option v-for="graph in overlayGraphs" :key="graph.value" :value="graph.value">{{ graph.label }}</option>
        </select>
        <button @click="zoomOut = !zoomOut" v-if="selectedOverlayId !== OVERLAY_NONE_ID"
          :title="!zoomOut ? 'Expand x-axis to fit overlay graph' : 'Shrink x-axis to fit energy graph points'"
        >
          <svg xmlns="http://www.w3.org/2000/svg"
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="3"
            stroke-linecap="round"
            stroke-linejoin="round"
            v-if="!zoomOut"
            style="transform: rotate(45deg);"
          >
            <polyline points="15 3 21 3 21 9"></polyline>
            <polyline points="9 21 3 21 3 15"></polyline>
            <line x1="21" y1="3" x2="14" y2="10"></line>
            <line x1="3" y1="21" x2="10" y2="14"></line>
          </svg>
          <svg xmlns="http://www.w3.org/2000/svg"
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="3"
            stroke-linecap="round"
            stroke-linejoin="round"
            v-else
            style="transform: rotate(45deg);"
          >
            <polyline points="4 14 10 14 10 20"></polyline>
            <polyline points="20 10 14 10 14 4"></polyline>
            <line x1="14" y1="10" x2="21" y2="3"></line>
            <line x1="3" y1="21" x2="10" y2="14"></line>
          </svg>
        </button>
        </div><!-- button-group -->
      </div>
    </div>
    <div ref="graph" id="energyGraph" class="energy-graph">
      <div class="left-0 legend-container">
        <energy-legend class="legend-margin"/>
      </div>
      <div class="right-0 legend-container">
        <GraphLegend
          v-if="selectedLightCurve"
          class="legend-margin"
          :sensorIds="getSensorIds(selectedLightCurve.curves)"
        />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import * as R from 'ramda';
import { Delaunay } from 'd3-delaunay';
import { scaleLinear, scaleLog } from 'd3-scale';
import type { NumberValue, ScaleLinear, ScaleLogarithmic } from 'd3-scale';
import type { Axis } from 'd3-axis';
import { axisBottom, axisLeft, axisRight } from 'd3-axis';
import type { BrushBehavior } from 'd3-brush';
import { brush } from 'd3-brush';
import { format } from 'd3-format';
import { line, symbol, symbolCircle, symbolCross, symbolDiamond, symbolSquare, symbolTriangle } from 'd3-shape';
import type { SymbolType } from 'd3-shape';
import { select, pointer } from 'd3-selection';
import { transition } from 'd3-transition';
import EnergyLegend from './EnergyLegend.vue';
import GraphLegend from './GraphLegend.vue';
import SaveButton from './SaveButton.vue';
import ToggleLineButton from './ToggleLineButton.vue';
import ToggleScaleTypeButton from './ToggleScaleTypeButton.vue';
import { ACTIONS as MESSAGE_ACTIONS } from '@/store/modules/MessageModule';
import { MUTATIONS as EVENT_MUTATIONS } from '@/store/modules/EventModule';
import { MUTATIONS as POPUP_MUTATIONS } from '@/store/modules/PopupsModule';
import { getSensorColor } from '@/store/Helpers/getSensorColor';
import type { PointSource } from '@/types/PointSource';
import type { SensorColor, SensorPointShape, SensorLine } from '@/store/modules/SettingsModule';
import { PointShape } from '@/store/modules/SettingsModule';
import { getSensorPointShape } from '@/store/Helpers/getSensorPointShape';
import { getSensorLine } from '@/store/Helpers/getSensorLine';
import { formatUTC } from 'starfall-common/helpers/time';
import { logspace } from 'starfall-common/helpers/space';
import type { Curve, Point, Props } from './types';
import type { PointSourceDetails } from '@/types/PointSourceDetails';
import type { EventListItem } from 'starfall-common/Types/EventListItem';
import type { PropType } from 'vue';

const distance = (px: number, py: number, mx: number, my: number): number => {
  const a = px - mx;
  const b = py - my;
  return Math.sqrt(a * a + b * b);
};

const OVERLAY_NONE_ID = -1;
// inverse filter graph
const DEFAULT_OVERLAY_GRAPH_ID = 2;

const TIMELINE_X_TICKER_DATE_FMT = 'HH:mm:ss.SS';
const TIMELINE_X_LABEL_DATE_FMT = 'yyyy-MM-dd (DDD)';

export default {
  name: 'EnergyGraph',
  components: {
    EnergyLegend,
    GraphLegend,
    SaveButton,
    ToggleLineButton,
    ToggleScaleTypeButton
  },
  props: {
    curves:  Object as PropType<Props[]>,
    eventSummary: Object as PropType<EventListItem> | null,
    graphSize: {
      type: Number,
      default: 35,
      required: true
    }
  },
  data() {
    return {
      _x: (() => {}) as ScaleLinear<number, number, never> | (() => void),
      _y: (() => {}) as ScaleLinear<number, number, never> | ScaleLogarithmic<number, number, never> | (() => void),
      x: (() => {}) as ScaleLinear<number, number, never> | (() => void),
      y: (() => {}) as ScaleLinear<number, number, never> | ScaleLogarithmic<number, number, never> | (() => void),
      y2: (() => {}) as  ScaleLinear<number, number, never> | ScaleLogarithmic<number, number, never> | (() => void),
      xMin: 0,
      xMax: 0,
      yMin: 0,
      yMax: 0,
      y2Min: 0,
      y2Max: 0,
      shapes: undefined as any,
      svg: undefined as any,
      xAxis: undefined as  Axis<NumberValue> | undefined,
      yAxis: undefined as Axis<number> | undefined,
      y2Axis: undefined as Axis<number> | undefined,
      brush: undefined as BrushBehavior<unknown> | undefined,
      delaunay: Delaunay.from([]),
      data: [] as PointSource[],
      selected: null as PointSource | null,
      hovered: null as PointSource | null,
      selectedOverlayId: OVERLAY_NONE_ID,
      OVERLAY_NONE_ID,
      zoomOut: true,
      margin: {
        top: 5,
        right: 20,
        left: 170,
        bottom: 45
      },
      idleTimeout: null as ReturnType<typeof setTimeout> | null,
      idleDelay: 350,
      energyLines: true,
      linearScale: true
    }
  },
  mounted(): void {
    this.$store.watch((state) => state.eventModule.event, this.draw);
    this.$store.watch((state) => state.eventModule.selectedPointSource, (ps: PointSourceDetails | null) => {
      if (ps) {
        this.selectPointSource(ps);
      } else {
        this.selectPointSource(null);
      }
    });
  },
  methods: {
    downloadJSON() {
      const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(this.sightings, null, 2));
      const element = document.createElement('a');
      const date = new Date(this.eventSummary?.approx_trigger_time || '');
      const dateStr = formatUTC('y-MM-dd_HH-mm-ss', date);

      element.style.display = 'none';
      element.href = dataStr;
      element.download = `${dateStr}_${this.eventSummary?.event_id || ''}.json`;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    },
    getX(time: number): number { return this.x(time) || 0; },
    getY(intensity: number): number { return this.y(intensity) || 0; },
    draw(): void {
      if (!this.$refs.graph) return;
      if (!this.$store.state.eventModule.event) {
        this.drawAxes();
        return;
      }
      select('#svgEnergyGraph').remove();

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
      this.data = [];
      Object.values(this.sightings).forEach(sighting => {
        this.data.push(...sighting);
        sighting.forEach(ps => {
          this.xMin = Math.min(this.xMin, ps.time);
          this.xMax = Math.max(this.xMax, ps.time);
          this.yMin = Math.min(this.yMin, ps.intensity);
          this.yMax = Math.max(this.yMax, ps.intensity);
        });
      });

      // zoom out graph to fit the complete overlay graph
      if (this.zoomOut) {
        this.selectedLightCurve?.curves
          .forEach(curve => {
            curve.points
              .forEach(point => {
                this.xMin = Math.min(this.xMin, point.x);
                this.xMax = Math.max(this.xMax, point.x);
              });
          });
      }
      if (this.xMin === this.xMax) {
        this.xMin -= 1000;
        this.xMax += 1000;
      }
      if (this.yMin === this.yMax) {
        const offset = this.yMin * 0.1;
        this.yMin -= offset;
        this.yMax += offset;
      }

      this.x = scaleLinear()
        .domain(this.domainPad(this.xMin, this.xMax))
        .range([0, graphWidth]);
      this._x = this.x.copy();

      const yScale = this.linearScale ? scaleLinear : scaleLog;
      this.y = yScale()
        .domain(this.domainPad(this.yMin, this.yMax, this.linearScale))
        .range([graphHeight, 0]);
      this._y = this.y.copy();

      // GRAPH OVERLAY
      if (this.selectedLightCurve) {
        this.y2Min = Number.MAX_VALUE;
        this.y2Max = -Number.MAX_VALUE;
        this.selectedLightCurve.curves
          .forEach(curve => {
            curve.points
              // constrict max/min within time frame of first graph
              .filter(point => point.x < this.xMax && point.x > this.xMin)
              .forEach(point => {
                this.y2Min = Math.min(this.y2Min, point.y);
                this.y2Max = Math.max(this.y2Max, point.y);
              });
          });

        this.y2 = scaleLinear()
          .domain(this.domainPad(this.y2Min, this.y2Max))
          .range([graphHeight, 0]);
      }

      this.delaunay = Delaunay.from(
        this.data,
        (ps: PointSource) => this.getX(ps.time),
        (ps: PointSource) => this.getY(ps.intensity));

      this.xAxis = axisBottom(this.x)
        .ticks(7)
        .tickSizeInner(-graphHeight)
        .tickFormat(((mssue: number) => formatUTC(TIMELINE_X_TICKER_DATE_FMT, new Date(mssue))) as any);

      if (this.linearScale) {
        this.yAxis = axisLeft<number>(this.y)
          .tickSizeInner(-graphWidth)
          .ticks(12 * graphHeight / graphWidth + 1)
          .tickFormat(format('.1e'));

        this.y2Axis = axisRight<number>(this.y2)
          .tickFormat(format('.1e'));
      } else {
        this.yAxis = axisLeft<number>(this.y)
          .tickSizeInner(-graphWidth)
          .tickFormat(format('.1e'));

        this.y2Axis = axisRight<number>(this.y2)
          .tickFormat(format('.1e'));
      }

      this.brush = brush()
        .extent([[0, 0], [graphWidth, graphHeight]])
        .on('end', this.brushEnded);

      // define graph container
      this.svg = select('#energyGraph')
        .append('svg')
        .attr('id', 'svgEnergyGraph')
        .attr('width', graphWidth + this.margin.right + this.margin.left)
        .attr('height', graphHeight + this.margin.top + this.margin.bottom)
        .style('background-color', 'transparent')
        .append('g')
        .attr('transform', `translate(${this.margin.left}, ${this.margin.top})`);

      this.svg
        .append('rect')
        .attr('id', 'energyGraphBackground')
        .attr('fill', '#ffffff')
        .attr('width', graphWidth)
        .attr('height', graphHeight)
        .attr('x', 0)
        .attr('y', 0);

      this.svg
        .append('defs')
        .append('svg:clipPath')
        .attr('id', 'clip-energy')
        .append('svg:rect')
        .attr('width', graphWidth)
        .attr('height', graphHeight)
        .attr('x', 0)
        .attr('y', 0);

      this.shapes = this.svg.append('g')
        .attr('id', 'shapes-energy')
        .attr('clip-path', 'url(#clip-energy)');

      // GRAPH OVERLAY CURVES
      if (this.selectedLightCurve) {
        this.selectedLightCurve.curves.forEach(curve => {
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
                .y((p: Point) => this.y2(p.y))
              );
          }
        });
      }

      // selected point source marker
      const selectedX = this.selected ? this.getX(this.selected.time) : null;
      const selectedY = this.selected ? this.getY(this.selected.intensity) : null;
      const selectedO = this.selected ? 1 : 0;
      this.shapes.append('circle')
        .attr('id', 'dotselect')
        .attr('opacity', selectedO)
        .attr('r', 11)
        .attr('fill', '#f00')
        .attr('cx', selectedX)
        .attr('cy', selectedY);

      this.shapes.append('circle')
        .attr('id', 'hover-dotselect')
        .attr('opacity', selectedO)
        .attr('r', 11)
        .attr('fill', '#f00d')
        .attr('cx', selectedX)
        .attr('cy', selectedY);

      Object.values(this.sightings).forEach(sighting => {
        if (sighting.length === 0) return;
        const color = getSensorColor(sighting[0].sensor_id);
        const shape = getSensorPointShape(sighting[0].sensor_id);
        const lines = getSensorLine(sighting[0].sensor_id);
        const rgb = `rgb(${color.red * 255},${color.green * 255},${color.blue * 255})`;

        if (lines) {
          // create line
          this.shapes.append('path')
            .datum(sighting)
            .attr('id', 'pathPS')
            .attr('fill', 'none')
            .attr('stroke', rgb)
            .attr('stroke-width', 2)
            .style('display', this.energyLines ? 'inherit' : 'none')
            .attr('d', line<PointSource>()
              .x((ps: PointSource) => this.getX(ps.time))
              .y((ps: PointSource) => this.getY(ps.intensity))
            );

          type ShapeFn = (sighting: PointSource[], shape: PointShape, symbolShape: SymbolType, rotation: number, rgb: string) => void;
          type ShapeArgs = [PointSource[], PointShape, SymbolType, number, string];
          type LineFn = (sighting: PointSource[], shape: PointShape, width: number, height: number, rgb: string) => void;
          type LineArgs = [PointSource[], PointShape, number, number, string];
          const createWithRequiredKeys = <T extends Record<PointShape, [ShapeFn, ShapeArgs] | [LineFn, LineArgs] >>(obj: T) => obj;

          // This enforces a handler for each point shape
          const PointShapeMap = createWithRequiredKeys({
            [PointShape.circle]: [this.appendSymbol, [sighting, shape, symbolCircle, 0, rgb]],
            [PointShape.square]: [this.appendSymbol, [sighting, shape, symbolSquare, 0, rgb]],
            [PointShape.diamond]: [this.appendSymbol, [sighting, shape, symbolDiamond, 0, rgb]],
            [PointShape.triangle]: [this.appendSymbol, [sighting, shape, symbolTriangle, 0, rgb]],
            [PointShape.down_triangle]: [this.appendSymbol, [sighting, shape, symbolTriangle, 180, rgb]],
            [PointShape.left_triangle]: [this.appendSymbol, [sighting, shape, symbolTriangle, -90, rgb]],
            [PointShape.right_triangle]: [this.appendSymbol, [sighting, shape, symbolTriangle, 90, rgb]],
            [PointShape.plus]: [this.appendSymbol, [sighting, shape, symbolCross, 0, rgb]],
            [PointShape.times]: [this.appendSymbol, [sighting, shape, symbolCross, 90, rgb]],
            [PointShape.vertical_line]: [this.appendRect, [sighting, shape, 2, 8, rgb]],
            [PointShape.horizontal_line]: [this.appendRect, [sighting, shape, 8, 2, rgb]]
          });

          const [fn, args] = PointShapeMap[shape];
          // @ts-ignore function application too hard for TS
          fn(...args);
        }
      });

      // x-axis
      this.svg.append('g')
        .attr('class', 'x-axis')
        .attr('id', 'axis-energy-x')
        .attr('transform', 'translate(0,' + graphHeight + ')')
        .call(this.xAxis);

      const mssue = this.$store.state.eventModule.selectedEventSummary?.approx_trigger_time || 0;
      const date = new Date(mssue);
      const duration = ((this.xMax - this.xMin) / 1000).toFixed(2);
      this.svg.append('text')
        .style('text-anchor', 'middle')
        .attr('x', graphWidth / 2)
        .attr('y', graphHeight + 35)
        .style('font-size', '10pt')
        .text(`${formatUTC(TIMELINE_X_LABEL_DATE_FMT, date)} ${TIMELINE_X_TICKER_DATE_FMT} [ ${duration} second duration ]`);

      // y-axis
      this.svg.append('g')
        .attr('class', 'y-axis')
        .attr('id', 'axis-energy-y')
        .call(this.yAxis);

      // y-axis
      if (this.selectedLightCurve) {
        this.svg.append('g')
          .attr('class', 'y2-axis')
          .attr('id', 'axis-y2')
          .attr('transform', `translate(${graphWidth},0)`)
          .call(this.y2Axis);
      }

      this.svg.append('text')
        .attr('transform', 'rotate(-90)')
        .style('text-anchor', 'middle')
        .attr('y', -45)
        .attr('x', -graphHeight / 2)
        .style('font-size', '11pt')
        .text('Intensity (kW/sr)');

      if (this.selectedLightCurve) {
        this.svg.append('text')
          .attr('transform', 'rotate(-90)')
          .style('text-anchor', 'middle')
          .attr('y', graphWidth + 60)
          .attr('x', -graphHeight / 2)
          .style('font-size', '11pt')
          .text(this.selectedLightCurve.yLabel);
      }

      this.shapes.append('g')
        .attr('class', 'brush')
        .on('click', this.onClick)
        .on('mousemove', this.onHover)
        .call(this.brush);
    },
    getSensorIds(lightCurves: Curve[]): Set<number> {
      const ids = new Set<number>();
      for (const curve of lightCurves) {
        ids.add(curve.sensorId);
      }
      return ids;
    },
    domainPad(min: number, max: number, linear = true, factor = 0.05) : [number, number] {
      const log = logspace(Math.log10(min), Math.log10(max), 20);
      const logPaddingStart = log[1] - log[0];
      const logPaddingEnd = log[log.length - 1] - log[log.length - 2];
      const linearPadding = Math.abs(max - min) * factor;
      return linear
        ? [min - linearPadding, max + linearPadding]
        : [min - logPaddingStart, max + logPaddingEnd];
    },
    appendSymbol(sighting: PointSource[], shape: PointShape, symbolShape: SymbolType, rotation: number, rgb: string) {
      this.shapes.selectAll('.dot')
        .data(sighting)
        .enter()
        .append('path')
        .attr('id', shape + 'PS')
        .attr('d', symbol().type(symbolShape).size(45))
        .attr('transform', (ps: PointSource) => `rotate(${rotation},${this.getX(ps.time)},${this.getY(ps.intensity)}) translate(${this.getX(ps.time)},${this.getY(ps.intensity)}) `)
        .attr('intensity', (ps: PointSource) => ps.intensity)
        .attr('time', (ps: PointSource) => ps.time)
        .attr('fill', rgb)
        .attr('stroke', '#424949');
    },
    appendRect(sighting: PointSource[], shape: PointShape, width: number, height: number, rgb: string): void {
      this.shapes.selectAll('.dot')
        .data(sighting)
        .enter()
        .append('rect')
        .attr('id', shape + 'PS')
        .attr('x', (ps: PointSource) => this.getX(ps.time) - (width / 2))
        .attr('y', (ps: PointSource) => this.getY(ps.intensity) - (height / 2))
        .attr('width', width)
        .attr('height', height)
        .attr('intensity', (ps: PointSource) => ps.intensity)
        .attr('time', (ps: PointSource) => ps.time)
        .attr('fill', rgb)
        .attr('stroke', '#424949');
    },
    // pixel space -> untransformed pixel space
    untransformX(x: number): number {
      return Math.round(this._x(this.x.invert(x)));
    },
    untransformY(y: number): number {
      return Math.round(this._y(this.y.invert(y)));
    },
    find(mx: number, my: number): PointSource | null {
      const idx = this.delaunay.find(mx, my)
      if (idx == null) return null

      const ps = this.data[idx]
      const px = this.getX(ps.time)
      const py = this.getY(ps.intensity)

      const dist = Math.hypot(px - mx, py - my)
      const RADIUS = 10    // pixels
      return dist < RADIUS ? ps : null
    },
    brushEnded(e: any) {
      const s = e.selection;
      if (!s) {
        if (!this.idleTimeout) {
          this.idleTimeout = setTimeout(this.idled, this.idleDelay);
          return this.idleTimeout;
        }
        this.x.domain(this.domainPad(this.xMin, this.xMax));
        this.y.domain(this.domainPad(this.yMin, this.yMax, this.linearScale));

        if (this.y2 && this.y2.domain) {
          this.y2.domain(this.domainPad(this.y2Min, this.y2Max));
        }
      } else {
        this.x.domain([s[0][0], s[1][0]].map(this.x.invert, this.x));
        this.y.domain([s[1][1], s[0][1]].map(this.y.invert, this.y));
        if (this.y2 && this.y2.invert) {
          this.y2.domain([s[1][1], s[0][1]].map(this.y2.invert, this.y2));
        }
        this.shapes.select('.brush').call(this.brush.move, null);
      }
      this.zoom();
    },
    idled() {
      this.idleTimeout = null;
    },
    zoom() {
      const t = transition().duration(750);
      this.svg.select('#axis-energy-x').transition(t).call(this.xAxis);
      this.svg.select('#axis-energy-y').transition(t).call(this.yAxis);
      if (this.selectedLightCurve) {
        this.svg.select('#axis-y2').transition(t).call(this.y2Axis);

        this.shapes.selectAll('#pathLC').transition(t)
          .attr('d', line<Point>()
            .x((p: Point) => this.x(p.x))
            .y((p: Point) => this.y2(p.y))
          );
      }

      if (this.$store.state.eventModule.event) {
        this.shapes.selectAll('#pathPS').transition(t)
          .attr('d', line<PointSource>()
            .x((ps: PointSource) => this.getX(ps.time))
            .y((ps: PointSource) => this.getY(ps.intensity))
          );

        // TODO: add selection point highlight zoom
        this.shapes.selectAll(
          `#${PointShape.circle}PS,
          #${PointShape.square}PS,
          #${PointShape.diamond}PS,
          #${PointShape.triangle}PS,
          #${PointShape.plus}PS`
        ).transition(t)
          .attr('transform', (ps: PointSource) => `translate(${this.getX(ps.time)},${this.getY(ps.intensity)})`);

        this.shapes.selectAll(`#${PointShape.down_triangle}PS`).transition(t)
          .attr('transform', (ps: PointSource) =>
            `rotate(180,${this.getX(ps.time)},${this.getY(ps.intensity)}) translate(${this.getX(ps.time)},${this.getY(ps.intensity)})`);

        this.shapes.selectAll(`#${PointShape.left_triangle}PS`).transition(t)
          .attr('transform', (ps: PointSource) =>
            `rotate(-90,${this.getX(ps.time)},${this.getY(ps.intensity)}) translate(${this.getX(ps.time)},${this.getY(ps.intensity)})`);

        this.shapes.selectAll(`#${PointShape.right_triangle}PS`).transition(t)
          .attr('transform', (ps: PointSource) =>
            `rotate(90,${this.getX(ps.time)},${this.getY(ps.intensity)}) translate(${this.getX(ps.time)},${this.getY(ps.intensity)})`);

        this.shapes.selectAll(`#${PointShape.times}PS`).transition(t)
          .attr('transform', (ps: PointSource) =>
            `rotate(45,${this.getX(ps.time)},${this.getY(ps.intensity)}) translate(${this.getX(ps.time)},${this.getY(ps.intensity)})`);

        const v_line = this.shapes.selectAll(`#${PointShape.vertical_line}PS`);
        this.shapes.selectAll(`#${PointShape.vertical_line}PS`).transition(t)
          .attr('x', (ps: PointSource) => this.getX(ps.time) - (v_line.attr('width') / 2))
          .attr('y', (ps: PointSource) => this.getY(ps.intensity) - (v_line.attr('height') / 2));

        const h_line = this.shapes.selectAll(`#${PointShape.horizontal_line}PS`);
        this.shapes.selectAll(`#${PointShape.horizontal_line}PS`).transition(t)
          .attr('x', (ps: PointSource) => this.getX(ps.time) - (h_line.attr('width') / 2))
          .attr('y', (ps: PointSource) => this.getY(ps.intensity) - (h_line.attr('height') / 2));

        if (this.selected) {
          this.shapes.selectAll('#dotselect').transition(t)
            .attr('cx', this.getX(this.selected.time))
            .attr('cy', this.getY(this.selected.intensity));
        }
        this.delaunay = Delaunay.from(
          this.data,
          (ps: PointSource) => this.getX(ps.time),
          (ps: PointSource) => this.getY(ps.intensity)
        );
      }
    },
    selectPointSource(pointSource: PointSource | PointSourceDetails | null): void {
      if (!pointSource) {
        select('#dotselect')
          .attr('cx', null)
          .attr('cy', null)
          .attr('opacity', 0);
      } else {
        const time = pointSource.time.toString().includes('.') ? pointSource.time * 1000 : pointSource.time;
        this.svg.select('#dotselect')
          .attr('cx', this.getX(time))
          .attr('cy', this.getY(pointSource.intensity))
          .attr('opacity', 1);
      }
    },
    onClick(event: MouseEvent): void {
      const [mx, my] = pointer(event, this.shapes.node());
      this.selected = this.find(mx, my, this.data);
      this.selectPointSource(this.selected);

      if (this.selected) {
        this.$store.dispatch(MESSAGE_ACTIONS.GET_POINT_SOURCE_DETAILS, this.selected?.point_source_id);
        this.svg.select('#dotselect')
          .attr('cx', this.getX(this.selected.time))
          .attr('cy', this.getY(this.selected.intensity))
          .attr('opacity', 1)
      } else {
        this.$store.commit(EVENT_MUTATIONS.SET_POINT_SOURCE_DETAILS, null);
        this.svg.select('#dotselect').attr('opacity', 0)
      }
    },
    onHover(event: MouseEvent): void {
      const [mx, my] = pointer(event, this.shapes.node());
      this.hovered = this.find(mx, my, this.data);
      
      if (!this.hovered) {
        select('#hover-dotselect')
          .attr('cx', null)
          .attr('cy', null)
          .attr('opacity', 0);
      } else {
        this.svg.select('#hover-dotselect')
          .attr('cx', this.getX(this.hovered.time))
          .attr('cy', this.getY(this.hovered.intensity))
          .attr('opacity', 0.3);
      }
    },
    drawAxes() {
      select('#svgEnergyGraph').remove();

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

      this.xAxis = axisBottom(this.x)
        .tickSizeInner(-graphHeight)
        .ticks(12);
      this.yAxis = axisLeft<number>(this.y)
        .tickSizeInner(-graphWidth)
        .ticks(12 * graphHeight / graphWidth + 1)
        .tickFormat(format('.1e'));

      this.svg = select('#energyGraph')
        .append('svg')
        .attr('id', 'svgEnergyGraph')
        .attr('width', graphWidth + this.margin.right + this.margin.left)
        .attr('height', graphHeight + this.margin.top + this.margin.bottom)
        .style('background-color', 'transparent')
        .append('g')
        .attr('transform', `translate(${this.margin.left}, ${this.margin.top})`);

      this.svg
        .append('rect')
        .attr('id', 'energyGraphBackground')
        .attr('fill', '#ffffff')
        .attr('width', graphWidth)
        .attr('height', graphHeight)
        .attr('x', 0)
        .attr('y', 0);

      // x-axis
      this.svg.append('g')
        .attr('class', 'x-axis')
        .attr('id', 'axis-energy-x')
        .attr('transform', 'translate(0,' + graphHeight + ')')
        .call(this.xAxis);

      this.svg.append('text')
        .style('text-anchor', 'middle')
        .attr('x', graphWidth / 2)
        .attr('y', graphHeight + 30)
        .style('font-size', '10pt')
        .text(`${TIMELINE_X_LABEL_DATE_FMT} ${TIMELINE_X_TICKER_DATE_FMT} [ duration __ seconds ]`);

      // y-axis
      this.svg.append('g')
        .attr('class', 'y-axis')
        .attr('id', 'axis-energy-y')
        .call(this.yAxis);

      this.svg.append('text')
        .attr('transform', 'rotate(-90)')
        .style('text-anchor', 'middle')
        .attr('y', -50)
        .attr('x', -graphHeight / 2)
        .style('font-size', '11pt')
        .text('Intensity (kW/sr)');
    },
    help(): void {
      this.$store.commit(POPUP_MUTATIONS.CREATE_INFO_POPUP, {
        title: 'Plot Help',
        message: `
  click and drag to zoom
  double click to reset zoom
  click a point source to see details
        `
      });
    }
  },
  computed: {
    overlayGraphs() {
      return [{ label: 'None', value: OVERLAY_NONE_ID }].concat(R.map(x => ({ label: x.title, value: x.type }), this.curves));
    },
    selectedLightCurve(): Props | undefined {
      return R.head(R.filter(x => x.type === this.selectedOverlayId, this.curves));
    },
    sensorColors(): SensorColor[] {
      return this.$store.state.settingsModule.sensorColorList;
    },
    sensorPointShapes(): SensorPointShape[] {
      return this.$store.state.settingsModule.sensorPointShapeList;
    },
    sensorLines(): SensorLine[] {
      return this.$store.state.settingsModule.sensorLineList;
    },
    sightings(): { [sightingId: string]: PointSource[]; } {
      if (!this.$store.state.eventModule.event) return {};
      return this.$store.state.eventModule.event.sightings;
    }
  },
  watch: {
    graphSize() {
      setTimeout(this.draw, 1);
    },
    curves(): void {
      const inverseFilter = R.filter(x => x.type === DEFAULT_OVERLAY_GRAPH_ID, this.curves);
      if (inverseFilter.length > 0) {
        this.selectedOverlayId = DEFAULT_OVERLAY_GRAPH_ID;
      }
    },
    selectedLightCurve(newVal: number): void {
      if (newVal === undefined) {
        this.margin.right = 20;
      } else {
        this.margin.right = 180;
      }
      this.draw();
    },
    zoomOut(): void {
      this.draw();
    },
    sensorColors(): void {
      this.draw();
    },
    sightings(): void {
      this.draw();
    },
    sensorPointShapes(): void {
      this.draw();
    },
    sensorLines(): void {
      this.draw();
    },
    selectedOverlayId(): void {
      this.draw();
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/colors.scss';

.mr {
  margin-right: 1em;
}
.label {
  padding: 0 0.5em;
}
.graph-container {
  height: 100%;
  background-color: $white;
  display: flex;
  flex-direction: column;
}
.energy-graph {
  flex-grow: 1;
  display: flex;
  width: 100%;
  color: black;
  background-color: $white;
  overflow: hidden;
  position: relative;
  padding-bottom: 2em;
}
.legend-container {
  position: absolute;
  top: 0;
  height: 100%;
  max-width: 110px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.left-0 {
  left: 0;
}
.right-0 {
  right: 0;
}
.legend-margin {
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
