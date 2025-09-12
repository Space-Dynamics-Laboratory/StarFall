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

const SensorSchema = {
  id: '/Sensor',
  description: 'Satellite JSON schema for StarFall',
  type: 'object',
  properties: {
    pos_ecef_m: {
      type: ['array', 'null'],
      items: {
        type: ['number', 'null']
      }
    },
    event_id: {
      type: 'string'
    },
    sighting_id: {
      type: 'string'
    },
    sensor_id: {
      type: 'number'
    },
    platform_id: {
      type: 'number'
    },
    platform_name: {
      type: 'string'
    },
    sensor_name: {
      type: 'string'
    },
    sensor_type: {
      type: 'string'
    },
    fov: {
      type: ['number', 'null']
    },
  },
  required: [
    'pos_ecef_m', 'event_id', 'sighting_id', 'sensor_id',
    'platform_id', 'platform_name', 'sensor_name', 'sensor_type', 'fov'
  ]
};

export default SensorSchema;
