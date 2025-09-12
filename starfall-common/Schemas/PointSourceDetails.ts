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

const PointSourceDetailsSchema = {
  id: '/PointSourceDetails',
  description: 'Point Source Details JSON schema for StarFall',
  type: 'object',
  properties: {
    point_source_id: {
      type: 'string'
    },
    sighting_id: {
      type: 'string'
    },
    platform_name: {
      type: 'string'
    },
    sensor_name: {
      type: 'string'
    },
    time: {
      type: 'number'
    },
    intensity: {
      type: 'number'
    },
    cluster_size: {
      type: ['number', 'null']
    },
    above_horizon: {
      type: 'boolean'
    },
    meas_near_point_ecef_m: {
      type: 'array',
      items: {
        type: 'number'
      }
    },
    meas_far_point_ecef_m: {
      type: 'array',
      items: {
        type: 'number'
      }
    },
    tags: {
      type: 'array',
      items: {
        type: 'string'
      }
    }
  },
  required: [
    'point_source_id', 'sighting_id', 'platform_name', 'sensor_name',
    'time', 'intensity', 'cluster_size', 'above_horizon',
    'meas_near_point_ecef_m', 'meas_far_point_ecef_m', 'tags'
  ]
};

export default PointSourceDetailsSchema;
