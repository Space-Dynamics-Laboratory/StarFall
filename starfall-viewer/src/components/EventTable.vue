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
  <ContextMenu ref="eventTableContextMenu">
    <div class="menu">
      <ul>
        <li @click="onMarkViewedUnviewed(contextId)">Mark as {{ contextViewed ? 'unviewed' : 'viewed' }}</li>
        <li @click="onDelete(contextId)">Delete</li>
        <!-- <li @click="onReestimate(contextId)">Reestimate</li> -->
      </ul>
    </div>
  </ContextMenu>
  <div class="table-container">
    <table class="event-table no-select">
      <thead>
        <tr>
          <th
            @click="orderBy = orderBy === PageSort.DATE_DESC ? PageSort.DATE_ASC : PageSort.DATE_DESC"
          >
            Date (DOY) Time
            <fa-icon v-if="orderBy === PageSort.DATE_DESC" icon="sort-down"/>
            <fa-icon v-if="orderBy === PageSort.DATE_ASC" icon="sort-up"/>
          </th>
          <th
            @click="orderBy = orderBy === PageSort.STATE_DESC ? PageSort.STATE_ASC : PageSort.STATE_DESC"
          >
            State
            <fa-icon v-if="orderBy === PageSort.STATE_DESC" icon="sort-down"/>
            <fa-icon v-if="orderBy === PageSort.STATE_ASC" icon="sort-up"/>
          </th>
          <th
            @click="orderBy = orderBy === PageSort.ENERGY_DESC ? PageSort.ENERGY_ASC : PageSort.ENERGY_DESC"
          >
            Energy (J)
            <fa-icon v-if="orderBy === PageSort.ENERGY_DESC" icon="sort-down"/>
            <fa-icon v-if="orderBy === PageSort.ENERGY_ASC" icon="sort-up"/>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="event in events"
          :key="event.event_id"
          :class="getRowClasses(event)"
          @click="onClick(event.event_id)"
          @contextmenu.prevent="onContextMenu($event, event.event_id)"
          @mouseenter="onMouseEnter(event.event_id)"
          @mouseleave="onMouseLeave"
          :ref="event.event_id"
        >
          <td>{{ formatDate(event.approx_trigger_time) }}</td>
          <td>{{ stateStr[event.processing_state] }}</td>
          <td>{{ event.approx_energy_j !== null ? event.approx_energy_j.toExponential(1) : '---' }}</td>
        </tr>
      </tbody>
    </table>
    <div class="page-select-container">
      <button class="btn left round" @click="fetchFirstPage"><fa-icon icon="caret-left"/><fa-icon icon="caret-left"/></button>
      <button class="btn border-x border-right" @click="fetchPrevPage"><fa-icon icon="caret-left"/></button>
      <label class="sr-only" for="page">page number</label>
      <input class="border-x page-input" type="number" name="page" step="1" min="1" :max="lastPage + 1" onfocus="this.select()" onmouseup="return false" v-model="pageDisplay" pattern="\d*">
      <p class="align-center border-x last-page">/ {{ lastPage + 1 }}</p>
      <button class="btn border-x border-left" @click="fetchNextPage"><fa-icon icon="caret-right"/></button>
      <button class="btn right round" @click="fetchLastPage"><fa-icon icon="caret-right"/><fa-icon icon="caret-right"/></button>
      <button class="btn left right round" @click="refreshPage">
        <svg class="mr" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2v6h-6"></path><path d="M21 13a9 9 0 1 1-3-7.7L21 8"></path></svg>
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { ACTIONS as GLOBAL_ACTIONS } from '@/store/modules/GlobalModule';
import { ACTIONS as MESSAGE_ACTIONS } from '@/store/modules/MessageModule';
import type { ContextMenuData } from '@/types/ContextMenuData';
import type { EventListItem } from 'starfall-common/Types/EventListItem';
import { MUTATIONS as EVENT_MUTATIONS, GETTERS as EVENT_GETTERS } from '@/store/modules/EventModule';
import { MUTATIONS as POPUP_MUTATIONS } from '@/store/modules/PopupsModule';
import { ProcessingState as State, stateStr } from 'starfall-common/Types/ProcessingState';
import type { StateStrMap } from 'starfall-common/Types/ProcessingState';
import { formatUTC } from 'starfall-common/helpers/time';
import { PageSort } from 'starfall-common/Types/Paging';
import type { Page } from 'starfall-common/Types/Paging';
import type { RootState } from '@/types/RootState';
import { defaultFilter, type EventFilter } from 'starfall-common/Types/EventFilter';
import { reestimatePopup } from '@/helpers/reestimatePopup';
import ContextMenu from '@/components/ContextMenu.vue';


