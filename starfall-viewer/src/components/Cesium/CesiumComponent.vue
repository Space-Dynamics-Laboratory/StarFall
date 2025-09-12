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
  <div id="cesiumContainer"/>
  <EventEnergyLegend/>
  <div id="scaleBox">
    <div ref="scaleBar" class="scalebar"/>
    <p ref="scaleBarText" class="scale-text">Distance Scale</p>
  </div>
  <div id="latLonBox">
    <p class="lat-lon-text" >{{  latLonText }}</p>
  </div>
  <div class="toolbar">
    <button v-if="!detailView" class="btn" @click="flyHome" title="fly home">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
    </button>
    <div v-if="detailView">
      <button class="btn" @click="flyHome" title="fly home">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
      </button>
      <button v-if="unlockedView" class="btn" @click="lockView" title="lock view">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
      </button>
      <button v-if="lockedView" class="btn" @click="unlockView" title="unlock view">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 9.9-1"></path></svg>
      </button>
      <button class="btn" @click="showAllEvents" title="unselect event">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h6"></path><path d="m12 12 4 10 1.7-4.3L22 16Z"></path></svg>
      </button>
    </div>
  </div>
</div>
</template>

<script lang="ts">
import {
  Cartesian2,
  Cartesian3,
  Cartographic,
  EllipsoidGeodesic,
  Math as CesiumMath,
  ScreenSpaceEventHandler,
  ScreenSpaceEventType,
  Viewer,
  PolylineCollection,
  ProviderViewModel,
  TileMapServiceImageryProvider,
  buildModuleUrl,
  UrlTemplateImageryProvider,
  PointPrimitiveCollection
} from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css';
import AllEventDrawHandler from './CesiumDrawingHandlers/AllEventDrawHandler';
import EventEnergyLegend from './EventEnergyLegend.vue';
import cesiumDrawingHandlerFunctions from './CesiumDrawingHandlerFunctions';
import { ACTIONS as GLOBAL_ACTIONS } from '@/store/modules/GlobalModule';
import { ACTIONS as MESSAGE_ACTIONS } from '@/store/modules/MessageModule';
import { ACTIONS as EVENT_ACTIONS, MUTATIONS as EVENT_MUTATIONS, GETTERS as EVENT_GETTERS } from '@/store/modules/EventModule';
import type { EventListItem } from 'starfall-common/Types/EventListItem';
import type { IDrawHandlerArgs, IEntityCollections } from './CesiumDrawingHandlers/IDrawHandlerArgs';
import type { MutationPayload } from 'vuex';
import type { RootState } from '@/types/RootState';
import { ProcessingState as State } from 'starfall-common/Types/ProcessingState';
import { formatUTC } from 'starfall-common/helpers/time';
import type { MotionEvent } from 'cesium';

