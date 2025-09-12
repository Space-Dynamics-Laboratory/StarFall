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
 * Return an array of [x, y, z] coordinates in meters from lat, lon, alt in degrees and meters
 * @param lat latitude in degrees
 * @param lon longitude in degrees
 * @param alt altitude in meters
 */
export function project (lat: number, lon: number, alt: number): number[];

/**
 * Return an array of [lat, lon, alt] coordinates in degrees and meters from x, y, z in meters 
 * @param x x coordinate in meters
 * @param y y coordinate in meters
 * @param z z coordinate in meters
 */
export function unproject (x: number, y: number, z: number): number[];