export default {
  name: 'EventTable',
  components: {
    ContextMenu
  },
  data() {
    return {
      page: 0,
      orderBy: PageSort.DATE_DESC,
      PageSort: PageSort,
      eventFilter: defaultFilter,
      precision: 2,
      contextId: undefined,
      contextViewed: undefined
    }
  },
  mounted(): void {
    this.$store.dispatch(MESSAGE_ACTIONS.GET_EVENT_LIST, { pageNumber: this.page, pageSize: this.pageSize, orderBy: this.orderBy, eventFilter: this.eventFilter } as Page);

    this.$store.watch(
      (state: RootState) => state.eventModule.eventFilter,
      (eventFilter: EventFilter) => {
          this.page = 0;
          this.eventFilter = eventFilter;
          this.$store.dispatch(MESSAGE_ACTIONS.GET_EVENT_LIST, { pageNumber: this.page, pageSize: this.pageSize, orderBy: this.orderBy, eventFilter: this.eventFilter } as Page);
      }
    );
  },
  watch: {
    pageSize(pageSize: number): void {
      this.$store.dispatch(MESSAGE_ACTIONS.GET_EVENT_LIST, { pageNumber: this.page, pageSize: pageSize, orderBy: this.orderBy, eventFilter: this.eventFilter } as Page);
    },
    page(page: number): void {
      this.$store.dispatch(MESSAGE_ACTIONS.GET_EVENT_LIST, { pageNumber: page, pageSize: this.pageSize, orderBy: this.orderBy, eventFilter: this.eventFilter } as Page);
    },
    orderBy(sort: PageSort): void {
      this.page = 0;
      this.$store.dispatch(MESSAGE_ACTIONS.GET_EVENT_LIST, { pageNumber: this.page, pageSize: this.pageSize, orderBy: sort, eventFilter: this.eventFilter } as Page);
    }
  },
  computed: {
  /* pagination */
    pageSize(): number {
      return this.$store.state.settingsModule.nEventsPerPage;
    },
    lastPage(): number {
      const totalCount = this.$store.getters[EVENT_GETTERS.FULL_EVENT_LIST].filteredCount;
      const last = Math.ceil(totalCount / this.pageSize) - 1;
      return Math.max(last, 0);
    },
    pageDisplay: {
      get() {
        return `${this.page + 1}`;
      },
      set(page: string) {
        const newPage = parseInt(page) - 1;
        if (newPage > 0 && newPage <= this.lastPage) {
          this.page = newPage;
        } else if (newPage < 0) {
          this.page = 0;
        } else {
          this.page = this.lastPage;
        }
      }
    },
    events(): EventListItem[] {
      return this.$store.getters[EVENT_GETTERS.FULL_EVENT_LIST].data;
    },
    /* row selection */
    hovered(): string {
      return this.$store.state.eventModule.hoveredId;
    },
    selected(): string | undefined {
      return this.$store.state.eventModule.selectedEventSummary?.event_id;
    },
    stateStr(): StateStrMap {
      return stateStr;
    }
  },
  methods: {
    // TODO: simplify classes
    getRowClasses(event: EventListItem): unknown {
      if (event.event_id === this.selected) {
        return {
          'new-selected': event.processing_state === State.New,
          'waiting-selected': event.processing_state === State.Waiting,
          'processing-selected': event.processing_state === State.Processing,
          'failed-selected': event.processing_state === State.Failed,
          'parameter-estimation-selected': event.processing_state === State.ParameterEstimation,
          'user-analysis-selected': event.processing_state === State.UserAnalysis,
          'accepted-selected': event.processing_state === State.Accepted,
          'deferred-selected': event.processing_state === State.Deferred,
          'rejected-selected': event.processing_state === State.Rejected,
          'no-solution-selected': event.processing_state === State.NoSolution,
          'no-data-selected': event.processing_state === State.NoData,
          unviewed: !event.user_viewed
        };
      }

      if (event.event_id === this.hovered) {
        return {
          'new-hovered': event.processing_state === State.New,
          'waiting-hovered': event.processing_state === State.Waiting,
          'processing-hovered': event.processing_state === State.Processing,
          'failed-hovered': event.processing_state === State.Failed,
          'parameter-estimation-hovered': event.processing_state === State.ParameterEstimation,
          'user-analysis-hovered': event.processing_state === State.UserAnalysis,
          'accepted-hovered': event.processing_state === State.Accepted,
          'deferred-hovered': event.processing_state === State.Deferred,
          'rejected-hovered': event.processing_state === State.Rejected,
          'no-solution-hovered': event.processing_state === State.NoSolution,
          'no-data-hovered': event.processing_state === State.NoData,
          unviewed: !event.user_viewed
        };
      }

      return {
        new: event.processing_state === State.New,
        waiting: event.processing_state === State.Waiting,
        processing: event.processing_state === State.Processing,
        failed: event.processing_state === State.Failed,
        'parameter-estimation': event.processing_state === State.ParameterEstimation,
        'user-analysis': event.processing_state === State.UserAnalysis,
        accepted: event.processing_state === State.Accepted,
        deferred: event.processing_state === State.Deferred,
        rejected: event.processing_state === State.Rejected,
        'no-solution': event.processing_state === State.NoSolution,
        'no-data': event.processing_state === State.NoData,
        unviewed: !event.user_viewed
      };
    },
    onMouseEnter(id: string): void {
      this.$store.commit(EVENT_MUTATIONS.CLEAR_HOVERED_EVENT, this.hovered);
      this.$store.commit(EVENT_MUTATIONS.SET_HOVERED_EVENT, id);
    },
    onMouseLeave(): void {
      this.$store.commit(EVENT_MUTATIONS.CLEAR_HOVERED_EVENT, this.hovered);
    },
    onClick(id: string): void {
      this.$store.dispatch(GLOBAL_ACTIONS.SELECT_EVENT, id);
    },
    /* context menu */
    onContextMenu(event: MouseEvent, id: string): void {
      const menu = this.$refs.eventTableContextMenu;
      menu.open(event);

      this.contextId = id;
      this.contextViewed = this.$store.getters[EVENT_GETTERS.SINGLE_EVENT_BY_ID](id).user_viewed;
    },
    onMarkViewedUnviewed(id: string) {
      this.$store.dispatch(MESSAGE_ACTIONS.TOGGLE_EVENT_USER_VIEWED, id);
    },
    onDuplicate(id: string) {
      this.$store.dispatch(MESSAGE_ACTIONS.DUPLICATE_EVENT, id);
    },
    onReestimate(id: string) {
      const event = this.$store.getters[EVENT_GETTERS.SINGLE_EVENT_BY_ID](id);
      if (event) {
        reestimatePopup(this.$store, event.approx_trigger_time, event?.event_id);
      }
    },
    onDelete(id: string) {
      const event = this.$store.getters[EVENT_GETTERS.SINGLE_EVENT_BY_ID](id);
      this.$store.commit(POPUP_MUTATIONS.CREATE_CONFIRMATION_POPUP, {
        title: 'Delete Event',
        message: `Do you want to permanently delete this event on ${this.formatDate(event.approx_trigger_time)}?`,
        confirmButtonText: 'Delete',
        onConfirm: () => { this.$store.dispatch(MESSAGE_ACTIONS.DELETE_EVENT, id); }
      });
    },
    onCompress(id: string) {
      console.debug('compress', id);
    },
    fetchFirstPage(): void {
      if (this.page !== 0) {
        this.page = 0;
      }
    },
    fetchNextPage(): void {
      if (this.page < this.lastPage) {
        this.page += 1;
      }
    },
    fetchPrevPage(): void {
      if (this.page > 0) {
        this.page -= 1;
      }
    },
    fetchLastPage(): void {
      if (this.page !== this.lastPage) {
        this.page = this.lastPage;
      }
    },
    refreshPage(): void {
      this.$store.dispatch(MESSAGE_ACTIONS.GET_EVENT_LIST, { pageNumber: this.page, pageSize: this.pageSize, orderBy: this.orderBy, eventFilter: this.eventFilter } as Page);
    },
    formatDate(mssue: number): string {
      const date = new Date(mssue);
      if (date) {
        return formatUTC('yyy-MM-dd (DDD) HH:mm:ss', date);
      } else {
        return 'invalid timestamp';
      }
    }
  }
}
</script>