export default {
  name: 'CesiumComponent',
  components: {
    EventEnergyLegend
  },
  data() {
    return {
      State: State,
      latLonText: '',

      // These are set when the component is mounted
      viewer: undefined as Viewer | undefined,
      collections: undefined as IEntityCollections | undefined,
    }
  },
  computed: {
    eventSummary(): EventListItem | null {
      return this.$store.state.eventModule.selectedEventSummary;
    },
    processingState(): State | null {
      if (this.eventSummary !== null) {
        return this.eventSummary.processing_state;
      }
      return null;
    },
    detailView(): boolean {
      return this.$store.state.eventModule.detailView;
    },
    lockedView(): boolean {
      return this.$store.state.eventModule.lockedView;
    },
    unlockedView(): boolean {
      return !this.$store.state.eventModule.lockedView;
    }
  },
  created(): void {
    this.$store.watch(
      (state: RootState) => state.eventModule.eventList,
      () => {
        const eventList: EventListItem[] = this.$store.getters[EVENT_GETTERS.FULL_EVENT_LIST];
        AllEventDrawHandler[EVENT_MUTATIONS.SHOW_ALL_EVENTS]({
          viewer: this.viewer,
          payload: { events: eventList },
          collections: this.collections
        });
      }
    );
  },
  async mounted(): void {
    const natural = new ProviderViewModel({
      name: 'Natural Earth\u00a0II',
      iconUrl: buildModuleUrl(
        'Widgets/Images/ImageryProviders/naturalEarthII.png'
      ),
      tooltip:
          'Natural Earth II, darkened for contrast.\nhttp://www.naturalearthdata.com/',
      category: 'Cesium ion',
      creationFunction: function() {
        return TileMapServiceImageryProvider.fromUrl(buildModuleUrl('Assets/Textures/NaturalEarthII'));
      }
    });

    const config = await fetch('/api/config')
      .then(res => res.json())
      .then(res => {
        return res
      })
      .catch(console.error);

    let localTiles: ProviderViewModel | undefined = undefined;
    if (config.mapTileServerURL !== '' && config.mapTileSetID !== '' && config.mapTileSetAttribution !== '') {
      localTiles = new ProviderViewModel({
        name: config.mapTileSetName || 'Local Tiles (Raster)',
        iconUrl: buildModuleUrl('Widgets/Images/ImageryProviders/blueMarble.png'),
        tooltip: 'Tiles from local TileServer',
        category: 'Custom',
        creationFunction: function() {
          return new UrlTemplateImageryProvider({
            url: `${config.mapTileServerURL}/data/${config.mapTileSetID}/{z}/{x}/{y}.jpg`,
            maximumLevel: 18,
            credit: config.mapTileSetAttribution
          });
        }
      });
    } else {
      console.info('Local map tile server not specified in config. Defaulting to low resoution tile map.');
    }

    // The default view on the globe
    // Centered around Central America
    // const extent = Rectangle.fromDegrees(-90, 0, -70, 20);
    // Camera.DEFAULT_VIEW_RECTANGLE = extent;
    // Camera.DEFAULT_VIEW_FACTOR = 1;

    const viewer = new Viewer('cesiumContainer', {
      imageryProviderViewModels: localTiles ? [natural, localTiles] : [natural],
      selectedImageryProviderViewModel: localTiles ? localTiles : natural,
      terrainProviderViewModels: [], // we don't need any terrain on the globe
      animation: false,
      fullscreenButton: false,
      baseLayerPicker: true,
      geocoder: false,
      infoBox: false,
      timeline: false,
      navigationHelpButton: false,
      navigationInstructionsInitiallyVisible: false,
      scene3DOnly: false,
      homeButton: false,
      requestRenderMode: false,
      sceneModePicker: true,
      projectionPicker: false,
      maximumRenderTimeChange: Infinity
    });
    this.viewer = viewer;
    this.registerMouseMovement();
    this.registerMouseLeftClick();
    this.registerMouseDoubleLeftClick();
    this.viewer.scene.debugShowFramesPerSecond = process.env.NODE_ENV !== 'production';
    // this.viewer.scene.globe.lightingFadeInDistance = 10000000.0;
    // this.viewer.scene.globe.lightingFadeOutDistance = 1000000.0;
    const START_PITCH = -CesiumMath.PI_OVER_TWO;
    const START_HEADING = 0.0;
    const START_ROLL = 0.0;
    this.viewer.camera.setView({
      // destination: Cartesian3.fromDegrees(START_POSITION[0], START_POSITION[1], START_POSITION[2]),
      orientation: {
        pitch: START_PITCH,
        heading: START_HEADING,
        roll: START_ROLL
      }
    });

    // Zoom listener
    this.viewer.camera.moveEnd.addEventListener(this.updateDistanceScale);

    this.collections = {
      allEventPoints: this.viewer.scene.primitives.add(new PointPrimitiveCollection()),
      pointsourcePolylines: this.viewer.scene.primitives.add(new PolylineCollection())
    };

    this.$store.subscribe((mutation: MutationPayload /*, state: any */): void => {
      cesiumDrawingHandlerFunctions(mutation.type).forEach(handler => {
        handler({
          viewer: this.viewer,
          payload: mutation.payload,
          collections: this.collections
        } as IDrawHandlerArgs);
      });
    });

    cesiumDrawingHandlerFunctions(EVENT_MUTATIONS.INIT).forEach(handler => {
      handler({
        viewer: this.viewer,
        payload: null,
        collections: this.collections
      } as IDrawHandlerArgs);
    });

    this.$store.commit(EVENT_MUTATIONS.STORE_SCENE, this.viewer);
  },
  methods: {
    formatDate(mssue: number): string {
      const date = new Date(mssue);
      if (date) {
        return formatUTC('yyy-MM-dd (DDD) HH:mm:ss', date);
      } else {
        return 'invalid timestamp';
      }
    },
    showAllEvents(): void {
      this.$store.dispatch(EVENT_ACTIONS.SHOW_ALL_EVENTS);
    },
    lockView(): void {
      this.$store.commit(EVENT_MUTATIONS.LOCK_VIEW, this.$store.state.eventModule.selectedEventSummary);
    },
    unlockView(): void {
      this.$store.commit(EVENT_MUTATIONS.UNLOCK_VIEW);
    },
    flyHome(): void {
      this.$store.commit(EVENT_MUTATIONS.FLY_HOME);
    },
    registerMouseMovement(): void {
      const mouseMovementHandler = new ScreenSpaceEventHandler(this.viewer.scene.canvas as HTMLCanvasElement);
      mouseMovementHandler.setInputAction((movement: MotionEvent) => {
        const cartesian = this.viewer.camera.pickEllipsoid(movement.endPosition, this.viewer.scene.globe.ellipsoid);
        if (cartesian) {
          const cartographic = Cartographic.fromCartesian(cartesian);
          const mousePosition = {
            lat: CesiumMath.toDegrees(cartographic.latitude),
            lon: CesiumMath.toDegrees(cartographic.longitude),
            id: ''
          };
          const latStr = mousePosition.lat.toFixed(5);
          const lonStr = mousePosition.lon.toFixed(5);
          this.latLonText = `(${latStr}, ${lonStr})`;
        } else {
          this.latLonText = '( lat, lon )';
        }

        // TODO: fix hover event on globe.
        // scene.pick causes Cesium to crash in Firefox
        // Prevent Firefox from crashing Cesium
        if (navigator.userAgent.toLowerCase().indexOf('firefox') < 0) {
          const pickedObject = this.viewer.scene.pick(movement.endPosition);
          if (!this.$store.state.eventModule.detailView && pickedObject) {
            this.$store.commit(EVENT_MUTATIONS.CLEAR_HOVERED_EVENT, this.$store.state.eventModule.hoveredId);
            this.$store.commit(EVENT_MUTATIONS.SET_HOVERED_EVENT, pickedObject.id);
          }
        }

      }, ScreenSpaceEventType.MOUSE_MOVE);
    },
    registerMouseDoubleLeftClick(): void {
      const mouseDoubleLeftClickHandler = new ScreenSpaceEventHandler(this.viewer.scene.canvas as HTMLCanvasElement);
      mouseDoubleLeftClickHandler.setInputAction(() => {
        // Disable the default dbl click to track entity for the viewer
        // this.viewer.trackedEntity = new Entity();
      }, ScreenSpaceEventType.LEFT_DOUBLE_CLICK);
    },
    registerMouseLeftClick(): void {
      const mouseLeftClickHandler = new ScreenSpaceEventHandler(this.viewer.scene.canvas as HTMLCanvasElement);
      mouseLeftClickHandler.setInputAction((e: { position: Cartesian2 }) => {
        const pickedObject = this.viewer.scene.pick(e.position);
        if (!this.$store.state.eventModule.detailView && pickedObject) {
          this.$store.dispatch(GLOBAL_ACTIONS.SELECT_EVENT, pickedObject.id);
        } else if (pickedObject) {
          this.$store.dispatch(MESSAGE_ACTIONS.GET_POINT_SOURCE_DETAILS, pickedObject.id);
        } else {
          this.$store.commit(EVENT_MUTATIONS.SET_POINT_SOURCE_DETAILS, null);
        }
      }, ScreenSpaceEventType.LEFT_CLICK);
    },
    setMainCamera(location: Cartesian3, heading = 0, pitch = -45, roll = 0): void {
      this.viewer.scene.camera.setView({
        destination: location,
        orientation: {
          heading: CesiumMath.toRadians(heading),
          pitch: CesiumMath.toRadians(pitch),
          roll: CesiumMath.toRadians(roll)
        }
      });
    },
   
    // adapted from https://community.cesium.com/t/distance-scale-indicator/10371/11
    updateDistanceScale() {
      const units_m = ' m';
      const units_km = ' km';
      const geodesic = new EllipsoidGeodesic();
      const distances = [
        1, 2, 3, 5,
        10, 20, 30, 50,
        100, 200, 300, 500,
        1000, 2000, 3000, 5000,
        10000, 20000, 30000, 50000,
        100000, 200000, 300000, 500000];

      // Find the distance between two pixels at center of the screen.
      const width = this.viewer.scene.canvas.clientWidth;
      const height = this.viewer.scene.canvas.clientHeight;

      const left = this.viewer.scene.camera.getPickRay(new Cartesian2((width / 2) | 0, height / 2));
      const right = this.viewer.scene.camera.getPickRay(new Cartesian2(1 + (width / 2) | 0, height / 2));

      const globe = this.viewer.scene.globe;
      const leftPosition = globe.pick(left, this.viewer.scene);
      const rightPosition = globe.pick(right, this.viewer.scene);

      // one of the points is not on the globe
      if (typeof leftPosition === 'undefined' || typeof rightPosition === 'undefined') {
        this.$refs.scaleBarText.innerText = 'Zoom In';
        return;
      }

      const leftCartographic = globe.ellipsoid.cartesianToCartographic(leftPosition);
      const rightCartographic = globe.ellipsoid.cartesianToCartographic(rightPosition);

      geodesic.setEndPoints(leftCartographic, rightCartographic);
      const pixelDistanceM = geodesic.surfaceDistance;
      const pixelDistanceKm = pixelDistanceM / 1000;

      // Find the first distance that makes the scale bar less than 100 pixels.
      const maxBarWidth = 100;
      let distance;
      let label;
      let units;

      for (let i = distances.length - 1; i >= 0; --i) {
        if (distances[i] / pixelDistanceM < maxBarWidth) {
          if (distances[i] > 1000) {
            for (let j = distances.length - 1; j >= 0; --j) {
              if (distances[j] / pixelDistanceKm < maxBarWidth) {
                distance = distances[j];
                units = units_km;
                break;
              }
            }
            break;
          } else {
            distance = distances[i];
            units = units_m;
            break;
          }
        }
      }

      if (typeof distance !== 'undefined') {
        label = distance.toString() + units;

        if (units === units_km) {
          this.$refs.scaleBar.style.width = ((distance / pixelDistanceKm) | 0).toString() + 'px';
        } else {
          this.$refs.scaleBar.style.width = ((distance / pixelDistanceM) | 0).toString() + 'px';
        }

        this.$refs.scaleBarText.innerText = label;
      } else { // too far zoomed in
        this.$refs.scaleBar.style.width = `${maxBarWidth}px`;
        this.$refs.scaleBarText.innerText = `> ${distances[0]}${units_m}`;
      }
    }
  }
}
</script>

