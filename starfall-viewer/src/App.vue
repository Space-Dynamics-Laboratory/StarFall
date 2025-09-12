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
    <PopupHandler/>
    <NewVersion v-if="!isLatestVersion" />
    <MenuBar class="menu-height"/>

    <splitpanes class="pane-height" @resized="onLeftPanesResized">
      <pane size="30" min-size="20">
        <splitpanes horizontal>
          <pane size="65" min-size="20" class="overflow-y">
            <EventTable />
          </pane>
          <pane size="35" min-size="20">
            <Tabs class="tabs-1-3" :options="{ useUrlFragment: false }">
              <Tab name="Event Parameters">
                <EventDetails
                  dark
                  :eventSummary="eventSummary"
                  :saveButton="true"
                  class="mr15"
                />
              </Tab>
              <Tab name="Event History">
                <EventHistory
                />
              </Tab>
              <Tab name="Satellites">
                <Satellite
                />
              </Tab>
            </Tabs>
          </pane>
        </splitpanes>
      </pane>
      <pane min-size="40">
        <splitpanes
          horizontal
          @resized="onGraphResized"
        >
          <pane size="65" min-size="20">
            <splitpanes>
              <pane size="80" min-size="20">
                <div class="cesium-container">
                  <CesiumComponent />
                </div>
              </pane>
              <pane size="20" min-size="20">
                <Tabs class="tabs-50-50" ref="rightTabs" :options="{ useUrlFragment: false }">
                  <Tab name="Point Source Filters" id="point-source-filters">
                    <PointSourceFilter
                    />
                  </Tab>
                  <Tab name="Selected Point Source" id="selected-point-source">
                    <SelectedPointSource
                    />
                  </Tab>
                </Tabs>
              </pane>
            </splitpanes>
          </pane>
          <pane size="35" min-size="20">
            <!-- tabs go here -->
            <Tabs
              :options="{ useUrlFragment: false }"
              @changed="drawGraph"
              @clicked="drawGraph"
              ref="graphTabs"
              class="tabs-1-7"
            >
              <Tab name="Event Filters" id="graph-filters">
                <EventFilter />
              </Tab>
              <Tab name="Energy Graph" id="main-graph">
                <EnergyGraph
                  :curves="curves"
                  :graphSize="graphSize"
                  :eventSummary="eventSummary"
                  ref="graph0"
                />
              </Tab>
              <Tab name="Ground Track Graph">
                <GroundTrackGraph
                  ref="graph1"
                  :graphSize="graphSize"
                />
              </Tab>
              <Tab
                v-for="(props, id) in curves"
                :key="id"
                :name="props.title"
              >
                <Graph
                  :curves="props.curves"
                  :yLabel="props.yLabel"
                  :elid="props.elid"
                  :type="props.type"
                  :graphSize="graphSize"
                  ref="graphCurves"
                />
              </Tab>
            </Tabs>
          </pane>
        </splitpanes>
      </pane>
    </splitpanes>
  </div>
</template>

<script lang="ts">
import { Splitpanes, Pane } from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';

import { ACTIONS as GLOBAL_ACTIONS } from '@/store/modules/GlobalModule';
import { ACTIONS as STATUS_ACTIONS } from '@/store/modules/MicroserviceStatusModule';
import { ACTIONS as SETTINGS_ACTIONS } from '@/store/modules/SettingsModule';
import { timestamp } from 'starfall-common/helpers/time';

import PopupHandler from '@/components/Popups/PopupHandler.vue';
import NewVersion from '@/components/Popups/NewVersion.vue';
import MenuBar from '@/components/MenuBar.vue';
import EventTable from '@/components/EventTable.vue';
import CesiumComponent from '@/components/Cesium/CesiumComponent.vue';
import EventFilter from '@/components/EventFilter/EventFilter.vue';
import EventDetails from '@/components/EventDetails.vue';
import { Tabs, Tab } from 'vue3-tabs-component';
import EventHistory from '@/components/EventHistory.vue';
import Satellite from '@/components/Satellite.vue';
import SelectedPointSource from '@/components/SelectedPointSource.vue';
import PointSourceFilter from '@/components/PointSourceFilter.vue';
import EnergyGraph from '@/components/Graphs/EnergyGraph.vue';
import GroundTrackGraph from './components/Graphs/GroundTrackGraph.vue';
import Graph from '@/components/Graphs/Graph.vue';
import type { Point, Props } from '@/components/Graphs/types';
import type { LightCurve } from '@/store/modules/EventModule';
import * as R from 'ramda';
import type { RootState } from '@/types/RootState';
import type { EventDetails as EventDetailsType } from '@/store/modules/EventModule';
import type { PointSourceDetails } from './types/PointSourceDetails';

// TODO: replace custom popup windows with modal library -> https://vue-final-modal.org/