<style lang="scss" scoped>
@use 'sass:color';
@import '@/assets/scss/colors.scss';

$perc: 25%;
$perc-hov: 10%;
$perc-sel: 10%;

.table-container {
  position: relative;
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: #ccc;
}
.event-table {
  cursor: pointer;
  background-color: $white;
  width: 100%;
  margin: 0;
  padding: 0;
  overflow-y: auto;
  border-collapse: collapse;
  position: relative;
}
.event-table, tr, td {
  border: none;
}
td, th {
  padding: 4px;
}
td {
  border-right: 1px solid #3331;
}
th {
  padding-right: 1px;
}
th:last-child {
  padding-right: 0;
}
td:last-child {
  border-right: none;
}
tr, p {
  font: 13px "Consolas", monospace;
  text-align: left;
}
.event-table th {
  position: sticky;
  background-color: $white;
  top: 0;
}

.new                           { background: color.adjust($new,                  $lightness: $perc); }
.waiting                       { background: color.adjust($waiting,              $lightness: $perc); }
.processing                    { background: color.adjust($processing,           $lightness: $perc); }
.failed                        { background: color.adjust($failed,               $lightness: $perc); }
.parameter-estimation          { background: color.adjust($parameter-estimation, $lightness: $perc); }
.user-analysis                 { background: color.adjust($user-analysis,        $lightness: $perc); }
.accepted                      { background: color.adjust($accepted,             $lightness: $perc); }
.deferred                      { background: color.adjust($deferred,             $lightness: $perc); }
.rejected                      { background: color.adjust($rejected,             $lightness: $perc); }
.no-solution                   { background: color.adjust($no-solution,          $lightness: $perc); }
.no-data                       { background: color.adjust($no-data,              $lightness: $perc); }

