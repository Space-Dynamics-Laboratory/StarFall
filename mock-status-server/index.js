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

const path = require('path');
// const proto_path = path.resolve(__dirname, '../starfall-common/proto/Status');
// const { StatusInformation } = require(path.resolve(proto_path, 'StatusReply_pb'));
// const { StatusRequest } = require(path.resolve(proto_path, 'StatusRequest_pb'));
const { StatusInformation, StatusKey, StatusItem } = require('../starfall-common/proto/Status/StatusReply_pb');
const { StatusRequest } = require('../starfall-common/proto/Status/StatusRequest_pb');

const zmq = require('zeromq');
const readline = require('readline').createInterface({
  input: process.stdin,
  output: process.stdout
});

const sock = new zmq.Reply;

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
  sock.disconnect();
  process.exit(0)
}

const makeStatusItem = (time, status, error) => {
  const statusItem = new StatusItem;
  statusItem.setTimestamp(time)
  statusItem.setStatus(status);
  statusItem.setErrorFlag(error);
  return statusItem;
}

const makeStatusKey = (main, sub, statusArgs) => {
  const statusKey = new StatusKey;
  statusKey.setMainKey(main);
  statusKey.setSubKey(sub);
  for (const args of statusArgs) {
    statusKey.addStatus(
      makeStatusItem(...args)
    );
  }
  return statusKey;
}

const statusHistory = [];
const maxHistory = 100;

/**
 * Choose a random element of an array
 * @param {any[]} arr 
 * @returns a random element of the input array 
 */
const randomChoice = (arr) => arr[Math.floor(arr.length * Math.random())];

const _day = (d) => d.getUTCDate().toString().padStart(2, '0');
const _month = (d) => (d.getUTCMonth() + 1).toString().padStart(2, '0');
const _year = (d) => d.getUTCFullYear().toString();
const _hours = (d) => d.getUTCHours().toString().padStart(2, '0');
const _minutes = (d) => d.getUTCMinutes().toString().padStart(2, '0');
const _seconds = (d) => d.getUTCSeconds().toString().padStart(2, '0');
const _doy = (d) => `${(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()) - Date.UTC(d.getUTCFullYear(), 0, 0)) / 24 / 60 / 60 / 1000}`;

/**
 * Format a date into a timestamp string
 * @param {Date} d date
 * @returns string with timestamp in the form 'MM/DD/YYYY HH:mm:ss'
 */
const timestamp = (d) => `${_year(d)}-${_month(d)}-${_day(d)} ${_doy(d)} ${_hours(d)}:${_minutes(d)}:${_seconds(d)}`;

const addStatusHistory = () => {
  const main = randomChoice(['A', 'B', 'C']);
  const sub = randomChoice(['a', 'b', 'c']);
  const [status, error] = randomChoice([['good', false], ['ok', false], ['not bad', false], ['bad', true]]);
  const time = timestamp(new Date((new Date()).getTime()));
  const record = makeStatusKey(main, sub, [[time, status, error]]);
  statusHistory.push(record)
  
  const level = randomChoice (['debug', 'debug', 'debug', 'debug', 'info', 'info', 'info', 'warning', 'warning', 'error'])
  const log = makeStatusKey(main, 'Recent Logs', [[time, `${time}: ${randomChoice([`(${level})`, ''])} ${main} - ${sub} : ${status}`, false]])
  statusHistory.push(log)

  if (statusHistory.length > maxHistory) {
    statusHistory.shift();
    statusHistory.shift();
  }
}

//   MAIN
// --------
(async () => {
  const args = process.argv.slice(2);
  let a = 0
  let port = 6666;
  while ( a < args.length ) {
    switch (args[a]) {
      case '-p':
      case '--port':
        ++a;
        port = Number(args[a]);
        break;
    }
    ++a;
  }
  
  setInterval(addStatusHistory, 4000);

  await sock.bind(`tcp://127.0.0.1:${port}`);
  console.log(`Socket bound to port ${port}`);

  for await (const [msg] of sock) {
    const request = StatusRequest.deserializeBinary(msg)
    const n = 20;
    const reply = new StatusInformation;

    for (let i = Math.max(0, statusHistory.length - n); i < statusHistory.length; ++i) {
      reply.addRecord(statusHistory[i])
    }

    await sock.send(reply.serializeBinary());
    console.log('sent')
  }

  process.once('SIGINT', async function (code) {
    exit();
  });

  await exit();
})().catch(e => {
  console.log('  -- ERROR --\n', e);
  exit();
});