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

import { PointSourceFilter } from 'starfall-common/dist/Types/PointSourceFilter';
import ecef from 'starfall-common/dist/ecef';
import log from '../log';

export const makePointSourceFilterQuery = (filter: PointSourceFilter): [string, (string|number)[]] => {
  let query = `
    select tag, ps.point_source_id, time, intensity, cluster_size, meas_near_point_ecef_m, meas_far_point_ecef_m, above_horizon, sensor_id
    from starfall_db_schema.point_sources ps
    inner join starfall_db_schema.sightings s on s.sighting_id = ps.sighting_id
    inner join starfall_db_schema.tags on tags.point_source_id = ps.point_source_id
    where ps.sighting_id = $1`;
  const args: (string|number)[] = [];


  if (filter.clusterSize.enabled) {
    query += ` and cluster_size >= $${args.length + 2} `;
    args.push(filter.clusterSize.extents[0]);
    query += ` and cluster_size <= $${args.length + 2} `;
    args.push(filter.clusterSize.extents[1]);
  }

  if (filter.horizon.enabled) {
    if (filter.horizon.above && !filter.horizon.below) query += ' and above_horizon = true ';
    else if (!filter.horizon.above && filter.horizon.below) query += ' and above_horizon = false ';
    /* else if (!filter.horizon.above && !filter.horizon.below) /* do nothing */
    /* else if (filter.horizon.above && filter.horizon.below) /* do nothing */
  }

  if (filter.intensity.enabled) {
    query += ` and intensity >= $${args.length + 2} `;
    args.push(filter.intensity.extents[0]);
    query += ` and intensity <= $${args.length + 2} `;
    args.push(filter.intensity.extents[1]);
  }
      
  if (filter.time.enabled) {
    query += ` and time >= $${args.length + 2} `;
    args.push(filter.time.extents[0]);
    query += ` and time <= $${args.length + 2} `;
    args.push(filter.time.extents[1]);
  }
      
  if (filter.geo.enabled) {
    if (filter.geo.lat === undefined || filter.geo.lon === undefined || filter.geo.alt === undefined) {
      log.warn('geo filter missing lat, lon or alt');
    } else if (typeof filter.geo.lat !== 'number' || typeof filter.geo.lon !== 'number' || typeof filter.geo.alt !== 'number' || typeof filter.geo.radius !== 'number') {
      log.warn('lat, lon, alt, or radius are not numbers');
    }
    else {
      const [x,y,z] = ecef.project([filter.geo.lat, filter.geo.lon, filter.geo.alt]);
      query += ` and ST_3DDWithin(los_points_geom, ST_GeomFromEWKT('SRID=4978;POINT(${x} ${y} ${z})'),${filter.geo.radius})`;
    }
  }
      
  if (filter.tags.enabled && filter.tags.tags.length > 0) {
    query += ` and tag in (${filter.tags.tags.map((_, i) => `$${args.length + 2 + i}`).join(',')}) `;
    args.push(...filter.tags.tags);
  }
      
  query += ' order by time';

  return [query, args];
};