.new-hovered                   { background: color.adjust($new,                  $lightness: $perc-hov); }
.waiting-hovered               { background: color.adjust($waiting,              $lightness: $perc-hov); }
.processing-hovered            { background: color.adjust($processing,           $lightness: $perc-hov); }
.failed-hovered                { background: color.adjust($failed,               $lightness: $perc-hov); }
.parameter-estimation-hovered  { background: color.adjust($parameter-estimation, $lightness: $perc-hov); }
.user-analysis-hovered         { background: color.adjust($user-analysis,        $lightness: $perc-hov); }
.accepted-hovered              { background: color.adjust($accepted,             $lightness: $perc-hov); }
.deferred-hovered              { background: color.adjust($deferred,             $lightness: $perc-hov); }
.rejected-hovered              { background: color.adjust($rejected,             $lightness: $perc-hov); }
.no-solution-hovered           { background: color.adjust($no-solution,          $lightness: $perc-hov); }
.no-data-hovered               { background: color.adjust($no-data,              $lightness: $perc-hov); }

.new-selected                  { background: color.adjust($new,                  $lightness: $perc-sel); border-top: black solid 2px; border-bottom: black solid 2px; }
.waiting-selected              { background: color.adjust($waiting,              $lightness: $perc-sel); border-top: black solid 2px; border-bottom: black solid 2px; }
.processing-selected           { background: color.adjust($processing,           $lightness: $perc-sel); border-top: black solid 2px; border-bottom: black solid 2px; }
.failed-selected               { background: color.adjust($failed,               $lightness: $perc-sel); border-top: black solid 2px; border-bottom: black solid 2px; }
.parameter-estimation-selected { background: color.adjust($parameter-estimation, $lightness: $perc-sel); border-top: black solid 2px; border-bottom: black solid 2px; }
.user-analysis-selected        { background: color.adjust($user-analysis,        $lightness: $perc-sel); border-top: black solid 2px; border-bottom: black solid 2px; }
.accepted-selected             { background: color.adjust($accepted,             $lightness: $perc-sel); border-top: black solid 2px; border-bottom: black solid 2px; }
.deferred-selected             { background: color.adjust($deferred,             $lightness: $perc-sel); border-top: black solid 2px; border-bottom: black solid 2px; }
.rejected-selected             { background: color.adjust($rejected,             $lightness: $perc-sel); border-top: black solid 2px; border-bottom: black solid 2px; }
.no-solution-selected          { background: color.adjust($no-solution,          $lightness: $perc-sel); border-top: black solid 2px; border-bottom: black solid 2px; }
.no-data-selected              { background: color.adjust($no-data,              $lightness: $perc-sel); border-top: black solid 2px; border-bottom: black solid 2px; }

