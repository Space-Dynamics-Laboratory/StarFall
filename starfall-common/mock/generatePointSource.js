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

/**
 * calculate the near and far points for a pointsource
 * @param { number[3] } point ecef location of pointsource
 * @param { number } altitude_m altitude of point source
 * @param { Platform } platform platform of sensor that produced the point source
 * @returns near and far points of the point source
 */
function generatePointSource(point, altitude_m, platform) {
  const sat_vec = [
    point[0] - platform.sensor_pos[0],
    point[1] - platform.sensor_pos[1],
    point[2] - platform.sensor_pos[2]
  ];
  const sat_vec_mag = Math.sqrt(
    sat_vec[0] * sat_vec[0] +
        sat_vec[1] * sat_vec[1] +
        sat_vec[2] * sat_vec[2]
  );
  const sat_unit_vec = [
    sat_vec[0] / sat_vec_mag,
    sat_vec[1] / sat_vec_mag,
    sat_vec[2] / sat_vec_mag
  ];
  const near = [
    point[0] - sat_unit_vec[0] * altitude_m,
    point[1] - sat_unit_vec[1] * altitude_m,
    point[2] - sat_unit_vec[2] * altitude_m
  ];
  const far = [
    point[0] + sat_unit_vec[0] * (100000 - altitude_m),
    point[1] + sat_unit_vec[1] * (100000 - altitude_m),
    point[2] + sat_unit_vec[2] * (100000 - altitude_m)
  ];

  return {
    near_str: `{${near[0]}, ${near[1]}, ${near[2]}}`,
    far_str: `{${far[0]}, ${far[1]}, ${far[2]}}`,
  }; 
}

module.exports = { generatePointSource };