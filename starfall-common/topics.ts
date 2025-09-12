/*************************************************************************************************
* Licensed to the Apache Software Foundation (ASF) under one
* or more contributor license agreements.  See the NOTICE file
* distributed with this work for additional information
* regarding copyright ownership.  The ASF licenses this file
* to you under the Apache License, Version 2.0 (the
* "License"); you may not use this file except in compliance
* with the License.  You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing,
* software distributed under the License is distributed on an
* "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
* KIND, either express or implied.  See the License for the
* specific language governing permissions and limitations
* under the License.
**************************************************************************************************/

enum topics {
  ProcessingStateChanged = 'processing_state_changed',
  NewEventInsert = 'new_event_insert',
  NewHistoryInsert = 'new_history_insert',
  NewEventStart = 'NEW_EVENT_START',
  NewEventFinish = 'NEW_EVENT_FINISH',
  GetEventList = 'GetEventList',
  EventList = 'EventList',
  GetEventDetails = 'GetEventDetails',
  EventDetails = 'EventDetails',
  GetPointSourceDetails = 'GetPointSourceDetails',
  PointSourceDetails = 'PointSourceDetails',
  GetEventHistory = 'GetEventHistory',
  EventHistory = 'EventHistory',
  PutEventHistoryNote = 'PutEventHistoryNote',
  ChangeEventProcessingState = 'ChangeEventProcessingState',
  AddUpdateEventSummary = 'AddUpdateEventSummary',
  GetSensorsForEvent = 'GetSensorsForEvent',
  SensorsForEvent = 'SatellitesForEvent',
  ToggleEventUserViewed = 'ToggleEventUserViewed',
  DeleteEvent = 'DeleteEvent',
  DuplicateEvent = 'DuplicateEvent',
  DeleteVelocity = 'DeleteVelocity',
  SaveViewerLog = 'SaveViewerLog',
  GetAllPlatforms = 'GetAllPlatforms',
  AllPlatforms = 'GetAllPlatforms',
  GetPointSourceFilterExtents = 'GetPointSourceFilterExtents',
  PointSourceFilterExtents = 'PointSourceFilterExtents',
  ChangePointSourceFilter = 'ChangePointSourceFilter',
  UpdateSightings = 'UpdateSightings',
  Toast = 'Toast',
  UpdateStatus = 'UpdateStatus',
  UpdatePlatformsInDatabase = 'UpdatePlatformsInDatabase',
  Heartbeat = 'Heartbeat',
  Reestimate = 'reestimate',
  TimeTrigger = 'trigger.1'
};

export default topics;