.unviewed { font-weight: bold; }

fa-icon {
  right: 1px;
  display: inline;
  margin-right: 1px;
}

.page-select-container {
  display: flex;
  justify-content: center;
  background: $white;
  padding: 2px 0;
  margin: 0;
  border-bottom: 1px solid color.adjust($light-grey, $lightness: 20%);
  height: 1.1em;
  position: sticky;
  bottom: 0;
  z-index: 9;
  width: 100%;
}
.btn {
  display: flex;
  align-items: center;
}
.align-center {
  display: flex;
  align-items: center;
}
.btn.round {
  border: 1px solid $light-grey;
}
.btn.right.round {
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
}
.btn.left.round {
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
}
.border-x {
  border-top: 1px solid $light-grey;
  border-bottom: 1px solid $light-grey;
  border-right: none;
  border-left: none;
}
.border-right {
  border-right: 1px solid $light-grey;
}
.border-left {
  border-left: 1px solid $light-grey;
}
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0,0,0,0);
  border: 0;
}

/* Chrome, Safari, Edge, Opera */
.page-input::-webkit-outer-spin-button,
.page-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Firefox */
.page-input[type=number] {
  -moz-appearance: textfield;
}
.page-input {
  text-align: center;
  width: 3em;
}
.last-page {
  margin: 0;
  padding: 1px;
  padding-right: 6px;
}
.page-input, .last-page {
  font-family: monospace;
  font-size: 14px;
}
.menu {
  padding: 0;
  background-color: white;
  border: 1px solid rgb(211, 211, 211);
}
.menu ul {
  list-style: none;
  margin: 0;
  padding: 0;
}
.menu li {
  padding: 2px 6px;
  font-size: 14px;
}
.menu li:hover {
  background-color: #EEE;
  cursor: pointer;
}
</style>
