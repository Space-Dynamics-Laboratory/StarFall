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

const EventListItemSchema = {
  id: '/EventListItem',
  description: 'Event List Item JSON schema for StarFall',
  type: 'object',
  properties: {
    event_id: {
      type: 'string',
    },
    parent_id: {
      type: ['string', 'null']
    },
    approx_trigger_time: {
      type: 'number'
    },
    created_time: {
      type: 'number',
    },
    last_updated_time: {
      type: 'number'
    },
    processing_state: {
      type: 'number'
    },
    user_viewed: {
      type: 'boolean'
    },
    location_ecef_m: {
      type: ['array', 'null'],
      item: {
        type: 'number'
      }
    },
    location_lat_lon_alt_m: {
      type: ['array', 'null'],
      item: {
        type: 'number'
      }
    },
    velocity_ecef_m_sec: {
      type: ['array', 'null'],
      item: {
        type: 'number'
      }
    },
    approx_energy_j: {
      type: ['number', 'null']
    },
  },
  required: [
    'event_id', 'parent_id', 'approx_trigger_time', 'created_time',
    'last_update_time', 'processing_state', 'user_viewed',
    'location_ecef_m', 'location_ecef_m', 'approx_energy_j', 'velocity_ecef_m_sec'
  ]
};

export default EventListItemSchema;