export default {
  components: {
    Splitpanes,
    Pane,
    NewVersion,
    PopupHandler,
    MenuBar,
    EventTable,
    EventDetails,
    EventFilter,
    EventHistory,
    Graph,
    EnergyGraph,
    GroundTrackGraph,
    CesiumComponent,
    Satellite,
    SelectedPointSource,
    PointSourceFilter,
    Tabs,
    Tab,
  },
  beforeCreate() {
    // setup console.debug/log/warn/error redirection
    const log = (logFunc: any, args: any, type: string): void => {
      for (const arg of args) {
        if (typeof arg === 'string') {
          this.$store.dispatch(STATUS_ACTIONS.SAVE_VIEWER_LOG, `${timestamp(new Date())}: (${type}) ${arg}`);
        } else {
          this.$store.dispatch(STATUS_ACTIONS.SAVE_VIEWER_LOG, `${timestamp(new Date())}: (${type}) ${JSON.stringify(arg)}`);
        }
      }
      logFunc.apply(console, args);
    };

    const defaultDebug = console.debug.bind(console);
    console.debug = function(...args: never) {
      log(defaultDebug, args, 'debug');
    };

    // console.log is expected to only be used for debugging
    // Since the log capturing runs JSON.stringify, it will crash on cyclic/self-referential objects
    // const defaultLog = console.log.bind(console);
    // console.log = function(...args: never) {
    //   log(defaultLog, args, 'info');
    // };

    const defaultInfo = console.info.bind(console);
    console.info = function(...args: never) {
      log(defaultInfo, args, 'info');
    };

    const defaultWarn = console.warn.bind(console);
    console.warn = function(...args: never) {
      log(defaultWarn, args, 'warning');
    };

    const defaultError = console.error.bind(console);
    console.error = function(...args: never) {
      log(defaultError, args, 'error');
    };

    this.$store.dispatch(GLOBAL_ACTIONS.INIT);

    fetch('/api/config')
      .then(res => res.json())
      .then(res => {
        this.$store.dispatch(SETTINGS_ACTIONS.SET_ENERGY_THRESHOLD, Number.parseFloat(res.energyThreshold));
      })
      .catch(console.error);
  },
  mounted() {
    this.$store.watch(
      (state: RootState) => state.eventModule.event,
      (event: EventDetailsType) => {
        if (event) {
          this.$refs.graphTabs.selectTab('#main-graph');
        } else {
          this.$refs.graphTabs.selectTab('#graph-filters');
        }
      }
    );
    this.$store.watch(
      (state: RootState) => state.eventModule.selectedPointSource,
      (event: PointSourceDetails) => {
        if (event) {
          this.$refs.rightTabs.selectTab('#selected-point-source');
        } else {
          this.$refs.rightTabs.selectTab('#point-source-filters');
        }
      }
    );
    
    window.addEventListener('resize', event => {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = setTimeout(() => this.onWindowResized(event), 100);
    }, true);

  },
  data() {
    return {
      GLayoutRoot: null as null | HTMLElement,
      graphSize: 0, // this value is used to trigger draw redraw on resize
      debounceTimer: 0,
    }
  },
  methods: {
    onWindowResized(event) {
      this.graphSize = event.timeStamp;
    },
    drawGraph(tabObj: any) {
      // TODO: This is hacky but it works
      // for some reason just calling draw makes a blank graph
      const TIMEOUT = 1;
      const tabIndex = tabObj.tab.index
      if (tabIndex === 1) {
        setTimeout(this.$refs.graph0.draw, TIMEOUT)
      } else if (tabIndex === 2) {
        setTimeout(this.$refs.graph1.draw, TIMEOUT)
      } else if (tabIndex >= 3 && this.$refs.graphCurves?.length > 0) {
        // refs assigned in a loop are in a refs array
        setTimeout(this.$refs.graphCurves[tabIndex - 3].draw, TIMEOUT)
      }
    },
    // The graphs watch this.graphSize to only trigger a redraw
    onGraphResized(panes) {
      this.graphSize = panes[1].size;
    },
    onLeftPanesResized(panes) {
      this.graphSize += 1
    }
  },
  computed: {
    isLatestVersion() {
      return this.$store.state.microserviceStatusModule.latestVersion;
    },
    eventSummary() {
      return this.$store.state.eventModule.selectedEventSummary;
    },
    event() {
      return this.$store.state.eventModule.event;
    },
    curves(): Props[] {
      const props: Props[] = [];
      if (!this.$store.state.eventModule.event) {
        return props;
      }
      for (const type in this.$store.state.eventModule.event.lightCurves) {
        const lightCurve: LightCurve[] = this.$store.state.eventModule.event.lightCurves[type];
        props[parseInt(type)] = {
          curves: [],
          yLabel: '',
          elid: 'graph_' + type,
          title: '',
          type: parseInt(type)
        };
        lightCurve.forEach(curve => {
          const epochReferenceTime = new Date(curve.triggerTimestamp).getTime();
          props[parseInt(type)].yLabel = curve.y_label;
          props[parseInt(type)].title = curve.title;
          props[parseInt(type)].curves.push({
            points: R.zipWith(
              (x, y) => ({ x, y }),
              R.map(x => Math.floor(x / 1000) + epochReferenceTime, curve.x),
              curve.y
            ) as Point[],
            sensorId: curve.sensor_id
          });
        });
      }
      return props;
    }
  }
}
</script>


