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
 * Custom logging function which avoids printing repeated messages
 * @param  {...any} args list of things that can be cast to string
 */
const customLog = (...args) => {
  const msg = args.join(' ');
  if (this.msg === msg) {
    process.stdout.cursorTo(0);
    process.stdout.write(`${'  '.repeat(this.groupCount)}(${++this.msgCount}) ${msg}`);
  } else {
    process.stdout.write(`\n${'  '.repeat(this.groupCount)}${msg}`);
    this.msg = msg;
    this.msgCount = 1;
  }
};

// Fall back to default if cursorTo is undefined (is not defined during docker contianer building)
const log = (process.stdout.cursorTo) ? customLog : console.log;
const group = (process.stdout.cursorTo) ? () => ++this.groupCount : console.group;
const groupEnd = (process.stdout.cursorTo) ? () => --this.groupCount : console.groupEnd;
if (process.stdout.cursorTo) this.groupCount = 0;

module.exports = { log, group, groupEnd };