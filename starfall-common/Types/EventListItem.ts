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

export type EventListItem = {
  event_id: string;
  parent_id: string | null;
  approx_trigger_time: number;
  created_time: number;
  last_update_time: number;
  processing_state: number;
  user_viewed: boolean;
  location_ecef_m: number[] | null;
  location_lat_lon_alt_m: number[] | null;
  velocity_ecef_m_sec: number[] | null;
  approx_energy_j: number | null;
};