<style lang="scss" scoped>
@import "@/assets/scss/colors.scss";
@import "@/assets/scss/side-bar.scss";

#cesiumContainer {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  top: 0;
  margin: 0;
  padding: 0;
  overflow: hidden;
  transition: 200ms;
  &.left-open {
    left: $v-bar-width;
  }
  &.right-open {
    right: $v-bar-width;
  }
  &.bottom-open {
    bottom: $h-bar-height;
  }
}
.cesium-viewer-bottom {
// Attribution is being displayed in the about section
  display: none !important;
}
// override the cesium button styles
.cesium-viewer-toolbar {
  margin-right: 50px;
}
.cesium-button {
  background: $grey !important;
  fill: $white !important;
  color: $white !important;
  border-radius: 0 !important;
}
.cesium-button:hover {
  box-shadow: 0 0 0px $black !important;
  border: 1px solid $purple !important;
}

#scaleBox {
  bottom: 35px;
  right: 10px;
  position: absolute;
  display: inline-block;
  text-align: right;
}

.scale-text {
  width: 100%;
  color: white;
  text-shadow:
    -1px -1px 0 $black,
    1px -1px 0 $black,
    -1px 1px 0 $black,
    1px 1px 0 $black;
  padding: 0;
  margin: 0;
  font-size: 16px;
  font-weight: bold;
}