<style lang="scss">
// All the styles here are global styles for the application
// Only import class and style definitions once
@import "@/assets/scss/color-classes.scss";
@import "@/assets/scss/scrollbar.scss";
@import "@/assets/scss/base.scss";
@import "@/assets/scss/button.scss";
@import '@/assets/scss/input.scss';
@import '@/assets/scss/popup.scss';
@import '@/assets/scss/dropdown.scss';
// The color sass variables
@import "./assets/scss/colors.scss";
@import "./assets/scss/variables.scss";

body.waiting * {
  cursor: wait;
}
html {
  background: #222;
  height: 100vh;
}
body {
  padding: 0;
  margin: 0;
  font-family: 'Arial', sans-serif;
  scrollbar-width: thin;
  scrollbar-color: $off-white $grey;
}
::-webkit-scrollbar {
  width: 10px;
}
::-webkit-scrollbar-track {
  background: $grey;
  border-radius: 5px;
}
::-webkit-scrollbar-thumb {
  background: $off-white;
  border-radius: 5px;
}
::-webkit-scrollbar-thumb:hover {
  background: $accent;
}
// Add this class to any text you don't want to be able to highlight
.no-select {
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -khtml-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

// // MAIN WINDOW
.menu-height {
  height: $menu-height;
}
.pane-height {
  height: 100vh - $menu-height;
}
.container {
  background: $gl-grey;
}
.full-screen {
  width: 100%;
  // TODO: fix this
  height: 93vh;
}
.layout-height {
  height: 95vh;
}
.menu-height {
  height: $menu-height;
}
// .white {
//   background-color: #f1f1f1;
//   color: black;
// }

// SPLITPANE LAYOUT
$splitter-color: black;
$splitter-hightlight-color: #444;
$splitter-width: 8px;
$splitter-highlight: calc($splitter-width / 4);
$splitter-highlight-padding: calc(($splitter-width * 3) / 8); 

// .splitpanes__pane > * {
//   width: 100%;
//   height: 100%;
// }
.splitpanes {
  background: #222;
}
.overflow-y {
  overflow-y: auto;
}

// tab overflow content
.splitpanes__pane {
  position: relative;
}
.tabs-component {
  position: absolute;
  top: 0;
  bottom: 0;
  right: 0;
  left: 0;
}
.tabs-component-panel {
  position: absolute;
  top: 20px;
  bottom: 0;
  right: 0;
  left: 0;
  overflow: auto;
}

.splitpanes--vertical > .splitpanes__splitter,
.splitpanes--horizontal > .splitpanes__splitter {
  background: $splitter-color;
}
.splitpanes--vertical > .splitpanes__splitter {
  min-width: $splitter-width;
  position: relative;
}
.splitpanes--vertical > .splitpanes__splitter:hover::after {
  content: '';
  width: $splitter-highlight;
  background: $splitter-hightlight-color;
  position: absolute;
  top: 0;
  bottom: 0;
  right: $splitter-highlight-padding; 
  left: $splitter-highlight-padding;
}
.splitpanes--horizontal > .splitpanes__splitter {
  min-height: $splitter-width;
  position: relative;
}
.splitpanes--horizontal > .splitpanes__splitter:hover::after {
  content: '';
  height: $splitter-highlight;
  background: $splitter-hightlight-color;
  position: absolute;
  top: $splitter-highlight-padding; 
  bottom: $splitter-highlight-padding;
  right: 0;
  left: 0;
}

// CESIUM 
.cesium-container {
  position: relative;
  height: 100%;
  width: 100%;
}
.cesium-baseLayerPicker-dropDown {
  z-index: 1;
}

// TAB STYLES
.tabs-component {
  background: black;
}
.tabs-component-tabs {
  display: flex;
  padding: 0;
  margin: 0;
}
.tabs-50-50 .tabs-component-tab {
  width: 50%;
}
.tabs-1-7 .tabs-component-tab {
  width: 14%;
}
.tabs-1-3 .tabs-component-tab {
  width: 33%;
}
.tabs-component-tab {
  padding: 0;
  margin: 0;
  list-style: none;
  font-size: 12px;
  background: #111;
  margin-right: 2px;
  margin-top: 2px;
}
.tabs-component-tab:last-child {
  margin-right: 0;
}
.tabs-component-tab a {
  user-select:none;
  text-decoration: none;
  color: #999;
  display: block;
  padding: 2px 0 0 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tabs-component-tab:hover {
  background: #222;
}
// .tabs-component-tab.is-disabled {

// }
.tabs-component-tab.is-active {
  background: #222;
  padding-bottom: 2px;
}
.tabs-component-tab.is-active a {
  color: #ddd;
}
.tabs-component-tab.is-inactive {
  margin-bottom: 2px;
}
.tabs-component-panels {
  // padding-top: 4px;
  color: white;
  background: #222;
  height: 100%;
}
// .tabs-component-panel {

// }
</style>
