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

/* eslint @typescript-eslint/no-var-requires: "off" */
const ecef = require('ecef-projector');
const { generateLightCurves } = require('./generateLightCurves');
const { generatePointSource } = require('./generatePointSource');
const { log } = require('./repeatLogger');
const { v4: uuidv4 } = require('uuid');
const randomInt = (min, max) => Math.floor(Math.random() * (max - min)) + Math.floor(min);

/**
 * 
 * @param {pg.Client} client pg postgres client connected to a database
 * @param {*} event event details
 * @param {*} message mock event history messages
 * @param {number} processing_state event processing state
 * @param {boolean} has_velocity if true will generate mock velocity
 * @param {boolean} make_lc if true will generate light curves for event
 * @param {zmq.Socket} sock zeromq socket, if provieded will emit NEW and FINISHED messages
 * @returns 
 */
async function generateEvent({client, event, message, processing_state, has_velocity, make_lc, sensors, update_to_user_analysis = false}) {
  event.meas.sort((a, b) => a.timeSsue - b.timeSsue);
  const peak = event.meas.reduce((max, cur) => (cur.energy > max.energy) ? cur : max, event.meas[0]);
  
  // Read and create event data
  const start_time_ssue = event.meas[0].timeSsue;
  const end_time_ssue = event.meas[event.meas.length-1].timeSsue;
  const event_time_ssue = peak.timeSsue;
  const current_time_ssue = Date.now() / 1000;
  const event_id = uuidv4();
  const user_viewed = false;
  const altitude_m = randomInt(14000, 74000);
  const total_energy_j = make_lc ? randomInt(2e10, 3.75e14) : null;
  const vel_x_m_s = has_velocity ? randomInt(-35000, 28000) : null;
  const vel_y_m_s = has_velocity ? randomInt(-44000, 31000) : null;
  const vel_z_m_s = has_velocity ? randomInt(-31000, 27000) : null;
  const location_ecef_m = (processing_state >= 4 && processing_state <= 8) ? ecef.project(peak.lat, peak.lon, altitude_m) : null;
  const location_str = (processing_state >= 4 && processing_state <= 8) ? `{${location_ecef_m[0]}, ${location_ecef_m[1]}, ${location_ecef_m[2]}}` : null;
  const velocity_m_s = [vel_x_m_s, vel_y_m_s, vel_z_m_s];
  const velocity_str = `{${velocity_m_s[0]}, ${velocity_m_s[1]}, ${velocity_m_s[2]}}`;
 
  // Insert event
  log('Inserting event', event_id);
  await client.query(`
    INSERT INTO starfall_db_schema.events (event_id, parent_id, approx_trigger_time, created_time, last_update_time, processing_state, user_viewed, approx_energy_j, location_ecef_m, velocity_ecef_m_sec)
    VALUES ($1, DEFAULT, $2, $3, $4, $5, $6, $7, $8, $9);`,
  [event_id, event_time_ssue, current_time_ssue, current_time_ssue, processing_state, user_viewed, total_energy_j, location_str, velocity_str]);
    
  if (processing_state === 0) return; // new event has no sightings

  // Pick sighting satellite
  const sat16 = 0;
  const sat16_sensor_pos = ecef.project(0, -57.2, 35780200);
  const sat16_sensor_pos_str = `{${sat16_sensor_pos[0]}, ${sat16_sensor_pos[1]}, ${sat16_sensor_pos[2]}}`;

  const sat17 = 1;
  const sat17_sensor_pos = ecef.project(0, -137.2, 35783800);
  const sat17_sensor_pos_str = `{${sat17_sensor_pos[0]}, ${sat17_sensor_pos[1]}, ${sat17_sensor_pos[2]}}`;

  const platforms = [
    {
      platform_id: sensors[0].platform_id,
      glm_sensor_id: sensors[0].sensor_id,
      lc_sensor_id: sensors[0].sensor_id,
      glm_sighting_uuid: uuidv4(),
      lc_sighting_uuid: uuidv4(),
      location_uuid: uuidv4(),
      sensor_pos: sat16_sensor_pos,
      sensor_pos_str: sat16_sensor_pos_str,
      saw_event: false,
      make_lc: true
    },{
      platform_id: sensors[1].platform_id,
      glm_sensor_id: sensors[1].sensor_id,
      lc_sensor_id: sensors[1].sensor_id,
      glm_sighting_uuid: uuidv4(),
      lc_sighting_uuid: uuidv4(),
      location_uuid: uuidv4(),
      sensor_pos: sat17_sensor_pos,
      sensor_pos_str: sat17_sensor_pos_str,
      saw_event: false,
      make_lc: false
    }
  ];

  if (peak.lon > -120) { // seen by GEOS East (16)
    platforms[sat16].saw_event = true;
    /*if (make_lc)*/ platforms[sat16].make_lc = true;
  }
  if (peak.lon < -70) { // seen by GOES West (17)
    platforms[sat17].saw_event = true;
    /*if (make_lc)*/ platforms[sat17].make_lc = true;
  }

  // create locations and sightings
  for (const platform of platforms) {
    if (!platform.saw_event) continue;

    log('Inserting location'); 
    await client.query(`
      INSERT INTO starfall_db_schema.locations (location_id, platform_id, pos_ecef_m)
      VALUES ($1, $2, $3);`,
    [platform.location_uuid, platform.platform_id, platform.sensor_pos_str]);

    log('Inserting sighting');
    await client.query(`
      INSERT INTO starfall_db_schema.sightings (sighting_id, event_id, sensor_id, location_id)
      VALUES ($1, $2, $3, $4);`,
    [platform.glm_sighting_uuid, event_id, platform.glm_sensor_id, platform.location_uuid]);

    // Insert Light Curves
    if (platform.make_lc) {
      const lightCurve = generateLightCurves(peak.timeSsue, end_time_ssue-start_time_ssue, randomInt(-10, 10));  

      try {
        const data = Buffer.from(lightCurve.serializeBinary()).toString('hex');

        log('Inserting sighting'); 
        await client.query(`
          INSERT INTO starfall_db_schema.sightings (sighting_id, event_id, sensor_id, location_id)
          VALUES ($1, $2, $3, $4);`,
        [platform.lc_sighting_uuid, event_id, platform.lc_sensor_id, null]);

        log('Light Curve insert successful'); 
        await client.query(`
          INSERT INTO starfall_db_schema.light_curves (light_curve_id, sighting_id, data)
          VALUES ($1, $2, $3);`,
        [uuidv4(), platform.lc_sighting_uuid, data]
        );

      } catch (err) {
        log('  --  FAILED  --  serialize light curve\n', err);
      }
    }
  }

  // Insert GLM Point Sources
  let p = 0;
  for (const ps of event.meas) {
    const time_ssue = ps.timeSsue + p; // the timing is very close, < 1s, between points. +p adds an extra second
    const point = ecef.project(ps.lat, ps.lon, altitude_m);

    let i = 0;
    for (const platform of platforms) {
      if (!platform.saw_event) continue;

      const { near_str, far_str } = generatePointSource(point, altitude_m, platform);

      const cluster_size = randomInt(1, 100);
      const point_source_id = uuidv4();

      // Point Source
      log('Inserting GLMSource and Tagging'); 
      await client.query(`
        INSERT INTO starfall_db_schema.point_sources (point_source_id, time, intensity, sighting_id, above_horizon, sensor_pos_ecef_m, meas_near_point_ecef_m, meas_far_point_ecef_m, cluster_size)
        VALUES ($1, $2, $3, $4, FALSE, $5, $6, $7, $8);`,
      [point_source_id, time_ssue, ps.energy + i * 10e-14, platform.glm_sighting_uuid, platform.sensor_pos_str, near_str, far_str, cluster_size]);
      
      if (p < 5) await client.query(`
        INSERT INTO starfall_db_schema.point_source_accessory (point_source_id, scan_start_time_ssue_utc, polar_az_radians, polar_el_radians, field_1, field_2, field_3, field_4, field_5, sensor_type)
        VALUES ($1, 123456789, 10, 10, 1, 2, 3, 4, 5, 0);`,
      [point_source_id]);

      let tag_text = 'Accepted';
      if (randomInt(0, 100) <= 15) tag_text = 'Candidate';

      // Tag
      await client.query(`
        INSERT INTO starfall_db_schema.tags (event_id, point_source_id, tag)
        VALUES ($1, $2, $3);`,
      [event_id, point_source_id, tag_text]);
      await client.query(`
        INSERT INTO starfall_db_schema.tags (event_id, point_source_id, tag)
        VALUES ($1, $2, $3);`,
      [event_id, point_source_id, 'tag0']);
      if (randomInt(0, 100) <= 50) await client.query(`
        INSERT INTO starfall_db_schema.tags (event_id, point_source_id, tag)
        VALUES ($1, $2, $3);`,
      [event_id, point_source_id, 'tag1']);
      if (randomInt(0, 100) <= 50) await client.query(`
        INSERT INTO starfall_db_schema.tags (event_id, point_source_id, tag)
        VALUES ($1, $2, $3);`,
      [event_id, point_source_id, 'tag2']);
      if (randomInt(0, 100) <= 50) await client.query(`
        INSERT INTO starfall_db_schema.tags (event_id, point_source_id, tag)
        VALUES ($1, $2, $3);`,
      [event_id, point_source_id, 'tag3']);
      ++i;
    }
    ++p;
  }

  // Insert history
  for (let i = 0; i < message.length; ++i) {
    let current_time_ssue = Date.now()/1000;
    log('Inserting history');
    await client.query(`
      INSERT INTO starfall_db_schema.history (history_id, time, entry, author, event_id)
      VALUES (gen_random_uuid(), $1, $2, $3, $4);`,
    [current_time_ssue, message[i], `Service ${i % 2}`, event_id]
    );
  }

  if (update_to_user_analysis) { // mock event emitter
    setTimeout(async () => {
      await client.query(`
        UPDATE starfall_db_schema.events
        SET processing_state = 5
        WHERE event_id = $1;`,
      [event_id]);
      log(`Updated processing state from ${processing_state} to ${5}`);
    }, 2000);
  }
}

module.exports = { generateEvent };
