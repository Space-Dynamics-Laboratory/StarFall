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
const root_path = '../starfall-common/mock/'

require('dotenv').config();
const fs = require('fs');
const path = require('path');
const zmq = require('zeromq')
const { Client } = require('pg')
const { generateEvent } = require(path.resolve(__dirname, root_path, 'generateEvent'));
const readline = require('readline').createInterface({
  input: process.stdin,
  output: process.stdout
});

const sock = new zmq.Publisher;
const dbClient = new Client({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_DATABASE,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT
});

/**
 * displays a message to the user and returns the input
 * @param {string} msg message to display to console
 * @returns string input by user
 */
function input(msg) {
  return new Promise(resolve => readline.question(msg, ans => {
    resolve(ans);
  }))
}

async function exit() {
  console.log('\nShutting down...');
  await dbClient.end();
  process.exit(0)
}

async function run() {
  const data_path = path.resolve(root_path + 'events.json')
  const message_path = path.resolve(root_path + 'messages.json')

  console.log('Reading input files...')
  const data = JSON.parse(fs.readFileSync(data_path, 'utf-8'))
  const messages = JSON.parse(fs.readFileSync(message_path, 'utf-8'))
  console.log('Found', data.candidates.length, 'candidate events in', data_path);

  const sensor_result = await dbClient.query('SELECT * FROM starfall_db_schema.sensors ORDER BY sensor_id ASC;')

  let msg = 0;
  let i = 0;
  console.log('Enter q to quit')
  while (await input(`Press enter to send message: ${i} `) !== 'q') {
    const event = data.candidates[i]
    const processing_state = 2; // processing
    const has_velocity = msg % 2 === 0
    const make_lc = msg % 3 === 0

    await generateEvent({
      client: dbClient,
      event,
      message: messages.messages[msg],
      processing_state,
      has_velocity,
      make_lc,
      sensors: sensor_result.rows,
      update_to_user_analysis: true
    });

    i = (i + 1) % data.candidates.length;
    msg = (msg + 1) % messages.messages.length;
  }
}

//   MAIN
// --------
(async () => {
  await sock.bind("tcp://127.0.0.1:1236");
  console.log("Publisher bound to port 1236");

  await dbClient.connect()
  console.log("Database client connected");

  const sensors = await dbClient.query('select sensor_id, name from starfall_db_schema.sensors')
  sat16_id = sensors.rows[0].sensor_id
  sat17_id = sensors.rows[1].sensor_id

  process.once('SIGINT', async function (code) {
    exit();
  });

  await run();
  await exit();
})().catch(e => {
  console.log('  -- ERROR -- ', e);
  exit();
});