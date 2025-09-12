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

import { formatUTC } from 'starfall-common/helpers/time';

const formatDate = (ssue: number): string => formatUTC('y-MM-dd HH:mm:ss.SSS', new Date(ssue * 1000));

export default {
  time: {
    label: 'Time',
    format: formatDate
  },
  intensity: {
    label: 'Intensity (J)',
    format: (i: number): string => i.toExponential(1)
  },
  cluster_size: {
    label: 'Cluster Size'
  },
  above_horizon: {
    label: 'Above Horizon',
    format: (a: boolean): string => a ? 'Yes' : 'No'
  },
  scan_start_time_ssue_utc: {
    label: 'Scan Start Time',
    format: formatDate
  },
  polar_az_radians: {
    label: 'Polar AZ (rad)'
  },
  polar_el_radians: {
    label: 'Polar EL (rad)'
  },
  sensor_type: {
    label: 'Sensor'
  },
  band_type: {
    label: 'Band'
  }
};
