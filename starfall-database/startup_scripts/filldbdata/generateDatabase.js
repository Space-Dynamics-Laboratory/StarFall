#!/usr/bin/env node
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
const root_path = '../../../starfall-common/mock/';

require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { Client } = require('pg');
const { generateEvent } = require(path.resolve(__dirname, root_path, 'generateEvent'));
const { log, group, groupEnd } = require(path.resolve(__dirname, root_path, 'repeatLogger'));

let client = null;

const main = async () => {
  log('Generating data for database...')
  group();

  const data_path = path.resolve(root_path, 'events.json');
  const message_path = path.resolve(root_path, 'messages.json');

  log('Reading input files...');
  const data = JSON.parse(fs.readFileSync(data_path, 'utf-8'));
  const messages = JSON.parse(fs.readFileSync(message_path, 'utf-8'));
  log('Found', data.candidates.length, 'candidate events in', data_path);

  log('Connecting to database...');
  client = new Client({
    user: process.env.DB_USER || 'starfall_admin',
    host: process.env.DB_HOST || 'database',
    database: process.env.DB_DATABASE || 'starfall_database',
    password: process.env.DB_PASSWORD || 'password',
    port: process.env.DB_PORT || '5432'
  });

  await client.connect();
  log('Connected to database');

  const tables = [
    'history', 'tags', 'light_curves',
    'point_sources', 'sightings', 'events',
    'sensors', 'locations', 'platforms'
  ];

  log('Clearing database');
  group();
  let deletes = [];
  tables.forEach(table => {
    log(`Clearing ${table} table`)
    deletes.push(client.query(`DELETE FROM starfall_db_schema.${table};`)
      .then(() => { log(`Clearing ${table} table successful`) })
      .catch(e => { console.error(`Clearing ${table} table failed:`, e) })
    );
  });

  await Promise.allSettled(deletes);
  groupEnd();
  log('Finished clearing database');

  log('Inserting new data into database');
  group();

  // ************************************************
  // Perform one time setup
  // ************************************************

  log('Creating Platforms...');
  const platform_result = await client.query(
    `INSERT INTO starfall_db_schema.platforms (name, series, flight_number) VALUES
    ('GOES-16', 'GOES', 16),
    ('GOES-17', 'GOES', 17),
    ('GOES-18', 'GOES', 18),
    ('GOES-19', 'GOES', 19)
    RETURNING *;`);
  log('Platform insert successful');

  log('Creating Sensors...');
  const sensor_result = await client.query(
    `INSERT INTO starfall_db_schema.sensors (platform_id, name, type, fov) VALUES
    ($1, 'GLM', '42', 10.6),
    ($2, 'GLM', '42', 10.6),
    ($3, 'GLM', '42', 10.6),
    ($4, 'GLM', '42', 10.6)
    RETURNING *;`,
    platform_result.rows.map(x => x.platform_id)
  );
  log('Sensor insert successful');

  // ************************************************
  // Perform insertions for each event
  // ************************************************
  let msg = 0;
  let i = 0;
  const N_PROCESSING_STATES = 11;
  for (const event of data.candidates) {
    log('Event', i+1, 'of', data.candidates.length);
    const processing_state = (N_PROCESSING_STATES - 1) - (msg % N_PROCESSING_STATES);
    const has_velocity = msg % 2 === 0;
    const make_lc = msg % 3 === 0;

    event.meas = event.meas.slice(0, 10)
    await generateEvent({
      client,
      event,
      message: messages.messages[msg],
      processing_state,
      has_velocity,
      make_lc,
      sensors: sensor_result.rows,
    });
    msg = (msg + 1) % messages.messages.length;
    i += 1;
  }

  groupEnd();
  log('Finished inserting new data');

  log('Disconnecting from database...');
  client.end()
  .then(() => { log('Disconnected'); })
  .then(() => {
    groupEnd();
    log('Finished\n');
  })
}

main()
.catch (e => {
  log('  --  ERROR -- ', e) 
  if (client) {
    log('Disconnecting from database...');
    client.end().then(() => {
      log('Disconnected');
      groupEnd();
      log('Finished\n');
    })
  } else {
    groupEnd();
    log('Finished\n');
  }
})