.scalebar {
  display: inline-block;
  background-color: black;
  border: 1px solid white;
  height: 5px;
  width: 100px;
  padding-left: 5%;
  margin-top: 10px;
  margin-bottom: 10px;
}

#latLonBox {
  bottom: 0px;
  right: 10px;
  position: absolute;
  display: inline-block;
  text-align: right;
}

.lat-lon-text {
  color: white;
  text-shadow:
    -1px -1px 0 $black,
    1px -1px 0 $black,
    -1px 1px 0 $black,
    1px 1px 0 $black;
  margin: 8px;
  font-size: 16px;
  font-weight: bold;
}

.btn {
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  color: #edffff;
  fill: #edffff;
  background-color: #303336;
  border: 1px solid #444;
  border-radius: 4px;
  margin: 0 2px;
  padding: 3px;
}
.btn:hover {
  color: #fff;
  fill: #fff;
  background: #48b;
  border-color: #aef;
  box-shadow: 0 0 8px #fff;
  cursor: pointer;
}

.toolbar {
  position: absolute;
  top: 5px;
  left: 0;
  white-space: nowrap;
}
.toolbar-section {
  display: inline-block;
  background-color: #555;
  border: 1px solid #666;
  border-radius: 2px;
  margin: 0 4px;
  padding: 2px;
}
</style>
