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

import projector from 'ecef-projector';
export default {
  /**
   * convert LLA in degrees and meters to ECEF in meters
   * @param lat_lon_alt three element array [lat, lon, alt]
   */
  project: (lat_lon_alt: number[]): number[] => {
    return projector.project(lat_lon_alt[0], lat_lon_alt[1], lat_lon_alt[2]);
  },
  
  /**
   * convert ECEF in meters to LLA in degrees and meters
   * @param xyz three element array [x, y, z]
   */
  unproject: (xyz: number[]): number[] => {
    return projector.unproject(xyz[0], xyz[1], xyz[2]);
  }
};
